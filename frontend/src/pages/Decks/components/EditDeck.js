import React from "react";

const EditDeck = ({
  handleCloseEditModal,
  handleEditDeck,
  editDeck,
  setEditDeck,
  editError,
  isEditing,
}) => {
  return (
    <div className="deck-modal-overlay" onClick={handleCloseEditModal}>
      <div className="deck-modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="deck-modal-title">Edit Deck</h2>
        <form onSubmit={handleEditDeck}>
          <label className="deck-modal-label" htmlFor="edit-deck-name">
            Deck name
          </label>
          <input
            id="edit-deck-name"
            type="text"
            className="deck-modal-input"
            value={editDeck.name}
            maxLength={100}
            onChange={(e) =>
              setEditDeck((prev) => ({ ...prev, name: e.target.value }))
            }
            required
          />

          <label
            className="deck-modal-label"
            htmlFor="edit-deck-description"
          >
            Description
          </label>
          <textarea
            id="edit-deck-description"
            className="deck-modal-textarea"
            rows={4}
            value={editDeck.description}
            onChange={(e) =>
              setEditDeck((prev) => ({
                ...prev,
                description: e.target.value,
              }))
            }
          />

          {editError && <p className="deck-modal-error">{editError}</p>}

          <div className="deck-modal-actions">
            <button
              type="button"
              className="deck-modal-btn deck-modal-btn--cancel"
              onClick={handleCloseEditModal}
              disabled={isEditing}
            >
              Cancel
            </button>
            <button
              type="submit"
              className="deck-modal-btn deck-modal-btn--submit"
              disabled={isEditing}
            >
              {isEditing ? "Saving..." : "Save Changes"}
            </button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditDeck;
