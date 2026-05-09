import React from "react";
import Button from "../../../components/Common/Button/Button.js";
import Input from "../../../components/Common/Input/Input.js";

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

          <label className="deck-modal-label" htmlFor="edit-deck-description">
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
            <Button
              type="button"
              variant="outline"
              color="red"
              onClick={handleCloseEditModal}
              disabled={isEditing}
            >
              Cancel
            </Button>

            <Button
              type="submit"
              color="blue"
              isLoading={isEditing}
              disabled={isEditing}
            >
              Save Changes
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditDeck;
