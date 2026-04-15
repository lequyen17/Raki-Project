import React, { useEffect, useState } from 'react';
import { useNavigate, useParams } from 'react-router-dom';
import api from '../api/api';

const Cards = () => {
  const navigate = useNavigate();
  const { deckId } = useParams();
  const [deckName, setDeckName] = useState('');
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState('');

  useEffect(() => {
    const token = localStorage.getItem('access_token');
    if (!token) {
      navigate('/login');
      return;
    }

    const fetchCards = async () => {
      try {
        setLoading(true);
        setError('');
        const res = await api.get(`/api/user/decks/${deckId}/cards/`);
        setDeckName(res.data?.deck_name || '');
        setCards(res.data?.results || []);
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem('access_token');
          navigate('/login');
          return;
        }
        setError(err.response?.data?.error || 'Khong the tai danh sach card.');
      } finally {
        setLoading(false);
      }
    };

    fetchCards();
  }, [deckId, navigate]);

  return (
    <div className="decks-page">
      <div className="decks-container">
        <div className="deck-detail-actions" style={{ marginBottom: '16px' }}>
          <button type="button" className="deck-action-btn" onClick={() => navigate('/decks')}>
            Back To Decks
          </button>
        </div>

        <h1 className="decks-title">Cards In Deck {deckName ? `- ${deckName}` : ''}</h1>

        {loading && <p className="decks-state">Dang tai danh sach card...</p>}
        {error && <p className="decks-error">{error}</p>}

        {!loading && !error && (
          <>
            {cards.length === 0 ? (
              <p className="decks-state">Deck nay chua co card nao.</p>
            ) : (
              <div className="deck-tree-list">
                {cards.map((card) => (
                  <div key={card.id} className="deck-tree-node">
                    <div className="deck-tree-row deck-tree-row--root">
                      <div className="deck-row-main">
                        <span className="deck-row-name">Card #{card.id}</span>
                        <span className="deck-row-count">
                          rep {card.repetition} | int {card.interval} | ease {card.easiness}
                        </span>
                        <span className="deck-row-count">
                          next review: {card.next_review ? new Date(card.next_review).toLocaleString() : 'N/A'}
                        </span>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </>
        )}
      </div>
    </div>
  );
};

export default Cards;
