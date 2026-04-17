import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../api/api";
import "./AddCardUI.css";

const AddCard = () => {
  const navigate = useNavigate();
  const { deckId } = useParams();
  const [deckName, setDeckName] = useState("");
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  // NoteTypes state
  const [noteTypes, setNoteTypes] = useState([]);
  const [selectedNoteTypeId, setSelectedNoteTypeId] = useState("");
  const [noteValues, setNoteValues] = useState({});
  const [showCreateNoteType, setShowCreateNoteType] = useState(false);

  // CREATE NOTETYPE logic states
  const [newNoteTypeName, setNewNoteTypeName] = useState("");
  const [newDefinitions, setNewDefinitions] = useState([
    { id: Date.now(), value: "" },
  ]);
  const [newTemplates, setNewTemplates] = useState([]);
  const [ntStep, setNtStep] = useState(1);
  const [ntError, setNtError] = useState("");

  const fetchDeckInfo = async () => {
    try {
      const res = await api.get(`/api/user/decks/${deckId}/cards/`);
      setDeckName(res.data?.deck_name || "");
    } catch (err) {
      console.error("Failed to fetch deck info", err);
    }
  };

  const fetchNoteTypes = async () => {
    try {
      const res = await api.get("/api/user/note-types/");
      setNoteTypes(res.data.results || []);
      if (
        res.data.results &&
        res.data.results.length > 0 &&
        !selectedNoteTypeId
      ) {
        setSelectedNoteTypeId(res.data.results[0].id);
      }
    } catch (err) {
      console.error("Failed to fetch note types", err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }
    fetchDeckInfo();
    fetchNoteTypes();
  }, [deckId, navigate]);

  const handleNoteValueChange = (defId, val) => {
    setNoteValues((prev) => ({ ...prev, [defId]: val }));
  };

  const submitAddNote = async () => {
    if (!selectedNoteTypeId) {
      alert("Vui lòng chọn Note Type");
      return;
    }
    try {
      await api.post(`/api/user/decks/${deckId}/notes/`, {
        note_type_id: selectedNoteTypeId,
        values: noteValues,
      });
      alert("Đã thêm card thành công!");
      setNoteValues({});
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      alert("Failed to add note: " + errorMsg);
    }
  };

  const selectedNoteType = noteTypes.find(
    (nt) => String(nt.id) === String(selectedNoteTypeId),
  );

  // NoteType Creation Handlers
  const resetTemplates = () => {
    if (newTemplates.length > 0) {
      setNewTemplates([]);
    }
  };

  const handleAddDefinition = () => {
    resetTemplates();
    setNewDefinitions([
      ...newDefinitions,
      { id: Date.now() + Math.random(), value: "" },
    ]);
  };
  const handleDefChange = (id, val) => {
    resetTemplates();
    setNewDefinitions(
      newDefinitions.map((def) =>
        def.id === id ? { ...def, value: val } : def,
      ),
    );
  };
  const handleRemoveDefinition = (id) => {
    resetTemplates();
    setNewDefinitions(newDefinitions.filter((def) => def.id !== id));
  };
  const validDefs = newDefinitions.map((d) => d.value.trim()).filter(Boolean);

  const handleNextNtStep1 = () => {
    setNtError("");
    if (!newNoteTypeName.trim()) {
      setNtError("NoteType Name không được để trống.");
      return;
    }
    if (newDefinitions.length === 0 || validDefs.length === 0) {
      setNtError("Phải có ít nhất một field.");
      return;
    }
    if (newDefinitions.some((def) => def.value.trim() === "")) {
      setNtError("Không được để field name trống.");
      return;
    }

    // Initialize first template if empty
    if (newTemplates.length === 0) {
      setNewTemplates([{ id: Date.now(), name: "", front: "", back: "" }]);
    }

    setNtStep(2);
  };

  const handleAddTemplateDraft = () => {
    setNewTemplates([
      ...newTemplates,
      { id: Date.now(), name: "", front: "", back: "" },
    ]);
  };

  const handleRemoveTemplate = (id) => {
    if (newTemplates.length <= 1) {
      alert("Phải có ít nhất một template.");
      return;
    }
    setNewTemplates(newTemplates.filter((t) => t.id !== id));
  };

  const handleTemplateChange = (id, field, value) => {
    setNewTemplates(
      newTemplates.map((t) => (t.id === id ? { ...t, [field]: value } : t)),
    );
  };

  const submitCreateNoteType = async () => {
    // Validation
    const isInvalid = newTemplates.some(
      (t) => !t.name.trim() || !t.front.trim() || !t.back.trim(),
    );
    if (isInvalid) {
      alert(
        "Tất cả các template phải được điền đầy đủ thông tin (Tên, Front, Back).",
      );
      return;
    }

    try {
      const res = await api.post("/api/user/note-types/", {
        name: newNoteTypeName,
        definitions: validDefs,
        templates: newTemplates.map(({ name, front, back }) => ({
          name,
          front,
          back,
        })),
      });
      // Reset creation state
      setShowCreateNoteType(false);
      setNewNoteTypeName("");
      setNewDefinitions([{ id: Date.now(), value: "" }]);
      setNewTemplates([]);
      setNtStep(1);
      setNtError("");

      // Refresh list and select new one
      await fetchNoteTypes();
      if (res.data?.id) {
        setSelectedNoteTypeId(res.data.id);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      alert("Failed to create note type: " + errorMsg);
    }
  };

  const handleDropToTemplate = (e, templateId, field) => {
    e.preventDefault();
    const draggedData = e.dataTransfer.getData("text/plain");
    const template = newTemplates.find((t) => t.id === templateId);
    if (template) {
      handleTemplateChange(templateId, field, template[field] + draggedData);
    }
  };

  if (loading)
    return (
      <div className="add-card-page">
        <p className="state-msg">Loading content...</p>
      </div>
    );

  return (
    <div className="add-card-page">
      <div className="add-card-container">
        <header className="page-header">
          <div className="header-left">
            <button
              className="btn-back"
              onClick={() => navigate(`/decks/${deckId}/cards`)}
            >
              &larr; Back to Cards
            </button>
            <h1 className="page-title">Add New Cards to {deckName}</h1>
          </div>
        </header>

        <main className="add-card-content">
          {!showCreateNoteType ? (
            <div className="card-form-section card-card">
              <div className="form-group-row">
                <div className="form-group flex-1">
                  <label className="form-label">Select Note Type</label>
                  <select
                    className="form-select"
                    value={selectedNoteTypeId}
                    onChange={(e) => setSelectedNoteTypeId(e.target.value)}
                  >
                    {noteTypes.map((nt) => (
                      <option key={nt.id} value={nt.id}>
                        {nt.name} {nt.user_id ? "(Custom)" : "(System)"}
                      </option>
                    ))}
                  </select>
                </div>
                <button
                  className="btn-secondary btn-action"
                  onClick={() => setShowCreateNoteType(true)}
                >
                  + Create New NoteType
                </button>
              </div>

              <hr className="divider" />

              <div className="fields-grid">
                {selectedNoteType?.definitions.map((def) => (
                  <div key={def.id} className="form-group">
                    <label className="form-label">{def.name}</label>
                    <textarea
                      className="form-textarea"
                      value={noteValues[def.id] || ""}
                      onChange={(e) =>
                        handleNoteValueChange(def.id, e.target.value)
                      }
                      placeholder={`Enter text for ${def.name}...`}
                    />
                  </div>
                ))}
              </div>

              <div className="form-actions">
                <button
                  className="btn-primary btn-large"
                  onClick={submitAddNote}
                >
                  Add Card
                </button>
              </div>
            </div>
          ) : (
            <div className="notetype-form-section card-card">
              <div className="section-header">
                <h2 className="section-title">Design Your Custom NoteType</h2>
                <button
                  className="btn-text"
                  onClick={() => setShowCreateNoteType(false)}
                >
                  Cancel
                </button>
              </div>

              {ntStep === 1 ? (
                <div className="nt-step-1">
                  <div className="form-group">
                    <label className="form-label">NoteType Name</label>
                    <input
                      className="form-input"
                      value={newNoteTypeName}
                      onChange={(e) => setNewNoteTypeName(e.target.value)}
                      placeholder="e.g. English-Vietnamese"
                    />
                  </div>

                  <div className="form-group">
                    <label className="form-label">Field Definitions</label>
                    <div className="definitions-inputs">
                      {newDefinitions.map((def) => (
                        <div key={def.id} className="input-row">
                          <input
                            className="form-input"
                            value={def.value}
                            onChange={(e) =>
                              handleDefChange(def.id, e.target.value)
                            }
                            placeholder="Field Name"
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
                      + Add Another Field
                    </button>
                  </div>

                  {ntError && <p className="error-text">{ntError}</p>}

                  <div className="section-footer">
                    <button className="btn-primary" onClick={handleNextNtStep1}>
                      Next: Design Layout &rarr;
                    </button>
                  </div>
                </div>
              ) : (
                <div className="nt-step-2">
                  <div className="fields-hint">
                    <label className="form-label">
                      Available Fields (Drag into textareas):
                    </label>
                    <div className="chips-container">
                      {validDefs.map((def, idx) => (
                        <span
                          key={idx}
                          className="field-chip"
                          draggable
                          onDragStart={(e) =>
                            e.dataTransfer.setData("text/plain", `{{${def}}}`)
                          }
                        >
                          {def}
                        </span>
                      ))}
                    </div>
                  </div>

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
                              Remove{" "}
                            </button>
                          )}
                        </header>

                        <div className="template-designer-fields">
                          <div className="form-group">
                            <label className="form-label">Template Name</label>
                            <input
                              className="form-input"
                              value={tmpl.name}
                              onChange={(e) =>
                                handleTemplateChange(
                                  tmpl.id,
                                  "name",
                                  e.target.value,
                                )
                              }
                              placeholder="e.g. Recognition Card"
                            />
                          </div>
                          <div className="design-grid">
                            <div className="form-group">
                              <label className="form-label">Front Design</label>
                              <textarea
                                className="form-textarea design-area"
                                value={tmpl.front}
                                onChange={(e) =>
                                  handleTemplateChange(
                                    tmpl.id,
                                    "front",
                                    e.target.value,
                                  )
                                }
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={(e) =>
                                  handleDropToTemplate(e, tmpl.id, "front")
                                }
                                placeholder={`e.g. {{${validDefs[0] || "Front"}}}`}
                              />
                            </div>
                            <div className="form-group">
                              <label className="form-label">Back Design</label>
                              <textarea
                                className="form-textarea design-area"
                                value={tmpl.back}
                                onChange={(e) =>
                                  handleTemplateChange(
                                    tmpl.id,
                                    "back",
                                    e.target.value,
                                  )
                                }
                                onDragOver={(e) => e.preventDefault()}
                                onDrop={(e) =>
                                  handleDropToTemplate(e, tmpl.id, "back")
                                }
                                placeholder="Use {{Field}} syntax"
                              />
                            </div>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>

                  <button
                    className="btn-secondary btn-full"
                    style={{ marginTop: "16px" }}
                    onClick={handleAddTemplateDraft}
                  >
                    + Add Another Template 
                  </button>

                  <div
                    className="section-footer split"
                    style={{ marginTop: "40px" }}
                  >
                    <button
                      className="btn-secondary"
                      onClick={() => setNtStep(1)}
                    >
                      &larr; Back to Fields
                    </button>
                    <button
                      className="btn-primary"
                      onClick={submitCreateNoteType}
                    >
                      Create NoteType & Continue
                    </button>
                  </div>
                </div>
              )}
            </div>
          )}
        </main>
      </div>
    </div>
  );
};

export default AddCard;
