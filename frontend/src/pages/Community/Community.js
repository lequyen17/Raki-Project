import React, { useState, useEffect } from "react";
import api from "../../api/api";
import "./Community.css";

function Community() {
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

  const handleLearn = async (deckId) => {
    try {
      await api.post(`/api/decks/${deckId}/learn/`);
      alert("Successfully added to your learning decks!");
      // Optionally remove from list or mark as learning
      fetchPublicDecks();
    } catch (err) {
      console.error(err);
      alert(err.response?.data?.message || "Failed to add deck.");
    }
  };

  return (
    <div className="community-container">
      <div className="community-header">
        <h1>Community Decks</h1>
        <p>Discover and learn from flashcard decks created by the community.</p>
      </div>

      {loading ? (
        <div className="community-loading">Loading decks...</div>
      ) : error ? (
        <div className="community-error">{error}</div>
      ) : decks.length === 0 ? (
        <div className="community-empty">No public decks found.</div>
      ) : (
        <div className="deck-grid">
          {decks.map((deck) => (
            <div className="deck-card" key={deck.id}>
              <div className="deck-card-content">
                <h3 className="deck-title">{deck.name}</h3>
                {deck.owner && <p className="deck-owner">By {deck.owner}</p>}
                <p className="deck-desc">
                  {deck.description || "No description provided."}
                </p>
              </div>
              <button
                className="learn-btn"
                onClick={() => handleLearn(deck.id)}
              >
                Learn Deck
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

export default Community;
