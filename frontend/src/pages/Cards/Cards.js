import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import toast from "react-hot-toast";
import api from "../../api/api";
import { tokenizeTemplate } from "../../utils/cardParser";
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
  const [deletingCardId, setDeletingCardId] = useState(null);

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

  const renderCardSides = (card) => {
    const displayFields = (card.field_values || []).reduce((acc, curr) => {
      acc[curr.name] = curr.value;
      return acc;
    }, {});

    const frontHTML = tokenizeTemplate(
      card.template?.front,
      displayFields,
      card.cloze_index || 0,
      false,
      {},
      card.template?.back,
    );

    let rawBackTemplate = card.template?.back || "";
    if (rawBackTemplate.includes("{{FrontSide}}")) {
      rawBackTemplate = rawBackTemplate.replace(
        /\{\{FrontSide\}\}/g,
        card.template?.front || "",
      );
    }

    const backHTML = tokenizeTemplate(
      rawBackTemplate,
      displayFields,
      card.cloze_index || 0,
      true,
      {},
    );

    return { frontHTML, backHTML };
  };

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
      const fieldText = (card.field_values || [])
        .map((field) => field.value || "")
        .join(" ")
        .toLowerCase();
      const matchesSearch =
        !keyword ||
        cardIdText.includes(keyword) ||
        fieldText.includes(keyword);
      const matchesFilter = filter === "all" || status === filter;
      return matchesSearch && matchesFilter;
    });
  }, [cards, searchText, filter]);

  const {
    page,
    setPage,
    totalPages,
    paginatedItems: paginatedCards,
  } = usePagination(filteredCards, 3);

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

  const handleDelete = async (cardId) => {
    if (!window.confirm(t("common.delete_confirm"))) {
      return;
    }

    try {
      setDeletingCardId(cardId);
      await api.delete(`/api/cards/${cardId}/`);
      setCards((prev) => prev.filter((card) => card.id !== cardId));
      toast.success(t("common.delete_success"));
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      toast.error(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "common.error")
          : t("common.error"),
      );
    } finally {
      setDeletingCardId(null);
    }
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
                    const { frontHTML, backHTML } = renderCardSides(card);
                    return (
                      <div key={card.id} className="card-item">
                        <div className="card-item-main">
                          <div className="card-item-header">
                            <h3 className="card-item-title">
                              {t("cards.card_id", { id: card.id })}
                            </h3>
                            <div className="card-item-actions">
                              <button
                                className="btn-view"
                                onClick={() => handleView(card.id)}
                                title={t("common.view")}
                              >
                                {t("common.edit")}
                              </button>
                              {card.is_owner && (
                                <button
                                  className="btn-delete"
                                  onClick={() => handleDelete(card.id)}
                                  disabled={deletingCardId === card.id}
                                  title={t("common.delete")}
                                >
                                  {t("common.delete")}
                                </button>
                              )}
                            </div>
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

                        <div className="card-item-preview">
                          <div className="card-item-preview-side">
                            <span className="card-item-preview-label">
                              {t("cards.front")}
                            </span>
                            <div
                              className="card-item-preview-content"
                              dangerouslySetInnerHTML={{ __html: frontHTML }}
                            />
                          </div>
                          <div className="card-item-preview-side">
                            <span className="card-item-preview-label">
                              {t("cards.back")}
                            </span>
                            <div
                              className="card-item-preview-content"
                              dangerouslySetInnerHTML={{ __html: backHTML }}
                            />
                          </div>
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
