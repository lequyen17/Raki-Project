import React from "react";
import { useTranslation } from "react-i18next";

const NoteTypeStep1 = ({
  newNoteTypeName,
  setNewNoteTypeName,
  newDefinitions,
  handleDefChange,
  handleRemoveDefinition,
  handleAddDefinition,
  ntError,
  handleNextNtStep1,
}) => {
  const { t } = useTranslation();

  return (
    <div className="nt-step-1">
      <div className="form-group">
        <label className="form-label">{t("noteType.name_label")}</label>
        <input
          className="form-input"
          value={newNoteTypeName}
          onChange={(e) => setNewNoteTypeName(e.target.value)}
          placeholder={t("noteType.name_placeholder")}
        />
      </div>

      <div className="form-group">
        <label className="form-label">{t("noteType.field_definitions")}</label>
        <div className="definitions-inputs">
          {newDefinitions.map((def) => (
            <div key={def.id} className="input-row">
              <input
                className="form-input"
                value={def.value}
                onChange={(e) => handleDefChange(def.id, e.target.value)}
                placeholder={t("noteType.field_placeholder")}
              />
              {newDefinitions.length > 1 && (
                <button
                  className="btn-icon btn-danger"
                  onClick={() => handleRemoveDefinition(def.id)}
                >
                  &times;
                </button>
              )}
            </div>
          ))}
        </div>
        <button
          className="btn-secondary btn-small"
          onClick={handleAddDefinition}
        >
          {t("noteType.add_field")}
        </button>
      </div>

      {ntError && <p className="error-text">{ntError}</p>}

      <div className="section-footer">
        <button className="btn-primary" onClick={handleNextNtStep1}>
          {t("noteType.next_design_layout")}
        </button>
      </div>
    </div>
  );
};

export default NoteTypeStep1;
