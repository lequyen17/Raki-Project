import React, { useEffect, useState } from "react";
import { useNavigate, useParams } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { mapApiError } from "../../utils/errorMapper";
import toast from "react-hot-toast";
import "./AddCard.css";
import Button from "../../components/Common/Button/Button.js";
import {
  extractClozeIndexes,
  isValidClozeSequence,
  hasClozeDeletion,
} from "../../utils/cloze.js";
import CreateNoteType from "./components/CreateNoteType";

const AddCard = () => {
  const { t } = useTranslation();
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
      const res = await api.get(`/api/decks/${deckId}/cards/`);
      setDeckName(res.data?.deck_name || "");
    } catch (err) {
      console.error("Failed to fetch deck info", err);
    }
  };

  const fetchNoteTypes = async () => {
    try {
      const res = await api.get("/api/note-types/");
      setNoteTypes(res.data.results || []);
      if (res.data.results && res.data.results.length > 0 && !selectedNoteTypeId) {
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

  const submitAddNote = async () => {
    if (!selectedNoteTypeId) {
      toast.error(t("addCard.toast_select_note_type"));
      return;
    }

    const hasEmptyField = selectedNoteType?.definitions.some(
      (def) => !noteValues[def.id] || !noteValues[def.id].trim(),
    );

    if (hasEmptyField) {
      toast.error(t("addCard.toast_fill_all_fields"));
      return;
    }

    const payload = Object.entries(noteValues).map(([id, val]) => ({
      def_id: id,
      value: val,
    }));

    try {
      await api.post(`/api/decks/${deckId}/notes/`, {
        note_type_id: selectedNoteTypeId,
        values: payload,
      });
      toast.success(t("addCard.toast_card_added"));
      navigate(`/decks/${deckId}/cards`);
    } catch (err) {
      const errorMsg = err.response?.data?.error;
      toast.error(t("addCard.toast_add_failed", { error: errorMsg ? mapApiError(errorMsg, t, "common.error_system") : err.message }));
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
      setNtError(t("addCard.error_notetype_name_required"));
      return;
    }
    if (newDefinitions.length === 0 || validDefs.length === 0) {
      setNtError(t("addCard.error_at_least_one_field"));
      return;
    }
    if (newDefinitions.some((def) => def.value.trim() === "")) {
      setNtError(t("addCard.error_field_empty"));
      return;
    }

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
      toast.error(t("addCard.toast_at_least_one_template"));
      return;
    }
    setNewTemplates(newTemplates.filter((t_item) => t_item.id !== id));
  };

  const handleTemplateChange = (id, field, value) => {
    setNewTemplates(
      newTemplates.map((t_item) => (t_item.id === id ? { ...t_item, [field]: value } : t_item)),
    );
  };

  const submitCreateNoteType = async () => {
    const isInvalid = newTemplates.some(
      (t_item) =>
        !t_item.name.trim() || !t_item.front.trim() || (!t_item.is_cloze && !t_item.back.trim()),
    );
    if (isInvalid) {
      toast.error(t("addCard.toast_all_fields_required"));
      return;
    }

    const fieldTagRegex = /{{.*}}/;
    const hasEmptyTags = newTemplates.some((t_item) => {
      if (t_item.is_cloze) return false;
      return !fieldTagRegex.test(t_item.front) && !fieldTagRegex.test(t_item.back);
    });

    if (hasEmptyTags) {
      toast.error(t("addCard.toast_field_tag_required"));
      return;
    }

    const clozeTemplates = newTemplates.filter((t_item) => t_item.is_cloze);
    for (const t_item of clozeTemplates) {
      const indexes = extractClozeIndexes(t_item.front);
      if (indexes.length > 0 && !isValidClozeSequence(indexes)) {
        toast.error(t("addCard.toast_cloze_invalid_numbers", { name: t_item.name }));
        return;
      }
    }

    const hasInvalidClozeTemplate = newTemplates.some((t_item) => {
      if (!t_item.is_cloze) return false;
      return !hasClozeDeletion(t_item.front);
    });

    if (hasInvalidClozeTemplate) {
      toast.error(t("addCard.toast_cloze_required"));
      return;
    }

    try {
      const res = await api.post("/api/note-types/", {
        name: newNoteTypeName,
        definitions: validDefs,
        templates: newTemplates.map(({ name, is_cloze, front, back }) => ({
          name, is_cloze, front,
          back: is_cloze ? front : back,
        })),
      });
      setShowCreateNoteType(false);
      setNewNoteTypeName("");
      setNewDefinitions([{ id: Date.now(), value: "" }]);
      setNewTemplates([]);
      setNtStep(1);
      setNtError("");
      await fetchNoteTypes();
      if (res.data?.id) {
        setSelectedNoteTypeId(res.data.id);
      }
    } catch (err) {
      const errorMsg = err.response?.data?.error;
      toast.error(t("addCard.toast_create_failed", { error: errorMsg ? mapApiError(errorMsg, t, "common.error_system") : err.message }));
    }
  };

  const handleDropToTemplate = (e, templateId, field) => {
    e.preventDefault();
    const draggedData = e.dataTransfer.getData("text/plain");

    if (field === "front" && draggedData.includes("{{type:")) {
      setNtError(t("addCard.error_type_in_answer_back_only"));
      setTimeout(() => setNtError(""), 3500);
      return;
    }

    const template = newTemplates.find((t_item) => t_item.id === templateId);
    if (template) {
      handleTemplateChange(templateId, field, template[field] + draggedData);
    }
  };

  if (loading)
    return (
      <div className="add-card-page">
        <p className="state-msg">{t("addCard.loading")}</p>
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
              {t("addCard.back_to_cards")}
            </button>
            <h1 className="page-title">{t("addCard.page_title", { deckName })}</h1>
          </div>
        </header>

        <main className="add-card-content">
          {!showCreateNoteType ? (
            <div className="card-form-section card-card">
              <div className="form-group-row">
                <div className="form-group flex-1" style={{ marginBottom: 0 }}>
                  <label className="form-label">{t("addCard.select_note_type")}</label>
                  <select
                    className="form-select"
                    value={selectedNoteTypeId}
                    onChange={(e) => setSelectedNoteTypeId(e.target.value)}
                  >
                    {noteTypes.map((nt) => (
                      <option key={nt.id} value={nt.id}>
                        {nt.name} {nt.user_id ? t("addCard.custom") : t("addCard.system")}
                      </option>
                    ))}
                  </select>
                </div>
                <Button
                  onClick={() => setShowCreateNoteType(true)}
                  color="blue"
                  size="lg"
                >
                  {t("addCard.create_note_type")}
                </Button>
              </div>

              <hr className="divider" />

              <div className="fields-grid">
                {selectedNoteType?.definitions.map((def) => (
                  <div key={def.id} className="form-group">
                    <label className="form-label">{def.name}</label>
                    <textarea
                      className="form-textarea design-area"
                      value={noteValues[def.id] || ""}
                      onChange={(e) =>
                        handleNoteValueChange(def.id, e.target.value)
                      }
                      placeholder={t("addCard.enter_text_for", { field: def.name })}
                    />
                  </div>
                ))}
              </div>

              <div className="form-actions">
                <button
                  className="btn-primary btn-large"
                  onClick={submitAddNote}
                >
                  {t("addCard.add_card_btn")}
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
            />
          )}
        </main>
      </div>
    </div>
  );
};

export default AddCard;
