import React from "react";
import { useTranslation } from "react-i18next";
import ClozeEditor from "../../../components/ClozeEditor/ClozeEditor";

const NoteTypeStep2 = ({
  validDefs,
  newTemplates,
  handleRemoveTemplate,
  handleTemplateChange,
  handleDropToTemplate,
  handleAddTemplateDraft,
  setNtStep,
  submitCreateNoteType,
  ntError,
}) => {
  const { t } = useTranslation();

  return (
    <div className="nt-step-2-layout">
      <div className="nt-sidebar">
        <div className="fields-hint sticky-sidebar">
          <div
            style={{
              display: "flex",
              alignItems: "center",
              gap: "8px",
              marginBottom: "1rem",
              position: "relative",
            }}
          >
            <label className="form-label" style={{ marginBottom: 0 }}>
              {t("noteType.available_fields")}
            </label>

            <div className="help-tooltip-wrapper">
              <span className="help-icon">?</span>

              <div className="help-tooltip">
                <h3>{t("noteType.help_title")}</h3>

                <ul>
                  <li>
                    <strong>{t("noteType.help_general_label")}</strong>{" "}
                    {t("noteType.help_general")}
                  </li>

                  <li>
                    <strong>{t("noteType.help_input_label")}</strong>{" "}
                    {t("noteType.help_input")}
                  </li>

                  <li>
                    <strong>{t("noteType.help_cloze_label")}</strong>{" "}
                    {t("noteType.help_cloze_intro")}
                    <ul>
                      <li>
                        <strong>{t("noteType.help_cloze_static_label")}</strong>{" "}
                        {t("noteType.help_cloze_static")}
                      </li>
                      <li>
                        <strong>{t("noteType.help_cloze_field_label")}</strong>{" "}
                        {t("noteType.help_cloze_field")}
                      </li>
                      <li>
                        {t("noteType.help_cloze_multiple")}
                      </li>
                    </ul>
                  </li>
                </ul>
              </div>
            </div>
          </div>

          <div className="chips-container column-layout">
            {validDefs.map((def, idx) => (
              <React.Fragment key={idx}>
                <div
                  className="field-chip"
                  draggable
                  onDragStart={(e) =>
                    e.dataTransfer.setData("text/plain", `{{${def}}}`)
                  }
                >
                  <span className="drag-handle">⋮⋮</span> {`{{${def}}}`}
                </div>
                <div
                  className="field-chip type-chip"
                  style={{
                    backgroundColor: "#e8f0fe",
                    color: "#1a73e8",
                    border: "1px solid #1a73e8",
                  }}
                  draggable
                  onDragStart={(e) =>
                    e.dataTransfer.setData("text/plain", `{{type:${def}}}`)
                  }
                >
                  <span className="drag-handle">⋮⋮</span> {`{{type:${def}}}`}
                </div>
              </React.Fragment>
            ))}
          </div>
        </div>
      </div>

      <div className="nt-main">
        {ntError && (
          <p
            className="error-text"
            style={{ marginBottom: "1rem", fontWeight: "bold" }}
          >
            {ntError}
          </p>
        )}
        <div className="templates-container">
          {newTemplates.map((tmpl, index) => (
            <div key={tmpl.id} className="template-box-item">
              <header className="template-box-header">
                <h3 className="template-box-title">
                  {t("noteType.card_template", { index: index + 1 })}
                </h3>
                {newTemplates.length > 1 && (
                  <button
                    className="btn-delete-link"
                    onClick={() => handleRemoveTemplate(tmpl.id)}
                  >
                    {t("noteType.remove")}
                  </button>
                )}
              </header>

              <div className="template-designer-fields">
                <div
                  className="form-group-row"
                  style={{
                    alignItems: "center",
                    justifyContent: "space-between",
                  }}
                >
                  <div className="form-group flex-1">
                    <label className="form-label">{t("noteType.template_name_label")}</label>
                    <input
                      className="form-input"
                      value={tmpl.name}
                      onChange={(e) =>
                        handleTemplateChange(tmpl.id, "name", e.target.value)
                      }
                      onDragOver={(e) => {
                        e.preventDefault();
                        e.dataTransfer.dropEffect = "none";
                      }}
                      onDrop={(e) => {
                        e.preventDefault();
                        e.stopPropagation();
                      }}
                      placeholder={t("noteType.template_name_placeholder")}
                    />
                  </div>
                  <div
                    className="form-group toggle-group"
                    style={{ marginLeft: "20px" }}
                  >
                    <label
                      className="form-label"
                      style={{
                        display: "inline-block",
                        marginRight: "10px",
                        marginBottom: 0,
                      }}
                    >
                      {t("noteType.cloze_label")}
                    </label>
                    <label className="switch">
                      <input
                        type="checkbox"
                        checked={tmpl.is_cloze || false}
                        onChange={(e) =>
                          handleTemplateChange(
                            tmpl.id,
                            "is_cloze",
                            e.target.checked,
                          )
                        }
                      />
                      <span className="slider round"></span>
                    </label>
                  </div>
                </div>
                <div className="design-grid">
                  <div
                    className="form-group"
                    style={tmpl.is_cloze ? { gridColumn: "1 / -1" } : {}}
                  >
                    <label className="form-label">
                      {tmpl.is_cloze ? t("noteType.text_design") : t("noteType.front_design")}
                    </label>
                    {tmpl.is_cloze ? (
                      <ClozeEditor
                        className="design-area"
                        value={tmpl.front}
                        onChange={(val) =>
                          handleTemplateChange(tmpl.id, "front", val)
                        }
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) =>
                          handleDropToTemplate(e, tmpl.id, "front")
                        }
                        placeholder={`VD: {{c1::{{${validDefs[0] || "Text"}}}}}`}
                        isCloze={true}
                      />
                    ) : (
                      <textarea
                        className="form-textarea design-area"
                        value={tmpl.front}
                        onChange={(e) =>
                          handleTemplateChange(tmpl.id, "front", e.target.value)
                        }
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) =>
                          handleDropToTemplate(e, tmpl.id, "front")
                        }
                        placeholder={`e.g. {{${validDefs[0] || "Front"}}}`}
                      />
                    )}
                  </div>
                  {!tmpl.is_cloze && (
                    <div className="form-group">
                      <label className="form-label">{t("noteType.back_design")}</label>
                      <textarea
                        className="form-textarea design-area"
                        value={tmpl.back}
                        onChange={(e) =>
                          handleTemplateChange(tmpl.id, "back", e.target.value)
                        }
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) => handleDropToTemplate(e, tmpl.id, "back")}
                        placeholder={t("noteType.back_placeholder")}
                      />
                    </div>
                  )}
                </div>
              </div>
            </div>
          ))}
        </div>

        <button
          className="btn-secondary btn-full"
          type="button"
          onClick={handleAddTemplateDraft}
        >
          {t("noteType.add_template")}
        </button>

        <div className="section-footer split section-footer--spaced">
          <button
            className="btn-secondary"
            type="button"
            onClick={() => setNtStep(1)}
          >
            {t("noteType.back_to_fields")}
          </button>
          <button
            className="btn-primary"
            type="button"
            onClick={submitCreateNoteType}
          >
            {t("noteType.create_and_continue")}
          </button>
        </div>
      </div>
    </div>
  );
};

export default NoteTypeStep2;
