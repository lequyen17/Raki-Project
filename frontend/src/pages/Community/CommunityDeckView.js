import React, { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import api from "../../api/api";
import Button from "../../components/Common/Button/Button";
import Pagination, { usePagination } from "../../components/Common/Pagination/Pagination";
import "./CommunityDeckView.css";

const CommunityDeckView = () => {
  const { t } = useTranslation();
  const { deckId } = useParams();
  const navigate = useNavigate();

  const [deck, setDeck] = useState(null);
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [learningLoading, setLearningLoading] = useState(false);

  useEffect(() => {
    fetchDeckDetailsAndCards();
  }, [deckId]);

  const fetchDeckDetailsAndCards = async () => {
    try {
      setLoading(true);
      setError("");

      // Fetch deck details
      const deckRes = await api.get(`/api/decks/${deckId}/`);
      setDeck(deckRes.data);

      // Fetch cards
      const cardsRes = await api.get(`/api/decks/${deckId}/cards/`);
      setCards(cardsRes.data?.results || []);
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError("Failed to load deck preview details.");
    } finally {
      setLoading(false);
    }
  };

  const handleLearnDeck = async () => {
    try {
      setLearningLoading(true);
      await api.post(`/api/decks/${deckId}/learn/`);
      toast.success(t("decks.already_learning") || "Successfully added to your decks!");
      // Refresh details to update buttons/badges
      await fetchDeckDetailsAndCards();
    } catch (err) {
      console.error(err);
      toast.error(err.response?.data?.message || "Failed to learn deck.");
    } finally {
      setLearningLoading(false);
    }
  };

  const {
    page,
    setPage,
    totalPages,
    paginatedItems: paginatedCards,
  } = usePagination(cards, 8);

  if (loading && !deck) {
    return (
      <div className="preview-loading">
        <div className="spinner"></div>
        <p>{t("common.loading")}</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="preview-error">
        <p>{error}</p>
        <Button color="gray" onClick={() => navigate("/community")}>
          {t("decks.back_to_community") || "Back to Community"}
        </Button>
      </div>
    );
  }

  if (!deck) return null;

  const isLearning = deck.role === "owner" || deck.role === "viewer";

  return (
    <div className="community-deck-preview-page">
      <div className="preview-container">
        {/* Header Section */}
        <div className="preview-header">
          <Button color="gray" onClick={() => navigate("/community")}>
            &larr; {t("decks.back_to_community") || "Back to Community"}
          </Button>
        </div>

        {/* Main Deck Info Glassmorphism Card */}
        <div className="deck-preview-hero">
          <div className="hero-content">
            <h1 className="hero-title">{deck.name}</h1>
            <p className="hero-desc">{deck.description || "No description provided."}</p>
            
            <div className="hero-meta">
              <span className="meta-badge">
                <strong>{cards.length}</strong> {t("common.cards")}
              </span>
              {isLearning && (
                <span className="meta-badge badge-learning">
                  {t("decks.already_learning") || "Learning"}
                </span>
              )}
            </div>
          </div>

          <div className="hero-actions">
            {isLearning ? (
              <Button
                color="blue"
                size="lg"
                onClick={() => navigate(`/decks/${deckId}/study`)}
              >
                {t("decks.study_now") || "Study Now"}
              </Button>
            ) : (
              <Button
                color="green"
                size="lg"
                isLoading={learningLoading}
                disabled={learningLoading}
                onClick={handleLearnDeck}
              >
                {t("decks.learn_deck") || "Learn Deck"}
              </Button>
            )}
          </div>
        </div>

        {/* Cards Preview Section */}
        <div className="cards-preview-section">
          <h2 className="section-title">
            {t("cards.title") || "Cards"} ({cards.length})
          </h2>

          {cards.length === 0 ? (
            <div className="empty-cards-preview">
              <p>No cards available in this public deck.</p>
            </div>
          ) : (
            <>
              <div className="preview-cards-grid">
                {paginatedCards.map((card) => (
                  <div key={card.id} className="preview-card-item">
                    <div className="item-info">
                      <h3>{t("cards.card_id", { id: card.id })}</h3>
                      <span className="item-status-pill">
                        {t("cards.status_new") || "New"}
                      </span>
                    </div>

                    <Button
                      variant="outline"
                      color="blue"
                      size="sm"
                      onClick={() => navigate(`/cards/${card.id}`)}
                    >
                      {t("common.view") || "View"}
                    </Button>
                  </div>
                ))}
              </div>

              {totalPages > 1 && (
                <div className="preview-pagination">
                  <Pagination
                    page={page}
                    totalPages={totalPages}
                    onPageChange={setPage}
                  />
                </div>
              )}
            </>
          )}
        </div>
      </div>
    </div>
  );
};

export default CommunityDeckView;
