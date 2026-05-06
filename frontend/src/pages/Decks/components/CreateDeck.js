import React from "react";

const CreateDeck = ({
  handleCloseCreateModal,
  handleCreateDeck,
  newDeck,
  setNewDeck,
  createError,
  isCreating,
}) => {
  return (
    <div className="deck-modal-overlay" onClick={handleCloseCreateModal}>
      <div className="deck-modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="deck-modal-title">Add New Deck</h2>
        <form onSubmit={handleCreateDeck}>
          <label className="deck-modal-label" htmlFor="deck-name">
            Deck name
          </label>
          <input
            id="deck-name"
            type="text"
            className="deck-modal-input"
            value={newDeck.name}
            maxLength={100}
            onChange={(e) =>
              setNewDeck((prev) => ({ ...prev, name: e.target.value }))
            }
            required
          />

          <label className="deck-modal-label" htmlFor="deck-description">
            Description
          </label>
          <textarea
            id="deck-description"
            className="deck-modal-textarea"
            rows={4}
            value={newDeck.description}
            onChange={(e) =>
              setNewDeck((prev) => ({
                ...prev,
                description: e.target.value,
              }))
            }
          />

          {createError && <p className="deck-modal-error">{createError}</p>}

          <div className="deck-modal-actions">
            <button
              type="button"
              className="deck-modal-btn deck-modal-btn--cancel"
              onClick={handleCloseCreateModal}
              disabled={isCreating}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="deck-modal-btn deck-modal-btn--submit"
              disabled={isCreating}
            >
              {isCreating ? "Creating..." : "Create Deck"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDeck;
