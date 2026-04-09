import React, { useEffect, useMemo, useState } from 'react';
import { useNavigate } from 'react-router-dom';
import api from '../api/api';

const buildDeckTree = (items) => {
  const byId = new Map();
  const roots = [];

  items.forEach((item) => byId.set(item.id, { ...item, children: [] }));
  items.forEach((item) => {
    const node = byId.get(item.id);
    if (item.parent_id && byId.has(item.parent_id)) {
      byId.get(item.parent_id).children.push(node);
    } else {
      roots.push(node);
    }
  });

  return roots;
};

const Decks = () => {
  const navigate = useNavigate();
  const [decks, setDecks] = useState([]);
  const [searchText, setSearchText] = useState('');
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDeck, setNewDeck] = useState({ name: '', description: '' });
  const [createError, setCreateError] = useState('');
  const [isCreating, setIsCreating] = useState(false);

  const [expandedIds, setExpandedIds] = useState(() => new Set());
  const [draggingDeckId, setDraggingDeckId] = useState(null);
  const [dropTargetId, setDropTargetId] = useState(null);
  const [moveError, setMoveError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchDecks = async () => {
      try {
        setLoading(true);
        setError('');
        const res = await api.get('/api/user/decks/');
        setDecks(res.data?.results || []);
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('access_token');
          navigate('/login');
          return;
        }
        setError('Khong the tai danh sach deck. Vui long thu lai.');
      } finally {
        setLoading(false);
      }
    };

    fetchDecks();
  }, [navigate]);

  const filteredDecks = useMemo(() => {
    const keyword = searchText.trim().toLowerCase();
    if (!keyword) {
      return decks;
    }

    return decks.filter((deck) => {
      const name = (deck.name || '').toLowerCase();
      const description = (deck.description || '').toLowerCase();
      return name.includes(keyword) || description.includes(keyword);
    });
  }, [decks, searchText]);

  const treeDecks = useMemo(() => buildDeckTree(filteredDecks), [filteredDecks]);

  const toggleExpanded = (deckId) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(deckId)) {
        next.delete(deckId);
      } else {
        next.add(deckId);
      }
      return next;
    });
  };

  const handleOpenCreateModal = () => {
    setCreateError('');
    setNewDeck({ name: '', description: '' });
    setShowCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    if (isCreating) {
      return;
    }
    setShowCreateModal(false);
    setCreateError('');
  };

  const handleCreateDeck = async (e) => {
    e.preventDefault();
    const payload = {
      name: newDeck.name.trim(),
      description: newDeck.description.trim(),
    };

    if (!payload.name) {
      setCreateError('Deck name is required.');
      return;
    }

    try {
      setIsCreating(true);
      setCreateError('');
      const res = await api.post('/api/user/decks/', payload);
      setDecks((prev) => [res.data, ...prev]);
      setShowCreateModal(false);
      setNewDeck({ name: '', description: '' });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
        return;
      }
      setCreateError(err.response?.data?.error || 'Cannot create deck. Please try again.');
    } finally {
      setIsCreating(false);
    }
  };

  const handleDragStart = (e, deckId) => {
    e.dataTransfer.effectAllowed = 'move';
    e.dataTransfer.setData('text/plain', String(deckId));
    setDraggingDeckId(deckId);
    setMoveError('');
  };

  const handleDragEnd = () => {
    setDraggingDeckId(null);
    setDropTargetId(null);
  };

  const handleDropOnDeck = async (targetDeckId) => {
    if (!draggingDeckId || draggingDeckId === targetDeckId) {
      setMoveError('Khong the drop vao chinh deck do.');
      return;
    }

    try {
      setMoveError('');
      await api.post('/api/user/decks/move/', {
        deck_id: draggingDeckId,
        parent_id: targetDeckId,
      });

      setDecks((prev) =>
        prev.map((deck) =>
          deck.id === draggingDeckId ? { ...deck, parent_id: targetDeckId } : deck
        )
      );
      setExpandedIds((prev) => new Set(prev).add(targetDeckId));
    } catch (err) {
      setMoveError(err.response?.data?.error || 'Di chuyen deck that bai.');
    } finally {
      setDraggingDeckId(null);
      setDropTargetId(null);
    }
  };

  const renderNode = (node, depth = 0) => {
    const hasChildren = node.children.length > 0;
    const isExpanded = expandedIds.has(node.id);

    return (
      <div key={node.id} className="deck-tree-node">
        <div
          className={`deck-tree-row ${depth === 0 ? 'deck-tree-row--root' : 'deck-tree-row--child'} ${dropTargetId === node.id ? 'deck-tree-row--drop' : ''}`}
          style={{ marginLeft: `${depth * 24}px` }}
          draggable
          onDragStart={(e) => handleDragStart(e, node.id)}
          onDragEnd={handleDragEnd}
          onDragOver={(e) => {
            e.preventDefault();
            e.dataTransfer.dropEffect = 'move';
            setDropTargetId(node.id);
          }}
          onDragLeave={() => setDropTargetId(null)}
          onDrop={(e) => {
            e.preventDefault();
            handleDropOnDeck(node.id);
          }}
        >
          <button
            type="button"
            className="deck-expand-btn"
            onClick={() => hasChildren && toggleExpanded(node.id)}
          >
            {hasChildren ? (isExpanded ? 'v' : '>') : '-'}
          </button>
          <div className="deck-drag-handle">::</div>
          <div className="deck-row-main">
            <span className="deck-row-name">{node.name}</span>
            <span className="deck-row-count">{node.total_cards || 0} cards</span>
          </div>
        </div>

        {hasChildren && isExpanded && node.children.map((child) => renderNode(child, depth + 1))}
      </div>
    );
  };

  return (
    <div className="decks-page">
      <div className="decks-container">
        <h1 className="decks-title">My Decks</h1>

        <div className="decks-toolbar">
          <input
            type="text"
            className="decks-search"
            placeholder="Search deck..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <button type="button" className="decks-add-btn" onClick={handleOpenCreateModal}>
            Add New Deck
          </button>
        </div>

        {loading && <p className="decks-state">Dang tai danh sach deck...</p>}
        {error && <p className="decks-error">{error}</p>}
        {moveError && <p className="decks-error">{moveError}</p>}

        {!loading && !error && (
          <>
            {treeDecks.length === 0 ? (
              <p className="decks-state">Khong tim thay deck phu hop.</p>
            ) : (
              <div className="deck-tree-list">{treeDecks.map((node) => renderNode(node))}</div>
            )}
          </>
        )}
      </div>

      {showCreateModal && (
        <div className="deck-modal-overlay" onClick={handleCloseCreateModal}>
          <div className="deck-modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="deck-modal-title">Add New Deck</h2>
            <form onSubmit={handleCreateDeck}>
              <label className="deck-modal-label" htmlFor="deck-name">
                Deck name
              </label>
              <input
                id="deck-name"
                type="text"
                className="deck-modal-input"
                value={newDeck.name}
                maxLength={100}
                onChange={(e) => setNewDeck((prev) => ({ ...prev, name: e.target.value }))}
                required
              />

              <label className="deck-modal-label" htmlFor="deck-description">
                Description
              </label>
              <textarea
                id="deck-description"
                className="deck-modal-textarea"
                rows={4}
                value={newDeck.description}
                onChange={(e) => setNewDeck((prev) => ({ ...prev, description: e.target.value }))}
              />

              {createError && <p className="deck-modal-error">{createError}</p>}

              <div className="deck-modal-actions">
                <button
                  type="button"
                  className="deck-modal-btn deck-modal-btn--cancel"
                  onClick={handleCloseCreateModal}
                  disabled={isCreating}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="deck-modal-btn deck-modal-btn--submit"
                  disabled={isCreating}
                >
                  {isCreating ? 'Creating...' : 'Create Deck'}
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};

export default Decks;
