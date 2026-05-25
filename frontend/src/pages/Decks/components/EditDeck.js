import React from "react";
import { useTranslation } from "react-i18next";
import Button from "../../../components/Common/Button/Button.js";

const EditDeck = ({
  handleCloseEditModal,
  handleEditDeck,
  editDeck,
  setEditDeck,
  editError,
  isEditing,
}) => {
  const { t } = useTranslation();

  return (
    <div className="deck-modal-overlay" onClick={handleCloseEditModal}>
      <div className="deck-modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="deck-modal-title">{t("decks.edit_title")}</h2>
        <form onSubmit={handleEditDeck}>
          <label className="deck-modal-label" htmlFor="edit-deck-name">
            {t("decks.edit_name_label")}
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
            {t("decks.edit_description_label")}
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
              {t("common.cancel")}
            </Button>

            <Button
              type="submit"
              color="blue"
              isLoading={isEditing}
              disabled={isEditing}
            >
              {t("decks.edit_submit")}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default EditDeck;
