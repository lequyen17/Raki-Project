import React, { useEffect, useState, useCallback } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../../api/api";
import "./CommunitySidebar.css";

function CommunitySidebar({ activeDeckId, refreshTrigger = 0 }) {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [sharedDecks, setSharedDecks] = useState([]);
  const [learningDecks, setLearningDecks] = useState([]);
  const [loading, setLoading] = useState(true);

  const fetchMyDecks = useCallback(async () => {
    try {
      setLoading(true);
      const res = await api.get("/api/decks/");
      const all = res.data?.results || [];
      const deckById = new Map(all.map((deck) => [deck.id, deck]));

      setSharedDecks(
        all.filter((deck) => deck.role === "owner" && deck.share_mode === "public")
      );
      setLearningDecks(
        all.filter((deck) => {
          if (deck.role !== "viewer") return false;
          if (!deck.parent_id) return true;
          const parent = deckById.get(deck.parent_id);
          return !parent || parent.role !== "viewer";
        })
      );
    } catch (err) {
      console.error(err);
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
      }
    } finally {
      setLoading(false);
    }
  }, [navigate]);

  useEffect(() => {
    fetchMyDecks();
  }, [fetchMyDecks, refreshTrigger]);

  const renderDeckList = (items, emptyKey) => {
    if (loading) {
      return (
        <p className="community-sidebar-empty">
          {t("community.sidebar_loading")}
        </p>
      );
    }
    if (items.length === 0) {
      return <p className="community-sidebar-empty">{t(emptyKey)}</p>;
    }
    return (
      <ul className="community-sidebar-list">
        {items.map((deck) => {
          const isActive = Number(activeDeckId) === deck.id;
          return (
            <li key={deck.id}>
              <button
                type="button"
                className={`community-sidebar-item${
                  isActive ? " community-sidebar-item--active" : ""
                }`}
                onClick={() => navigate(`/community/${deck.id}`)}
              >
                <span className="community-sidebar-item-name">{deck.name}</span>
                {deck.total_cards != null && (
                  <span className="community-sidebar-item-meta">
                    {deck.total_cards} {t("common.cards")}
                  </span>
                )}
              </button>
            </li>
          );
        })}
      </ul>
    );
  };

  return (
    <aside className="community-sidebar">
      <section className="community-sidebar-section">
        <h2 className="community-sidebar-title">
          {t("community.sidebar_shared_title")}
        </h2>
        {renderDeckList(sharedDecks, "community.sidebar_empty_shared")}
      </section>

      <section className="community-sidebar-section">
        <h2 className="community-sidebar-title">
          {t("community.sidebar_learning_title")}
        </h2>
        {renderDeckList(learningDecks, "community.sidebar_empty_learning")}
      </section>
    </aside>
  );
}

export default CommunitySidebar;
