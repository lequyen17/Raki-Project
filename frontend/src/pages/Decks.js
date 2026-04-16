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
  

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDeck, setNewDeck] = useState({ name: '', description: '' });
  const [createError, setCreateError] = useState('');

  const [expandedIds, setExpandedIds] = useState(() => new Set());
  const [draggingDeckId, setDraggingDeckId] = useState(null);
  const [dropTargetId, setDropTargetId] = useState(null);
  const [moveError, setMoveError] = useState('');
  const [selectedDeckId, setSelectedDeckId] = useState(null);
  const [selectedDeckInfo, setSelectedDeckInfo] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState('');
  const [showEditModal, setShowEditModal] = useState(false);
  const [editDeck, setEditDeck] = useState({ name: '', description: '' });
  const [editError, setEditError] = useState('');
  const [isEditing, setIsEditing] = useState(false);
  const [deletingDeck, setDeletingDeck] = useState(false);

  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

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
  }, []);

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

  const handleOpenEditModal = () => {
    if (!selectedDeckId) {
      return;
    }
    const deckInList = decks.find((deck) => deck.id === selectedDeckId);
    setEditDeck({
      name: selectedDeckInfo?.name || deckInList?.name || '',
      description: selectedDeckInfo?.description || deckInList?.description || '',
    });
    setEditError('');
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    if (isEditing) {
      return;
    }
    setShowEditModal(false);
    setEditError('');
  };

  const handleEditDeck = async (e) => {
    e.preventDefault();
    if (!selectedDeckId) {
      setEditError('Khong co deck de chinh sua.');
      return;
    }

    const payload = {
      name: editDeck.name.trim(),
      description: editDeck.description.trim(),
    };

    if (!payload.name) {
      setEditError('Deck name is required.');
      return;
    }

    try {
      setIsEditing(true);
      setEditError('');
      const res = await api.put(`/api/user/decks/${selectedDeckId}/`, payload);
      const updatedDeck = res.data;

      setDecks((prev) =>
        prev.map((deck) =>
          deck.id === selectedDeckId
            ? {
                ...deck,
                name: updatedDeck?.name ?? payload.name,
                description: updatedDeck?.description ?? payload.description,
              }
            : deck
        )
      );

      setSelectedDeckInfo((prev) =>
        prev
          ? {
              ...prev,
              name: updatedDeck?.name ?? payload.name,
              description: updatedDeck?.description ?? payload.description,
            }
          : prev
      );
      setShowEditModal(false);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem('access_token');
        navigate('/login');
        return;
      }
      setEditError(err.response?.data?.error || 'Cap nhat deck that bai.');
    } finally {
      setIsEditing(false);
    }
  };

  const handleDragStart = (e, deckId) => {
    e.dataTransfer.effectAllowed = 'move';
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

  const handleDropToRoot = async () => {
    if (!draggingDeckId) {
      return;
    }

    try {
      setMoveError('');
      await api.post('/api/user/decks/move/', {
        deck_id: draggingDeckId,
        parent_id: null,
      });

      setDecks((prev) =>
        prev.map((deck) =>
          deck.id === draggingDeckId ? { ...deck, parent_id: null } : deck
        )
      );
    } catch (err) {
      setMoveError(err.response?.data?.error || 'Di chuyen deck that bai.');
    } finally {
      setDraggingDeckId(null);
      setDropTargetId(null);
    }
  };

  const isInsideDeckRow = (target) => {
    return Boolean(target?.closest && target.closest('.deck-tree-row'));
  };

  const handleSelectDeck = async (deckId) => {
    setStatsError('');
    setStatsLoading(true);
    try {
      const res = await api.get(`/api/user/decks/${deckId}/`);
      setSelectedDeckId(deckId);
      setSelectedDeckInfo(res.data);
    } catch (err) {
      setSelectedDeckId(null);
      setSelectedDeckInfo(null);
      setStatsError(err.response?.data?.error || 'Khong the tai thong ke deck.');
    } finally {
      setStatsLoading(false);
    }
  };

const renderNode = (node, depth) => {
  const currentDepth = depth ?? 0; // nếu depth undefined thì = 0

  const hasChildren = node.children.length > 0;
  const isExpanded = expandedIds.has(node.id);

  return (
    <div key={node.id} className="deck-tree-node">
      <div
        className={`deck-tree-row ${
          currentDepth === 0 ? 'deck-tree-row--root' : 'deck-tree-row--child'
        } ${dropTargetId === node.id ? 'deck-tree-row--drop' : ''}`}
        style={{ marginLeft: `${currentDepth * 24}px` }}
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
          e.stopPropagation();
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
          <button
            type="button"
            className={`deck-row-name ${
              selectedDeckId === node.id ? 'deck-row-name--selected' : ''
            }`}
            onClick={() => handleSelectDeck(node.id)}
          >
            {node.name}
          </button>

          <span className="deck-row-count">
            {node.total_cards || 0} cards
          </span>

          <button
            type="button"
            className="deck-view-btn"
            onClick={() => handleSelectDeck(node.id)}
          >
            View
          </button>
        </div>
      </div>

      {hasChildren &&
        isExpanded &&
        node.children.map((child) =>
          renderNode(child, currentDepth + 1)
        )}
    </div>
  );
};

  return (
    <div
      className="decks-page"
      onDragOver={(e) => {
        if (!draggingDeckId) {
          return;
        }
        if (!isInsideDeckRow(e.target)) {
          e.preventDefault();
          e.dataTransfer.dropEffect = 'move';
          setDropTargetId('root');
        }
      }}
      onDrop={(e) => {
        if (!draggingDeckId) {
          return;
        }
        if (!isInsideDeckRow(e.target)) {
          e.preventDefault();
          handleDropToRoot();
        }
      }}
    >
      <div className="decks-layout">
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
      <div className="deck-detail-panel">
        <h2 className="deck-detail-title">Deck Statistic</h2>
        {!selectedDeckId && <p className="decks-state">Chon 1 deck de xem thong ke.</p>}
        {statsError && <p className="decks-error">{statsError}</p>}
        {statsLoading && <p className="decks-state">Dang tai thong ke...</p>}

        {selectedDeckInfo && !statsLoading && (
          <>
            <p className="deck-detail-name">{selectedDeckInfo.name}</p>
            <p className="decks-state">
              {selectedDeckInfo.description?.trim() || ' '}
            </p>
            <div className="deck-stat-grid">
              <div className="deck-stat-card">
                <span className="deck-stat-label">New</span>
                <strong>{selectedDeckInfo.stats.new}</strong>
              </div>
              <div className="deck-stat-card">
                <span className="deck-stat-label">Learn</span>
                <strong>{selectedDeckInfo.stats.learn}</strong>
              </div>
              <div className="deck-stat-card">
                <span className="deck-stat-label">Review</span>
                <strong>{selectedDeckInfo.stats.review}</strong>
              </div>
            </div>

            <div className="deck-detail-actions">
              <button
                type="button"
                className="deck-action-btn"
                onClick={handleOpenEditModal}
              >
                Edit Deck
              </button>
              <button
                type="button"
                className="deck-action-btn deck-action-btn--danger"
                disabled={deletingDeck}
                onClick={async () => {
                  if (!window.confirm('Ban chac chan muon xoa deck nay?')) {
                    return;
                  }
                  try {
                    setDeletingDeck(true);
                    await api.delete(`/api/user/decks/${selectedDeckId}/`);
                    const res = await api.get('/api/user/decks/');
                    setDecks(res.data?.results || []);
                    setSelectedDeckId(null);
                    setSelectedDeckInfo(null);
                    setStatsError('');
                  } catch (err) {
                    setStatsError(err.response?.data?.error || 'Xoa deck that bai.');
                  } finally {
                    setDeletingDeck(false);
                  }
                }}
              >
                {deletingDeck ? 'Deleting...' : 'Delete Deck'}
              </button>
              <button
                type="button"
                className="deck-action-btn deck-action-btn--primary"
                onClick={() => navigate(`/decks/${selectedDeckId}/cards`)}
              >
                View Card
              </button>
            </div>
          </>
        )}
      </div>
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
      {showEditModal && (
        <div className="deck-modal-overlay" onClick={handleCloseEditModal}>
          <div className="deck-modal" onClick={(e) => e.stopPropagation()}>
            <h2 className="deck-modal-title">Edit Deck</h2>
            <form onSubmit={handleEditDeck}>
              <label className="deck-modal-label" htmlFor="edit-deck-name">
                Deck name
              </label>
              <input
                id="edit-deck-name"
                type="text"
                className="deck-modal-input"
                value={editDeck.name}
                maxLength={100}
                onChange={(e) => setEditDeck((prev) => ({ ...prev, name: e.target.value }))}
                required
              />

              <label className="deck-modal-label" htmlFor="edit-deck-description">
                Description
              </label>
              <textarea
                id="edit-deck-description"
                className="deck-modal-textarea"
                rows={4}
                value={editDeck.description}
                onChange={(e) => setEditDeck((prev) => ({ ...prev, description: e.target.value }))}
              />

              {editError && <p className="deck-modal-error">{editError}</p>}

              <div className="deck-modal-actions">
                <button
                  type="button"
                  className="deck-modal-btn deck-modal-btn--cancel"
                  onClick={handleCloseEditModal}
                  disabled={isEditing}
                >
                  Cancel
                </button>
                <button
                  type="submit"
                  className="deck-modal-btn deck-modal-btn--submit"
                  disabled={isEditing}
                >
                  {isEditing ? 'Saving...' : 'Save Changes'}
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
