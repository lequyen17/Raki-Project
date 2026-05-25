import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { mapApiError } from "../../utils/errorMapper";
import "./Cards.css";
import Pagination, {
  usePagination,
} from "../../components/Common/Pagination/Pagination";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";

const Cards = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { deckId } = useParams();
  const [deckName, setDeckName] = useState("");
  const [cards, setCards] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");
  const [searchText, setSearchText] = useState("");
  const [filter, setFilter] = useState("all");

  const fetchCards = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get(`/api/decks/${deckId}/cards/`);
      setDeckName(res.data?.deck_name || "");
      setCards(res.data?.results || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "cards.error_load")
          : t("cards.error_load"),
      );
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    fetchCards();
  }, [deckId, navigate]);

  const getCardStatus = (card) => {
    const nextReview = card?.next_review ? new Date(card.next_review) : null;
    if (!nextReview || Number.isNaN(nextReview.getTime())) {
      return "new";
    }
    if (nextReview <= new Date()) {
      return "due";
    }
    return "scheduled";
  };

  const filteredCards = useMemo(() => {
    const keyword = searchText.trim().toLowerCase();
    return cards.filter((card) => {
      const status = getCardStatus(card);
      const cardIdText = String(card.id || "");
      const matchesSearch = !keyword || cardIdText.includes(keyword);
      const matchesFilter = filter === "all" || status === filter;
      return matchesSearch && matchesFilter;
    });
  }, [cards, searchText, filter]);

  const {
    page,
    setPage,
    totalPages,
    paginatedItems: paginatedCards,
  } = usePagination(filteredCards);

  const summary = useMemo(() => {
    return cards.reduce(
      (acc, card) => {
        const status = getCardStatus(card);
        acc.total += 1;
        if (status === "due") acc.due += 1;
        if (status === "new") acc.newCount += 1;
        if (status === "scheduled") acc.scheduled += 1;
        return acc;
      },
      { total: 0, due: 0, newCount: 0, scheduled: 0 },
    );
  }, [cards]);

  const formatDate = (value) => {
    if (!value) return t("common.not_scheduled");
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return t("common.not_scheduled");
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  const handleView = (id) => {
    navigate(`/cards/${id}`);
  };

  return (
    <div className="cards-page">
      <div className="cards-container">
        <div className="cards-actions">
          <Button
            color="gray"
            type="button"
            size="md"
            onClick={() => navigate("/decks")}
          >
            {t("cards.back_to_decks")}
          </Button>
          <Button
            type="button"
            color="green"
            size="md"
            onClick={() => navigate(`/decks/${deckId}/add-card`)}
          >
            {t("cards.add_card")}
          </Button>
          <Button
            type="button"
            color="blue"
            size="md"
            onClick={() => navigate(`/decks/${deckId}/study`)}
          >
            {t("cards.study_now")}
          </Button>
        </div>

        <div className="cards-header">
          <h1 className="cards-title">
            {t("cards.title")} {deckName ? `- ${deckName}` : ""}
          </h1>
          <div className="cards-stats">
            <span className="cards-chip">
              {t("cards.total", { count: summary.total })}
            </span>
            <span className="cards-chip cards-chip--due">
              {t("cards.due", { count: summary.due })}
            </span>
            <span className="cards-chip cards-chip--new">
              {t("cards.new", { count: summary.newCount })}
            </span>
            <span className="cards-chip cards-chip--scheduled">
              {t("cards.scheduled", { count: summary.scheduled })}
            </span>
          </div>
        </div>

        <div className="cards-toolbar">
          <input
            type="text"
            className="cards-search"
            placeholder={t("cards.search_placeholder")}
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <div className="cards-filters">
            <button
              type="button"
              className={`cards-filter-btn ${filter === "all" ? "is-active" : ""}`}
              onClick={() => setFilter("all")}
            >
              {t("cards.filter_all")}
            </button>
            <button
              type="button"
              className={`cards-filter-btn ${filter === "due" ? "is-active" : ""}`}
              onClick={() => setFilter("due")}
            >
              {t("cards.filter_due")}
            </button>
            <button
              type="button"
              className={`cards-filter-btn ${filter === "new" ? "is-active" : ""}`}
              onClick={() => setFilter("new")}
            >
              {t("cards.filter_new")}
            </button>
            <button
              type="button"
              className={`cards-filter-btn ${filter === "scheduled" ? "is-active" : ""}`}
              onClick={() => setFilter("scheduled")}
            >
              {t("cards.filter_scheduled")}
            </button>
          </div>
        </div>

        {loading && <p className="cards-state">{t("cards.loading")}</p>}
        {error && <p className="cards-error">{error}</p>}

        {!loading && !error && (
          <>
            {filteredCards.length === 0 ? (
              <div className="cards-empty">
                <p className="cards-state">{t("cards.empty")}</p>
              </div>
            ) : (
              <>
                <div className="cards-list">
                  {paginatedCards.map((card) => {
                    const status = getCardStatus(card);
                    return (
                      <div key={card.id} className="card-item">
                        <div className="card-item-main">
                          <div className="card-item-header">
                            <h3 className="card-item-title">
                              {t("cards.card_id", { id: card.id })}
                            </h3>

                            {/* Nút View thêm vào ở đây */}
                            <button
                              className="btn-view"
                              onClick={() => handleView(card.id)}
                              title={t("common.view")}
                            >
                              {t("common.view")}
                            </button>
                          </div>

                          <span
                            className={`card-status card-status--${status}`}
                          >
                            {status === "due"
                              ? t("cards.status_due")
                              : status === "new"
                                ? t("cards.status_new")
                                : t("cards.status_scheduled")}
                          </span>
                        </div>
                        <div className="card-item-meta">
                          <span className="card-meta-label">
                            {t("cards.next_review")}
                          </span>
                          <span className="card-meta-value">
                            {formatDate(card.next_review)}
                          </span>
                        </div>
                      </div>
                    );
                  })}
                </div>
                <Pagination
                  page={page}
                  totalPages={totalPages}
                  onPageChange={setPage}
                />
              </>
            )}
          </>
        )}
      </div>
    </div>
  );
};
// Cuối file Cards.js
export default Cards;
