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

  // Safely extract stats.
  const overall = selectedDeckInfo?.overall_stats || {
    total: 0,
    new: 0,
    learning: 0,
    review: 0,
    average_ease: 0,
  };
  const daily = selectedDeckInfo?.counts || { new: 0, learning: 0, review: 0 };

  const completionRate =
    overall.total > 0
      ? (((overall.total - overall.new) / overall.total) * 100).toFixed(1)
      : 0;

  const newPct = overall.total > 0 ? (overall.new / overall.total) * 100 : 0;
  const learningPct =
    overall.total > 0 ? (overall.learning / overall.total) * 100 : 0;
  const reviewPct =
    overall.total > 0 ? (overall.review / overall.total) * 100 : 0;

  // Average ease is clamped to render it on a stable 0-100 scale.
  const easeClamped = Math.min(Math.max(overall.average_ease, 1.3), 3.0);
  const easePct = ((easeClamped - 1.3) / (3.0 - 1.3)) * 100;

  return (
    <div className="deck-detail-panel">
      {!selectedDeckId && (
        <p className="decks-state">Select a deck to view statistics.</p>
      )}
      {statsError && <p className="decks-error">{statsError}</p>}
      {statsLoading && <p className="decks-state">Loading statistics...</p>}

      {selectedDeckInfo && !statsLoading && (
        <>
          <div className="deck-info-section">
            <h3 className="deck-info-title">{selectedDeckInfo.name}</h3>
            {selectedDeckInfo.description && (
              <p className="deck-info-description">
                {selectedDeckInfo.description}
              </p>
            )}
          </div>

          <div className="deck-stat-group">
            <h4 className="deck-group-title">Learning Progress</h4>

            <div className="deck-progress-section">
              <div className="deck-progress-header">
                <span className="deck-progress-label">Completion Rate</span>
                <span>{completionRate}%</span>
              </div>
              <div className="deck-progress-track">
                <div
                  className="deck-progress-fill"
                  style={{ width: `${completionRate}%` }}
                />
              </div>
            </div>

            <div>
              <div className="deck-distribution-header">
                <span>Card Distribution</span>
                <span className="deck-distribution-total">
                  Total: {overall.total} cards
                </span>
              </div>
              <div className="deck-distribution-bar">
                {newPct > 0 && (
                  <div
                    className="deck-segment deck-segment--new"
                    style={{ width: `${newPct}%` }}
                    title={`New: ${overall.new}`}
                  />
                )}
                {learningPct > 0 && (
                  <div
                    className="deck-segment deck-segment--learning"
                    style={{ width: `${learningPct}%` }}
                    title={`Learn: ${overall.learning}`}
                  />
                )}
                {reviewPct > 0 && (
                  <div
                    className="deck-segment deck-segment--review"
                    style={{ width: `${reviewPct}%` }}
                    title={`Review: ${overall.review}`}
                  />
                )}
                {overall.total === 0 && (
                  <div className="deck-segment deck-segment--empty" />
                )}
              </div>
              <div className="deck-legend">
                <span className="deck-legend-item">
                  <span className="deck-legend-dot deck-legend-dot--new" />
                  New ({overall.new})
                </span>
                <span className="deck-legend-item">
                  <span className="deck-legend-dot deck-legend-dot--learning" />
                  Learn ({overall.learning})
                </span>
                <span className="deck-legend-item">
                  <span className="deck-legend-dot deck-legend-dot--review" />
                  Review ({overall.review})
                </span>
              </div>
            </div>
          </div>

          <div className="deck-stat-group">
            <h4 className="deck-group-title">Today's Study</h4>
            <div className="deck-stat-grid deck-stat-grid--three">
              <div className="deck-stat-card">
                <span className="deck-stat-label">New</span>
                <strong className="deck-stat-value deck-stat-value--new">
                  {daily.new || 0}
                </strong>
              </div>
              <div className="deck-stat-card">
                <span className="deck-stat-label">Learn</span>
                <strong className="deck-stat-value deck-stat-value--learning">
                  {daily.learning || 0}
                </strong>
              </div>
              <div className="deck-stat-card">
                <span className="deck-stat-label">Review</span>
                <strong className="deck-stat-value deck-stat-value--review">
                  {daily.review || 0}
                </strong>
              </div>
            </div>
          </div>

          <div className="deck-stat-group">
            <h4 className="deck-group-title">Learning Quality</h4>
            <div className="deck-quality-section">
              <div className="deck-quality-header">
                <span>Average Difficulty</span>
                <span>{overall.average_ease.toFixed(2)}</span>
              </div>

              <div className="deck-difficulty-track">
                <div
                  className="deck-difficulty-thumb"
                  style={{ left: `${easePct}%` }}
                />
              </div>
              <div className="deck-difficulty-scale">
                <span>Hard (1.3)</span>
                <span>Easy (3.0+)</span>
              </div>
            </div>
          </div>

          <div className="deck-detail-actions">
            <button
              type="button"
              className="deck-action-btn deck-action-btn--primary"
              onClick={() => navigate(`/decks/${selectedDeckId}/study`)}
            >
              Study Now
            </button>

            <button
              type="button"
              className="deck-action-btn"
              onClick={handleOpenEditModal}
            >
              Edit
            </button>
            <button
              type="button"
              className="deck-action-btn deck-action-btn--danger"
              disabled={deletingDeck}
              onClick={handleDeleteDeck}
            >
              {deletingDeck ? "..." : "Delete"}
            </button>
            <button
              type="button"
              className="deck-action-btn deck-action-btn--primary"
              onClick={() => navigate(`/decks/${selectedDeckId}/cards`)}
            >
              Cards
            </button>
          </div>
        </>
      )}
    </div>
  );
};

export default DeckRight;
