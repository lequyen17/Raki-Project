import React from "react";
import { useTranslation } from "react-i18next";
import Button from "../../../components/Common/Button/Button.js";
import Input from "../../../components/Common/Input/Input.js";

const CreateDeck = ({
  handleCloseCreateModal,
  handleCreateDeck,
  newDeck,
  setNewDeck,
  createError,
  isCreating,
}) => {
  const { t } = useTranslation();

  return (
    <div className="deck-modal-overlay" onClick={handleCloseCreateModal}>
      <div className="deck-modal" onClick={(e) => e.stopPropagation()}>
        <h2 className="deck-modal-title">{t("decks.create_title")}</h2>
        <form onSubmit={handleCreateDeck}>
          <label className="deck-modal-label" htmlFor="deck-name">
            {t("decks.create_name_label")}
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
            {t("decks.create_description_label")}
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
            <Button
              type="button"
              variant="outline"
              color="red"
              onClick={handleCloseCreateModal}
              disabled={isCreating}
            >
              {t("common.cancel")}
            </Button>

            <Button
              type="submit"
              color="blue"
              isLoading={isCreating}
              disabled={isCreating}
            >
              {t("decks.create_submit")}
            </Button>
          </div>
        </form>
      </div>
    </div>
  );
};

export default CreateDeck;
