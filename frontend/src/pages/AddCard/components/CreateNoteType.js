import React from "react";
import { useTranslation } from "react-i18next";
import NoteTypeStep1 from "./NoteTypeStep1";
import NoteTypeStep2 from "./NoteTypeStep2";

const CreateNoteType = ({
  setShowCreateNoteType,
  ntStep,
  setNtStep,
  newNoteTypeName,
  setNewNoteTypeName,
  newDefinitions,
  handleDefChange,
  handleRemoveDefinition,
  handleAddDefinition,
  ntError,
  handleNextNtStep1,
  validDefs,
  newTemplates,
  handleRemoveTemplate,
  handleTemplateChange,
  handleDropToTemplate,
  handleAddTemplateDraft,
  submitCreateNoteType,
}) => {
  const { t } = useTranslation();

  return (
    <div className="notetype-form-section card-card">
      <div className="section-header">
        <h2 className="section-title">{t("noteType.design_title")}</h2>
        <button
          className="btn-text"
          onClick={() => setShowCreateNoteType(false)}
        >
          {t("noteType.cancel")}
        </button>
      </div>

      {ntStep === 1 ? (
        <NoteTypeStep1
          newNoteTypeName={newNoteTypeName}
          setNewNoteTypeName={setNewNoteTypeName}
          newDefinitions={newDefinitions}
          handleDefChange={handleDefChange}
          handleRemoveDefinition={handleRemoveDefinition}
          handleAddDefinition={handleAddDefinition}
          ntError={ntError}
          handleNextNtStep1={handleNextNtStep1}
        />
      ) : (
        <NoteTypeStep2
          validDefs={validDefs}
          newTemplates={newTemplates}
          handleRemoveTemplate={handleRemoveTemplate}
          handleTemplateChange={handleTemplateChange}
          handleDropToTemplate={handleDropToTemplate}
          handleAddTemplateDraft={handleAddTemplateDraft}
          setNtStep={setNtStep}
          submitCreateNoteType={submitCreateNoteType}
          ntError={ntError}
        />
      )}
    </div>
  );
};

export default CreateNoteType;
