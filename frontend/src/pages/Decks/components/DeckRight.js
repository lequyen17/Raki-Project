import React from "react";
import { useNavigate } from "react-router-dom";

const DeckRight = ({
  selectedDeckId,
  selectedDeckInfo,
  statsLoading,
  statsError,
  handleOpenEditModal,
  deletingDeck,
  handleDeleteDeck,
}) => {
  const navigate = useNavigate();

  return (
    <div className="deck-detail-panel">
      <h2 className="deck-detail-title">Deck Statistic</h2>
      {!selectedDeckId && (
        <p className="decks-state">Chon 1 deck de xem thong ke.</p>
      )}
      {statsError && <p className="decks-error">{statsError}</p>}
      {statsLoading && <p className="decks-state">Dang tai thong ke...</p>}

      {selectedDeckInfo && !statsLoading && (
        <>
          <p className="deck-detail-name">{selectedDeckInfo.name}</p>

          <div className="deck-stat-grid">
            <div className="deck-stat-card">
              <span className="deck-stat-label">New</span>
              <strong>{selectedDeckInfo.counts?.new || 0}</strong>
            </div>
            <div className="deck-stat-card">
              <span className="deck-stat-label">Learn</span>
              <strong>{selectedDeckInfo.counts?.learning || 0}</strong>
            </div>
            <div className="deck-stat-card">
              <span className="deck-stat-label">Review</span>
              <strong>{selectedDeckInfo.counts?.review || 0}</strong>
            </div>
          </div>

          <div className="deck-detail-actions">
            <button
              type="button"
              className="deck-action-btn deck-action-btn--primary"
              style={{
                backgroundColor: "#212121",
                color: "#fff",
                fontWeight: "bold",
              }}
              onClick={() => navigate(`/decks/${selectedDeckId}/study`)}
            >
              Study Now
            </button>

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
              onClick={handleDeleteDeck}
            >
              {deletingDeck ? "Deleting..." : "Delete Deck"}
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
  );
};

export default DeckRight;
