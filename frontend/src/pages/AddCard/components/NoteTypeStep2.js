import React from "react";
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
              Available Fields (Drag into textareas):
            </label>

            <div className="help-tooltip-wrapper">
              <span className="help-icon">?</span>

              <div className="help-tooltip">
                <h3>Available Fields Guidance:</h3>

                <ul>
                  <li>
                    <strong>General Information:</strong> Use {"{{"} and {"}}"}{" "}
                    to create value placeholders. The value enclosed will be
                    replaced with user input during card creation.
                  </li>

                  <li>
                    <strong>Input Fields:</strong> Drag the specialized
                    {" {{input:...}} "}tag to the "Back Design" to automatically
                    add an input text area on the front for writing practice and
                    automatic grading. Note: Do not drag this to the front.
                  </li>

                  <li>
                    <strong>Cloze Deletion:</strong> To create fill-in-the-blank
                    questions (cloze deletion), use the format
                    {" {{c1:{{value}}}} "}in your front design, replacing
                    "value" with your desired content. Multiple clozes can be
                    created using {"{{c1:{{value1}}}}"}, {"{{c2:{{value2}}}}"},
                    etc.
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
                  Card Template #{index + 1}
                </h3>
                {newTemplates.length > 1 && (
                  <button
                    className="btn-delete-link"
                    onClick={() => handleRemoveTemplate(tmpl.id)}
                  >
                    Remove
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
                    <label className="form-label">Template Name</label>
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
                      placeholder="e.g. Recognition Card"
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
                      Cloze
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
                      {tmpl.is_cloze ? "Text Design" : "Front Design"}
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
                      <label className="form-label">Back Design</label>
                      <textarea
                        className="form-textarea design-area"
                        value={tmpl.back}
                        onChange={(e) =>
                          handleTemplateChange(tmpl.id, "back", e.target.value)
                        }
                        onDragOver={(e) => e.preventDefault()}
                        onDrop={(e) => handleDropToTemplate(e, tmpl.id, "back")}
                        placeholder="Use {{Field}} syntax"
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
          + Add Another Template
        </button>

        <div className="section-footer split section-footer--spaced">
          <button
            className="btn-secondary"
            type="button"
            onClick={() => setNtStep(1)}
          >
            &larr; Back to Fields
          </button>
          <button
            className="btn-primary"
            type="button"
            onClick={submitCreateNoteType}
          >
            Create NoteType & Continue
          </button>
        </div>
      </div>
    </div>
  );
};

export default NoteTypeStep2;
