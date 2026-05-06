import React, { useRef } from "react";
import "./ClozeEditor.css";

const ClozeEditor = ({ value, onChange, placeholder, className, isCloze }) => {
  const textareaRef = useRef(null);

  const handleClozeClick = () => {
    const textarea = textareaRef.current;
    if (!textarea) return;

    const start = textarea.selectionStart;
    const end = textarea.selectionEnd;
    const selectedText = value.substring(start, end);

    if (!selectedText) {
      alert("Please select some text to cloze.");
      return;
    }

    // Find highest cloze index in the current value
    const matches = value.match(/\{\{c(\d+)::/g);
    let maxIndex = 0;
    if (matches) {
      matches.forEach((m) => {
        const idx = parseInt(m.match(/\d+/)[0], 10);
        if (idx > maxIndex) {
          maxIndex = idx;
        }
      });
    }

    const newIndex = maxIndex + 1;
    const clozeText = `{{c${newIndex}::${selectedText}}}`;

    const newValue =
      value.substring(0, start) + clozeText + value.substring(end);

    onChange(newValue);

    // Set cursor position after the newly inserted cloze
    setTimeout(() => {
      textarea.focus();
      textarea.setSelectionRange(
        start + clozeText.length,
        start + clozeText.length
      );
    }, 0);
  };

  return (
    <div className={`cloze-editor-container ${className || ""}`}>
      {isCloze && (
        <div className="cloze-toolbar">
          <button
            type="button"
            className="cloze-btn"
            onClick={handleClozeClick}
            title="Highlight text and click to create a cloze deletion."
          >
            [ + Cloze ]
          </button>
        </div>
      )}
      <textarea
        ref={textareaRef}
        className="cloze-textarea"
        value={value}
        onChange={(e) => onChange(e.target.value)}
        placeholder={placeholder}
      />
    </div>
  );
};

export default ClozeEditor;
