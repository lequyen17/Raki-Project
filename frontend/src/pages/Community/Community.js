import React, { useState, useEffect } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import CoinPrice from "../../components/Common/CoinPrice/CoinPrice";
import CommunitySidebar from "./components/CommunitySidebar";
import "./Community.css";

function Community() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [decks, setDecks] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  useEffect(() => {
    fetchPublicDecks();
  }, []);

  const fetchPublicDecks = async () => {
    try {
      setLoading(true);
      const res = await api.get("/api/decks/public/");
      setDecks(res.data.results);
      setError("");
    } catch (err) {
      console.error(err);
      setError("Failed to load community decks.");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="community-container">
      <div className="community-layout">
        <CommunitySidebar />

        <main className="community-main">
          <div className="community-header">
            <h1>{t("community.title")}</h1>
            <p>{t("community.subtitle")}</p>
          </div>

          {loading ? (
            <div className="community-loading">{t("community.loading")}</div>
          ) : error ? (
            <div className="community-error">{error}</div>
          ) : decks.length === 0 ? (
            <div className="community-empty">{t("community.empty")}</div>
          ) : (
            <div className="deck-grid">
              {decks.map((deck) => {
                const isLearning =
                  deck.role === "viewer" ||
                  deck.role === "editor" ||
                  deck.role === "owner";

                return (
                  <div className="deck-card" key={deck.id}>
                    {isLearning ? (
                      <span className="deck-corner-badge deck-corner-learning">
                        {t("decks.already_learning")}
                      </span>
                    ) : (
                      <div className="deck-corner-badge">
                        <CoinPrice
                          amount={deck.coin_price}
                          variant="floating"
                        />
                      </div>
                    )}
                    <div className="deck-card-content">
                      <h3 className="deck-title">{deck.name}</h3>
                      {deck.owner && (
                        <p className="deck-owner">
                          {t("community.by_owner", { owner: deck.owner })}
                        </p>
                      )}
                      <p className="deck-desc">
                        {deck.description || t("community.no_description")}
                      </p>
                    </div>
                    <button
                      className="learn-btn"
                      onClick={() => navigate(`/community/${deck.id}`)}
                    >
                      {t("decks.view_deck")}
                    </button>
                  </div>
                );
              })}
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

export default Community;
