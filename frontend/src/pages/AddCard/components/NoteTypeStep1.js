import React from "react";

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
  return (
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
                onChange={(e) => handleDefChange(def.id, e.target.value)}
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
  );
};

export default NoteTypeStep1;
