import React, { useState, useEffect } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../api/api";
import { tokenizeTemplate } from "../../utils/cardParser";
import "./Study.css";

const Study = () => {
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
      const res = await api.get(`/api/user/decks/${deckId}/study/`);
      setDeckName(res.data.deck_name);
      setCards(res.data.results || []);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setError(err.response?.data?.error || "Could not load study cards.");
    } finally {
      setLoading(false);
    }
  };

  const handleReview = async (quality) => {
    const currentCard = cards[currentIndex];
    if (!currentCard || submitting) return;

    try {
      setSubmitting(true);

      const res = await api.post(`/api/user/cards/${currentCard.id}/review/`, {
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
      alert(err.response?.data?.error || "Review failed.");
    } finally {
      setSubmitting(false);
    }
  };

  const handleShowAnswer = () => {
    // Capture typed answers from DOM
    const inputs = document.querySelectorAll('.type-answer-input');
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

  if (loading) {
    return <div className="study-loading">Preparing your study session...</div>;
  }

  if (error) {
    return (
      <div className="study-error">
        <p>{error}</p>
        <button className="study-back-btn" onClick={() => navigate("/decks")}>
          Back to Decks
        </button>
      </div>
    );
  }

  const isFinished = currentIndex >= cards.length;
  const currentCard = cards[currentIndex];

  if (isFinished) {
    return (
      <div className="study-finished-container">
        <h2>Great job!</h2>
        <p>
          You have completed today's session for <strong>{deckName}</strong>.
        </p>
        <button
          className="study-show-answer-btn"
          onClick={() => navigate("/decks")}
        >
          Back to Deck List
        </button>
      </div>
    );
  }

  const frontHTML = tokenizeTemplate(
    currentCard.template.front,
    currentCard.field_values,
    currentCard.cloze_index || 0,
    false,
    {}
  );
  
  let rawBackTemplate = currentCard.template.back;
  if (rawBackTemplate.includes("{{FrontSide}}")) {
    rawBackTemplate = rawBackTemplate.replace(/\{\{FrontSide\}\}/g, currentCard.template.front);
  }

  let backHTML = tokenizeTemplate(
    rawBackTemplate,
    currentCard.field_values,
    currentCard.cloze_index || 0,
    true,
    typedAnswers
  );
  
  // Split on <hr id='answer'> if present, and replace with back content, or Anki-like styling
  if (backHTML.includes("<hr id='answer'>")) {
    // We already have the front generated natively by Anki on the back, but here we just render the raw backHTML
    // because typically Anki's {{FrontSide}} is used, but Raki doesn't support {{FrontSide}} yet.
    // If we want we can just show backHTML.
  }

  return (
    <div className="study-container">
      <div className="study-header">
        <button className="study-back-btn" onClick={() => navigate("/decks")}>
          &larr; Back to Decks
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
          <button
            className="study-show-answer-btn"
            onClick={handleShowAnswer}
          >
            Show Answer
          </button>
        ) : (
          <div className="study-answer-actions">
            <button
              type="button"
              className="study-toggle-front-btn"
              disabled={submitting}
              onClick={() => setShowAnswer(false)}
            >
              View Front Again
            </button>
            <div className="study-rating-buttons">
              <button
                className="btn-again"
                disabled={submitting}
                onClick={() => handleReview("again")}
              >
                <span className="btn-label">Again</span>
                <span className="btn-hint">&lt;1m</span>
              </button>
              <button
                className="btn-hard"
                disabled={submitting}
                onClick={() => handleReview("hard")}
              >
                <span className="btn-label">Hard</span>
                <span className="btn-hint">&lt;10m</span>
              </button>
              <button
                className="btn-good"
                disabled={submitting}
                onClick={() => handleReview("good")}
              >
                <span className="btn-label">Good</span>
              </button>
              <button
                className="btn-easy"
                disabled={submitting}
                onClick={() => handleReview("easy")}
              >
                <span className="btn-label">Easy</span>
              </button>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default Study;
