import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { mapApiError } from "../../utils/errorMapper";
import { tokenizeTemplate } from "../../utils/cardParser";
import toast from "react-hot-toast";
import "./Study.css";

const Study = () => {
  const { t } = useTranslation();
  const { deckId } = useParams();
  const navigate = useNavigate();

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const [deckName, setDeckName] = useState("");
  const [cards, setCards] = useState([]);
  const [currentIndex, setCurrentIndex] = useState(0);
  const [showAnswer, setShowAnswer] = useState(false);
  const [submitting, setSubmitting] = useState(false);
  const [typedAnswers, setTypedAnswers] = useState({});

  useEffect(() => {
    fetchStudyCards();
  }, [deckId]);

  const fetchStudyCards = async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get(`/api/decks/${deckId}/study/`);
      setDeckName(res.data.deck_name);
      setCards(res.data.results || []);
      console.log(res.data.results);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "study.error_load")
          : t("study.error_load"),
      );
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality) => {
    const currentCard = cards[currentIndex];
    if (!currentCard || submitting) return;

    try {
      setSubmitting(true);

      const res = await api.post(`/api/cards/${currentCard.id}/review/`, {
        quality,
      });

      const { interval, status: nextStatus } = res.data;

      let newCards = [...cards];

      if (interval === 0) {
        const cardToRepeat = {
          ...currentCard,
          status: nextStatus,
        };

        if (quality === "again") {
          const insertAt = Math.min(currentIndex + 6, newCards.length);
          newCards.splice(insertAt, 0, cardToRepeat);
        } else {
          newCards.push(cardToRepeat);
        }

        setCards(newCards);
      }

      setShowAnswer(false);
      setTypedAnswers({});
      setCurrentIndex((prev) => prev + 1);
    } catch (err) {
      console.error(err);
      toast.error(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "study.error_review")
          : t("study.error_review"),
      );
    } finally {
      setSubmitting(false);
    }
  };

  const handleShowAnswer = () => {
    // Capture typed answers from DOM
    const inputs = document.querySelectorAll(".type-answer-input");
    const newAnswers = {};
    inputs.forEach((input) => {
      newAnswers[input.dataset.field] = input.value;
    });
    setTypedAnswers(newAnswers);
    setShowAnswer(true);

    console.log(inputs);
    console.log(newAnswers);
    console.log(currentCard.template.back);
    console.log(backHTML);
  };

  useEffect(() => {
    const handleKeyDown = (e) => {
      const tagName = e.target.tagName;
      if (e.key !== "Enter" || e.shiftKey) return;

      // Avoid triggering if we're already showing the answer or submitting
      if (showAnswer || submitting) return;

      // Prevent default behavior (like form submit) and show answer
      e.preventDefault();
      handleShowAnswer();
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [showAnswer, submitting]);

  if (loading) {
    return <div className="study-loading">{t("study.preparing")}</div>;
  }

  if (error) {
    return (
      <div className="study-error">
        <p>{error}</p>
        <button className="study-back-btn" onClick={() => navigate("/decks")}>
          {t("study.back_to_decks_btn")}
        </button>
      </div>
    );
  }

  const isFinished = currentIndex >= cards.length;
  const currentCard = cards[currentIndex];

  if (isFinished) {
    return (
      <div className="study-finished-container">
        <h2>{t("study.finished_title")}</h2>
        <p
          dangerouslySetInnerHTML={{
            __html: t("study.finished_message", { deckName }),
          }}
        />
        <button
          className="study-show-answer-btn"
          onClick={() => navigate("/decks")}
        >
          {t("study.back_to_deck_list")}
        </button>
      </div>
    );
  }

  const displayFields = (currentCard.field_values || []).reduce((acc, curr) => {
    acc[curr.name] = curr.value;
    return acc;
  }, {});

  const frontHTML = tokenizeTemplate(
    currentCard.template.front,
    displayFields,
    currentCard.cloze_index || 0,
    false,
    {},
    currentCard.template.back,
  );

  let rawBackTemplate = currentCard.template.back;
  if (rawBackTemplate.includes("{{FrontSide}}")) {
    rawBackTemplate = rawBackTemplate.replace(
      /\{\{FrontSide\}\}/g,
      currentCard.template.front,
    );
  }

  let backHTML = tokenizeTemplate(
    rawBackTemplate,
    displayFields,
    currentCard.cloze_index || 0,
    true,
    typedAnswers,
  );

  // Split on <hr id='answer'> if present
  if (backHTML.includes("<hr id='answer'>")) {
    // Render the raw backHTML as-is
  }

  return (
    <div className="study-container">
      <div className="study-header">
        <button className="study-back-btn" onClick={() => navigate("/decks")}>
          {t("study.back_to_decks")}
        </button>
        <div className="study-header-meta">
          <div className="study-deck-name">{deckName}</div>
        </div>
      </div>

      <div className="study-progress-bar">
        <div
          className="study-progress-fill"
          style={{ width: `${(currentIndex / cards.length) * 100}%` }}
        />
      </div>

      <div className="study-card-wrapper">
        <div className="study-card">
          {!showAnswer ? (
            <div
              className="study-card-section study-front"
              dangerouslySetInnerHTML={{ __html: frontHTML }}
            />
          ) : (
            <div
              className="study-card-section study-back"
              dangerouslySetInnerHTML={{ __html: backHTML }}
            />
          )}
        </div>
      </div>

      <div className="study-controls">
        {!showAnswer ? (
          <button className="study-show-answer-btn" onClick={handleShowAnswer}>
            {t("study.show_answer")}
          </button>
        ) : (
          <div className="study-answer-actions">
            <button
              type="button"
              className="study-toggle-front-btn"
              disabled={submitting}
              onClick={() => setShowAnswer(false)}
            >
              {t("study.view_front_again")}
            </button>
            <div className="study-rating-buttons">
              <button
                className="btn-again"
                disabled={submitting}
                onClick={() => handleReview("again")}
              >
                <span className="btn-label">{t("study.again")}</span>
                <span className="btn-hint">&lt;1m</span>
              </button>
              <button
                className="btn-hard"
                disabled={submitting}
                onClick={() => handleReview("hard")}
              >
                <span className="btn-label">{t("study.hard")}</span>
                <span className="btn-hint">&lt;10m</span>
              </button>
              <button
                className="btn-good"
                disabled={submitting}
                onClick={() => handleReview("good")}
              >
                <span className="btn-label">{t("study.good")}</span>
              </button>
              <button
                className="btn-easy"
                disabled={submitting}
                onClick={() => handleReview("easy")}
              >
                <span className="btn-label">{t("study.easy")}</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Study;
