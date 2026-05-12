import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import api from "../../api/api";
import ClozeEditor from "../../components/ClozeEditor/ClozeEditor";
import toast from "react-hot-toast";
import "./AddCard.css";
import Button from "../../components/Common/Button/Button.js";
import Input from "../../components/Common/Input/Input.js";
import {
  extractClozeIndexes,
  isValidClozeSequence,
  hasClozeDeletion,
} from "../../utils/cloze";
import CreateNoteType from "./components/CreateNoteType";

const AddCard = () => {
  const navigate = useNavigate();
  const { deckId } = useParams();
  const [deckName, setDeckName] = useState("");
  const [loading, setLoading] = useState(true);

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

  const selectedNoteType = noteTypes.find(
    (nt) => String(nt.id) === String(selectedNoteTypeId),
  );

  const isSystemCloze =
    selectedNoteType?.name?.toLowerCase() === "cloze" &&
    !selectedNoteType?.user_id;
  const isClozeNoteType =
    isSystemCloze ||
    selectedNoteType?.templates?.some((t) => t.is_cloze) ||
    false;

  const submitAddNote = async () => {
    if (!selectedNoteTypeId) {
      toast.error("Please select a note type.");
      return;
    }

    // Validate required fields before creating a card.
    const hasEmptyField = selectedNoteType?.definitions.some(
      (def) => !noteValues[def.id] || !noteValues[def.id].trim(),
    );

    if (hasEmptyField) {
      toast.error("Please fill in all fields before creating a card.");
      return;
    }

    const isCustomCloze = !isSystemCloze && isClozeNoteType;
    let textToValidate = "";

    if (isSystemCloze) {
      const values = Object.values(noteValues);
      const hasAnyCloze = values.some((val) => hasClozeDeletion(val));

      if (!hasAnyCloze) {
        toast.error("Cloze card must contain at least one {{c1::...}}");
        return;
      }
      textToValidate = values.join(" ");
    } else if (isCustomCloze) {
      // For custom cloze templates, the cloze markers are defined in the template fronts
      textToValidate =
        selectedNoteType?.templates
          ?.filter((t) => t.is_cloze)
          .map((t) => t.front)
          .join(" ") || "";

      // We don't force a cloze marker if the user didn't write one, but IF they wrote one, it must be valid.
    }

    if (textToValidate) {
      const indexes = extractClozeIndexes(textToValidate);
      if (indexes.length > 0 && !isValidClozeSequence(indexes)) {
        toast.error(
          "Cloze must start from c1 and not skip numbers (c1, c2, c3...)",
        );
        return;
      }
    }

    try {
      await api.post(`/api/user/decks/${deckId}/notes/`, {
        note_type_id: selectedNoteTypeId,
        values: noteValues,
      });

      toast.success("Card added successfully.");
      navigate(`/decks/${deckId}/cards`);
    } catch (err) {
      const errorMsg = err.response?.data?.error || err.message;
      toast.error("Failed to add note: " + errorMsg);
    }
  };
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
      setNtError("Note type name is required.");
      return;
    }
    if (newDefinitions.length === 0 || validDefs.length === 0) {
      setNtError("At least one field is required.");
      return;
    }
    if (newDefinitions.some((def) => def.value.trim() === "")) {
      setNtError("Field names cannot be empty.");
      return;
    }

    // Initialize first template if empty
    if (newTemplates.length === 0) {
      setNewTemplates([
        { id: Date.now(), name: "", is_cloze: false, front: "", back: "" },
      ]);
    }

    setNtStep(2);
  };

  const handleAddTemplateDraft = () => {
    setNewTemplates([
      ...newTemplates,
      { id: Date.now(), name: "", is_cloze: false, front: "", back: "" },
    ]);
  };

  const handleRemoveTemplate = (id) => {
    if (newTemplates.length <= 1) {
      toast.error("At least one template is required.");
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
      (t) =>
        !t.name.trim() || !t.front.trim() || (!t.is_cloze && !t.back.trim()),
    );
    if (isInvalid) {
      toast.error("All normal fields must include content.");
      return;
    }

    const fieldTagRegex = /{{.*}}/;
    const hasEmptyTags = newTemplates.some((t) => {
      if (t.is_cloze) return false; // Thẻ cloze đã có logic kiểm tra riêng ở dưới
      return !fieldTagRegex.test(t.front) && !fieldTagRegex.test(t.back);
    });

    if (hasEmptyTags) {
      toast.error(
        "Normal templates must contain at least one field tag (e.g., {{FieldName}}) in Front or Back design.",
      );
      return;
    }

    const clozeTemplates = newTemplates.filter((t) => t.is_cloze);
    for (const t of clozeTemplates) {
      const indexes = extractClozeIndexes(t.front);
      if (indexes.length > 0 && !isValidClozeSequence(indexes)) {
        toast.error(
          `Template "${t.name}" has invalid cloze numbers. Cloze must start from c1 and not skip numbers (c1, c2, c3...).`,
        );
        return;
      }
    }

    const hasInvalidClozeTemplate = newTemplates.some((t) => {
      if (!t.is_cloze) return false;
      return !hasClozeDeletion(t.front);
    });

    if (hasInvalidClozeTemplate) {
      toast.error("Cloze templates must contain at least one {{c1::...}}.");
      return;
    }

    try {
      const res = await api.post("/api/user/note-types/", {
        name: newNoteTypeName,
        definitions: validDefs,
        templates: newTemplates.map(({ name, is_cloze, front, back }) => ({
          name,
          is_cloze,
          front,
          back: is_cloze ? front : back,
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
      toast.error("Failed to create note type: " + errorMsg);
    }
  };

  const handleDropToTemplate = (e, templateId, field) => {
    e.preventDefault();
    const draggedData = e.dataTransfer.getData("text/plain");

    if (field === "front" && draggedData.includes("{{type:")) {
      setNtError("Type in answer fields can only be added to the Back design.");
      setTimeout(() => setNtError(""), 3500);
      return;
    }

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
                <div className="form-group flex-1" style={{ marginBottom: 0 }}>
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
                <Button
                  onClick={() => setShowCreateNoteType(true)}
                  color="blue"
                  size="lg"
                >
                  + Create New NoteType
                </Button>
              </div>

              <hr className="divider" />

              <div className="fields-grid">
                {selectedNoteType?.definitions.map((def) => (
                  <div key={def.id} className="form-group">
                    <label className="form-label">{def.name}</label>
                    <ClozeEditor
                      value={noteValues[def.id] || ""}
                      onChange={(val) => handleNoteValueChange(def.id, val)}
                      placeholder={`Enter text for ${def.name}...`}
                      isCloze={isSystemCloze}
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
            <CreateNoteType
              setShowCreateNoteType={setShowCreateNoteType}
              ntStep={ntStep}
              setNtStep={setNtStep}
              newNoteTypeName={newNoteTypeName}
              setNewNoteTypeName={setNewNoteTypeName}
              newDefinitions={newDefinitions}
              handleDefChange={handleDefChange}
              handleRemoveDefinition={handleRemoveDefinition}
              handleAddDefinition={handleAddDefinition}
              ntError={ntError}
              handleNextNtStep1={handleNextNtStep1}
              validDefs={validDefs}
              newTemplates={newTemplates}
              handleRemoveTemplate={handleRemoveTemplate}
              handleTemplateChange={handleTemplateChange}
              handleDropToTemplate={handleDropToTemplate}
              handleAddTemplateDraft={handleAddTemplateDraft}
              submitCreateNoteType={submitCreateNoteType}
              setShowGuide={setShowGuide}
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default AddCard;
