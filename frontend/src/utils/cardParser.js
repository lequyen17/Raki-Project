export const tokenizeTemplate = (
  templateStr,
  fieldValues,
  clozeIndex = 0,
  isBack = false,
  typedAnswers = {},
) => {
  if (!templateStr) return "";

  // Fallback: if clozeIndex is 0 but there are clozes, default to hiding c1.
  const activeCloze = clozeIndex > 0 ? clozeIndex : 1;

  let processedStr = templateStr;

  // 1. Process {{type:FieldName}}
  processedStr = processedStr.replace(
    /\{\{type:([^}]+)\}\}/g,
    (match, fieldName) => {
      const trimmed = fieldName.trim();
      if (isBack) {
        const expected = fieldValues[trimmed] || "";
        const typed = typedAnswers[trimmed] || "";
        // If we're on the back, we want to show the diff.
        const { diffHtml } = compareTypeAnswer(typed, expected);
        return diffHtml;
      }
      return `<input type="text" id="type-answer-${trimmed}" data-field="${trimmed}" class="type-answer-input" placeholder="Type answer here..." />`;
    },
  );

  // 2. Process normal {{FieldName}} and cloze
  processedStr = processedStr.replace(
    /\{\{(?:cloze:)?([^:}]+)\}\}/g,
    (match, fieldName) => {
      const trimmed = fieldName.trim();
      if (trimmed.startsWith("type:")) return match; // safety check
      return fieldValues[trimmed] !== undefined ? fieldValues[trimmed] : match;
    },
  );

  // 3. Process cloze markers globally: {{c1::Hà Nội}}
  processedStr = processedStr.replace(
    /\{\{c(\d+)::([^}]+)\}\}/g,
    (match, nStr, content) => {
      const n = parseInt(nStr, 10);
      if (n === activeCloze) {
        if (isBack) {
          return `<span class="cloze-answer" style="color: #3b82f6; font-weight: bold;">${content}</span>`;
        } else {
          return `<span class="cloze-hole" style="color: #3b82f6; font-weight: bold;">[...]</span>`;
        }
      }
      // For non-active clozes, just show the text
      return content;
    },
  );

  return processedStr;
};

// Helper for diffing two strings roughly
export const compareTypeAnswer = (userAnswer, correctAnswer) => {
  const normalize = (s) => (s || "").trim().toLowerCase();
  const u = normalize(userAnswer);
  const c = normalize(correctAnswer);

  if (u === c) {
    return {
      isCorrect: true,
      diffHtml: `<div class="type-diff correct" style="margin-top: 10px; padding: 10px; background: #e6ffed; border: 1px solid #acf2bd; border-radius: 4px; color: #22863a;">
        <span class="type-good">✅ ${correctAnswer}</span>
      </div>`,
    };
  }

  // Simple diff: just show what user typed vs what was expected.
  // Advanced diff can be added later if needed.
  return {
    isCorrect: false,
    diffHtml: `<div class="type-diff incorrect" style="margin-top: 10px; padding: 10px; background: #ffeef0; border: 1px solid #ffdce0; border-radius: 4px;">
      <del class="type-bad" style="color: #cb2431; text-decoration: line-through; display: block; margin-bottom: 5px;">❌ ${userAnswer || "(empty)"}</del>
      <ins class="type-good" style="color: #22863a; text-decoration: none; font-weight: bold; display: block;">✔️ ${correctAnswer}</ins>
    </div>`,
  };
};
