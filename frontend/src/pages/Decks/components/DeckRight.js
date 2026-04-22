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

  // Safely extract stats
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

  // Average ease usually ranges from 1.3 to above 2.5+. We clamp it between 1.3 and 3.0 for a 0-100% scale.
  const easeClamped = Math.min(Math.max(overall.average_ease, 1.3), 3.0);
  const easePct = ((easeClamped - 1.3) / (3.0 - 1.3)) * 100;

  return (
    <div
      className="deck-detail-panel"
      style={{ display: "flex", flexDirection: "column", gap: "24px" }}
    >
      {!selectedDeckId && (
        <p className="decks-state">Chon 1 deck de xem thong ke.</p>
      )}
      {statsError && <p className="decks-error">{statsError}</p>}
      {statsLoading && <p className="decks-state">Dang tai thong ke...</p>}

      {selectedDeckInfo && !statsLoading && (
        <>
          {/* 0. Tên, mô tả deck */}
          <div className="deck-info-section">
            <h3 style={{ fontSize: "1.5rem", marginBottom: "8px" }}>
              {selectedDeckInfo.name}
            </h3>
            {selectedDeckInfo.description && (
              <p
                style={{
                  color: "#666",
                  fontStyle: "italic",
                  marginBottom: "16px",
                }}
              >
                {selectedDeckInfo.description}
              </p>
            )}
          </div>

          {/* 1. Nhóm 1: Mastery Progress */}
          <div className="deck-stat-group">
            <h4
              style={{
                marginBottom: "12px",
                borderBottom: "1px solid #eee",
                paddingBottom: "8px",
              }}
            >
              Learning Progress
            </h4>

            <div style={{ marginBottom: "16px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "4px",
                }}
              >
                <span style={{ fontWeight: "500" }}>Completion Rate</span>
                <span>{completionRate}%</span>
              </div>
              <div
                style={{
                  width: "100%",
                  height: "8px",
                  backgroundColor: "#e0e0e0",
                  borderRadius: "4px",
                  overflow: "hidden",
                }}
              >
                <div
                  style={{
                    width: `${completionRate}%`,
                    height: "100%",
                    backgroundColor: "#2196f3",
                  }}
                ></div>
              </div>
            </div>

            <div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "4px",
                  fontWeight: "500",
                }}
              >
                <span>Card Distribution</span>
                <span style={{ fontSize: "0.85rem", color: "#666" }}>
                  Total: {overall.total} cards
                </span>
              </div>
              <div
                style={{
                  width: "100%",
                  height: "16px",
                  display: "flex",
                  borderRadius: "4px",
                  overflow: "hidden",
                  marginBottom: "8px",
                }}
              >
                {newPct > 0 && (
                  <div
                    style={{ width: `${newPct}%`, backgroundColor: "#9e9e9e" }}
                    title={`New: ${overall.new}`}
                  ></div>
                )}
                {learningPct > 0 && (
                  <div
                    style={{
                      width: `${learningPct}%`,
                      backgroundColor: "#ff9800",
                    }}
                    title={`Learn: ${overall.learning}`}
                  ></div>
                )}
                {reviewPct > 0 && (
                  <div
                    style={{
                      width: `${reviewPct}%`,
                      backgroundColor: "#4caf50",
                    }}
                    title={`Review: ${overall.review}`}
                  ></div>
                )}
                {overall.total === 0 && (
                  <div
                    style={{ width: "100%", backgroundColor: "#e0e0e0" }}
                  ></div>
                )}
              </div>
              <div
                style={{ display: "flex", gap: "16px", fontSize: "0.85rem" }}
              >
                <span
                  style={{ display: "flex", alignItems: "center", gap: "4px" }}
                >
                  <span
                    style={{
                      width: "10px",
                      height: "10px",
                      backgroundColor: "#9e9e9e",
                      display: "inline-block",
                      borderRadius: "2px",
                    }}
                  ></span>{" "}
                  New ({overall.new})
                </span>
                <span
                  style={{ display: "flex", alignItems: "center", gap: "4px" }}
                >
                  <span
                    style={{
                      width: "10px",
                      height: "10px",
                      backgroundColor: "#ff9800",
                      display: "inline-block",
                      borderRadius: "2px",
                    }}
                  ></span>{" "}
                  Learn ({overall.learning})
                </span>
                <span
                  style={{ display: "flex", alignItems: "center", gap: "4px" }}
                >
                  <span
                    style={{
                      width: "10px",
                      height: "10px",
                      backgroundColor: "#4caf50",
                      display: "inline-block",
                      borderRadius: "2px",
                    }}
                  ></span>{" "}
                  Review ({overall.review})
                </span>
              </div>
            </div>
          </div>

          {/* 2. Nhóm 2: Daily Workload */}
          <div className="deck-stat-group">
            <h4
              style={{
                marginBottom: "12px",
                borderBottom: "1px solid #eee",
                paddingBottom: "8px",
              }}
            >
              Today’s Study
            </h4>
            <div
              className="deck-stat-grid"
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(3, 1fr)",
                gap: "12px",
              }}
            >
              <div
                className="deck-stat-card"
                style={{
                  padding: "12px",
                  backgroundColor: "#f9f9f9",
                  borderRadius: "8px",
                  textAlign: "center",
                }}
              >
                <span
                  className="deck-stat-label"
                  style={{
                    display: "block",
                    fontSize: "0.9rem",
                    color: "#666",
                    marginBottom: "4px",
                  }}
                >
                  New
                </span>
                <strong style={{ fontSize: "1.2rem", color: "#2196f3" }}>
                  {daily.new || 0}
                </strong>
              </div>
              <div
                className="deck-stat-card"
                style={{
                  padding: "12px",
                  backgroundColor: "#f9f9f9",
                  borderRadius: "8px",
                  textAlign: "center",
                }}
              >
                <span
                  className="deck-stat-label"
                  style={{
                    display: "block",
                    fontSize: "0.9rem",
                    color: "#666",
                    marginBottom: "4px",
                  }}
                >
                  Learn
                </span>
                <strong style={{ fontSize: "1.2rem", color: "#ff9800" }}>
                  {daily.learning || 0}
                </strong>
              </div>
              <div
                className="deck-stat-card"
                style={{
                  padding: "12px",
                  backgroundColor: "#f9f9f9",
                  borderRadius: "8px",
                  textAlign: "center",
                }}
              >
                <span
                  className="deck-stat-label"
                  style={{
                    display: "block",
                    fontSize: "0.9rem",
                    color: "#666",
                    marginBottom: "4px",
                  }}
                >
                  Review
                </span>
                <strong style={{ fontSize: "1.2rem", color: "#4caf50" }}>
                  {daily.review || 0}
                </strong>
              </div>
            </div>
          </div>

          {/* 3. Nhóm 3: Quality & Health */}
          <div className="deck-stat-group">
            <h4
              style={{
                marginBottom: "12px",
                borderBottom: "1px solid #eee",
                paddingBottom: "8px",
              }}
            >
              Learning Quality
            </h4>
            <div style={{ marginBottom: "8px" }}>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginBottom: "8px",
                  fontWeight: "500",
                }}
              >
                <span>Average Difficulty</span>
                <span>{overall.average_ease.toFixed(2)}</span>
              </div>

              <div
                style={{
                  position: "relative",
                  width: "100%",
                  height: "8px",
                  borderRadius: "4px",
                  background:
                    "linear-gradient(to right, #f44336, #ffeb3b, #4caf50)",
                }}
              >
                <div
                  style={{
                    position: "absolute",
                    top: "50%",
                    left: `${easePct}%`,
                    transform: "translate(-50%, -50%)",
                    width: "16px",
                    height: "16px",
                    backgroundColor: "#fff",
                    border: "2px solid #333",
                    borderRadius: "50%",
                    transition: "left 0.3s ease",
                  }}
                ></div>
              </div>
              <div
                style={{
                  display: "flex",
                  justifyContent: "space-between",
                  marginTop: "6px",
                  fontSize: "0.8rem",
                  color: "#666",
                }}
              >
                <span>Hard (1.3)</span>
                <span>Easy (3.0+)</span>
              </div>
            </div>
          </div>

          {/* 4. Action Buttons */}
          <div
            className="deck-detail-actions"
            style={{
              display: "flex",
              gap: "8px",
              flexWrap: "wrap",
              marginTop: "auto",
              paddingTop: "16px",
            }}
          >
            <button
              type="button"
              className="deck-action-btn deck-action-btn--primary"
              style={{
                padding: "8px 16px",
                flex: "1",
                backgroundColor: "#212121",
                color: "#fff",
                fontWeight: "bold",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              onClick={() => navigate(`/decks/${selectedDeckId}/study`)}
            >
              Study Now
            </button>

            <button
              type="button"
              className="deck-action-btn"
              style={{
                padding: "8px 16px",
                backgroundColor: "#e0e0e0",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              onClick={handleOpenEditModal}
            >
              Edit
            </button>
            <button
              type="button"
              className="deck-action-btn deck-action-btn--danger"
              style={{
                padding: "8px 16px",
                backgroundColor: "#f44336",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
              disabled={deletingDeck}
              onClick={handleDeleteDeck}
            >
              {deletingDeck ? "..." : "Delete"}
            </button>
            <button
              type="button"
              className="deck-action-btn deck-action-btn--primary"
              style={{
                padding: "8px 16px",
                backgroundColor: "#2196f3",
                color: "#fff",
                border: "none",
                borderRadius: "4px",
                cursor: "pointer",
              }}
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
