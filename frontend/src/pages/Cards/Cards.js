import React, { useEffect, useMemo, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../api/api";
import "./Cards.css";
import Pagination, {
  usePagination,
} from "../../components/Common/Pagination/Pagination";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";

const Cards = () => {
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
      const res = await api.get(`/api/user/decks/${deckId}/cards/`);
      setDeckName(res.data?.deck_name || "");
      setCards(res.data?.results || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError(err.response?.data?.error || "Could not load card list.");
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
    if (!value) return "Not scheduled";
    const date = new Date(value);
    if (Number.isNaN(date.getTime())) return "Not scheduled";
    return date.toLocaleDateString("en-US", {
      year: "numeric",
      month: "short",
      day: "numeric",
    });
  };

  return (
    <div className="cards-page">
      <div className="cards-container">
        <div className="cards-actions">
          <Button type="button" size="md" onClick={() => navigate("/decks")}>
            Back to Decks
          </Button>

          <Button
            type="button"
            color="green"
            size="md"
            onClick={() => navigate(`/decks/${deckId}/add-card`)}
          >
            + Add Card
          </Button>

          <Button
            type="button"
            color="blue"
            size="md"
            onClick={() => navigate(`/decks/${deckId}/study`)}
          >
            Study Now
          </Button>
        </div>

        <div className="cards-header">
          <h1 className="cards-title">
            Cards {deckName ? `- ${deckName}` : ""}
          </h1>
          <div className="cards-stats">
            <span className="cards-chip">Total: {summary.total}</span>
            <span className="cards-chip cards-chip--due">
              Due: {summary.due}
            </span>
            <span className="cards-chip cards-chip--new">
              New: {summary.newCount}
            </span>
            <span className="cards-chip cards-chip--scheduled">
              Scheduled: {summary.scheduled}
            </span>
          </div>
        </div>

        <div className="cards-toolbar">
          <input
            type="text"
            className="cards-search"
            placeholder="Search by card ID..."
            value={searchText}
            onChange={(e) => setSearchText(e.target.value)}
          />
          <div className="cards-filters">
            <button
              type="button"
              className={`cards-filter-btn ${filter === "all" ? "is-active" : ""}`}
              onClick={() => setFilter("all")}
            >
              All
            </button>
            <button
              type="button"
              className={`cards-filter-btn ${filter === "due" ? "is-active" : ""}`}
              onClick={() => setFilter("due")}
            >
              Due
            </button>
            <button
              type="button"
              className={`cards-filter-btn ${filter === "new" ? "is-active" : ""}`}
              onClick={() => setFilter("new")}
            >
              New
            </button>
            <button
              type="button"
              className={`cards-filter-btn ${filter === "scheduled" ? "is-active" : ""}`}
              onClick={() => setFilter("scheduled")}
            >
              Scheduled
            </button>
          </div>
        </div>

        {loading && <p className="cards-state">Loading cards...</p>}
        {error && <p className="cards-error">{error}</p>}

        {!loading && !error && (
          <>
            {filteredCards.length === 0 ? (
              <div className="cards-empty">
                <p className="cards-state">No cards found for this view.</p>
              </div>
            ) : (
              <>
                <div className="cards-list">
                  {paginatedCards.map((card) => {
                    const status = getCardStatus(card);

                    return (
                      <div key={card.id} className="card-item">
                        <div className="card-item-main">
                          <h3 className="card-item-title">Card #{card.id}</h3>

                          <span
                            className={`card-status card-status--${status}`}
                          >
                            {status === "due"
                              ? "Due"
                              : status === "new"
                                ? "New"
                                : "Scheduled"}
                          </span>
                        </div>

                        <div className="card-item-meta">
                          <span className="card-meta-label">Next review</span>

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
