import React from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import Button from "../../../components/Common/Button/Button.js";

const DeckRight = ({
  selectedDeckId,
  selectedDeckInfo,
  statsLoading,
  statsError,
  handleOpenEditModal,
  deletingDeck,
  handleDeleteDeck,
  onOpenShareModal,
  unlearningDeck,
  handleStopLearning,
}) => {
  const { t } = useTranslation();
  const navigate = useNavigate();

  const overall = selectedDeckInfo?.overall_stats || {
    total: 0, new: 0, learning: 0, review: 0, average_ease: 0,
  };
  const daily = selectedDeckInfo?.counts || { new: 0, learning: 0, review: 0 };

  const completionRate = overall.total > 0
    ? (((overall.total - overall.new) / overall.total) * 100).toFixed(1) : 0;

  const newPct = overall.total > 0 ? (overall.new / overall.total) * 100 : 0;
  const learningPct = overall.total > 0 ? (overall.learning / overall.total) * 100 : 0;
  const reviewPct = overall.total > 0 ? (overall.review / overall.total) * 100 : 0;

  const easeClamped = Math.min(Math.max(overall.average_ease, 1.3), 3.0);
  const easePct = ((easeClamped - 1.3) / (3.0 - 1.3)) * 100;

  return (
    <div className="deck-detail-panel">
      {!selectedDeckId && (
        <p className="decks-state">{t("decks.select_to_view")}</p>
      )}
      {statsError && <p className="decks-error">{statsError}</p>}
      {statsLoading && <p className="decks-state">{t("decks.loading_stats")}</p>}

      {selectedDeckInfo && !statsLoading && (
        <>
          <div className="deck-info-section" style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
            <div>
              <h3 className="deck-info-title">{selectedDeckInfo.name}</h3>
              {selectedDeckInfo.description && (
                <p className="deck-info-description">{selectedDeckInfo.description}</p>
              )}
            </div>
            {selectedDeckInfo.role === "owner" && (
              <button
                type="button"
                className="deck-share-trigger"
                onClick={onOpenShareModal}
              >
                <span className="deck-share-label">
                  {t(`decks.share.mode_${selectedDeckInfo.share_mode || "private"}`)}
                </span>
                <span className="deck-share-settings-icon" aria-hidden="true">⚙</span>
              </button>
            )}
          </div>

          <div className="deck-stat-group">
            <h4 className="deck-group-title">{t("decks.learning_progress")}</h4>
            <div className="deck-progress-section">
              <div className="deck-progress-header">
                <span className="deck-progress-label">{t("decks.completion_rate")}</span>
                <span>{completionRate}%</span>
              </div>
              <div className="deck-progress-track">
                <div className="deck-progress-fill" style={{ width: `${completionRate}%` }} />
              </div>
            </div>

            <div>
              <div className="deck-distribution-header">
                <span>{t("decks.card_distribution")}</span>
                <span className="deck-distribution-total">
                  {t("decks.total_cards", { count: overall.total })}
                </span>
              </div>
              <div className="deck-distribution-bar">
                {newPct > 0 && (
                  <div className="deck-segment deck-segment--new" style={{ width: `${newPct}%` }}
                    title={`${t("decks.new_label")}: ${overall.new}`} />
                )}
                {learningPct > 0 && (
                  <div className="deck-segment deck-segment--learning" style={{ width: `${learningPct}%` }}
                    title={`${t("decks.learn_label")}: ${overall.learning}`} />
                )}
                {reviewPct > 0 && (
                  <div className="deck-segment deck-segment--review" style={{ width: `${reviewPct}%` }}
                    title={`${t("decks.review_label")}: ${overall.review}`} />
                )}
                {overall.total === 0 && (
                  <div className="deck-segment deck-segment--empty" />
                )}
              </div>
              <div className="deck-legend">
                <span className="deck-legend-item">
                  <span className="deck-legend-dot deck-legend-dot--new" />
                  {t("decks.new_count", { count: overall.new })}
                </span>
                <span className="deck-legend-item">
                  <span className="deck-legend-dot deck-legend-dot--learning" />
                  {t("decks.learn_count", { count: overall.learning })}
                </span>
                <span className="deck-legend-item">
                  <span className="deck-legend-dot deck-legend-dot--review" />
                  {t("decks.review_count", { count: overall.review })}
                </span>
              </div>
            </div>
          </div>

          <div className="deck-stat-group">
            <h4 className="deck-group-title">{t("decks.today_study")}</h4>
            <div className="deck-stat-grid deck-stat-grid--three">
              <div className="deck-stat-card">
                <span className="deck-stat-label">{t("decks.new_label")}</span>
                <strong className="deck-stat-value deck-stat-value--new">{daily.new || 0}</strong>
              </div>
              <div className="deck-stat-card">
                <span className="deck-stat-label">{t("decks.learn_label")}</span>
                <strong className="deck-stat-value deck-stat-value--learning">{daily.learning || 0}</strong>
              </div>
              <div className="deck-stat-card">
                <span className="deck-stat-label">{t("decks.review_label")}</span>
                <strong className="deck-stat-value deck-stat-value--review">{daily.review || 0}</strong>
              </div>
            </div>
          </div>

          <div className="deck-stat-group">
            <h4 className="deck-group-title">{t("decks.learning_quality")}</h4>
            <div className="deck-quality-section">
              <div className="deck-quality-header">
                <span>{t("decks.average_difficulty")}</span>
                <span>{overall.average_ease.toFixed(2)}</span>
              </div>
              <div className="deck-difficulty-track">
                <div className="deck-difficulty-thumb" style={{ left: `${easePct}%` }} />
              </div>
              <div className="deck-difficulty-scale">
                <span>{t("decks.hard_scale")}</span>
                <span>{t("decks.easy_scale")}</span>
              </div>
            </div>
          </div>

          <div className="deck-detail-actions">
            <Button type="button" color="blue"
              onClick={() => navigate(`/decks/${selectedDeckId}/study`)}>
              {t("decks.study_now")}
            </Button>
            {selectedDeckInfo.role === "owner" && (
              <>
                <Button type="button" variant="outline" color="blue" onClick={handleOpenEditModal}>
                  {t("common.edit")}
                </Button>
                <Button type="button" color="red" disabled={deletingDeck}
                  isLoading={deletingDeck} onClick={handleDeleteDeck}>
                  {t("common.delete")}
                </Button>
              </>
            )}
            {selectedDeckInfo.role === "viewer" && (
              <Button
                type="button"
                variant="outline"
                color="gray"
                disabled={unlearningDeck}
                isLoading={unlearningDeck}
                onClick={handleStopLearning}
              >
                {t("decks.stop_learning")}
              </Button>
            )}
            <Button type="button" color="green"
              onClick={() => navigate(`/decks/${selectedDeckId}/cards`)}>
              {t("decks.view_cards")}
            </Button>
          </div>
        </>
      )}
    </div>
  );
};

export default DeckRight;
