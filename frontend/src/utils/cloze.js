/**
 * Trích xuất các chỉ số cloze (ví dụ: {{c1::text}} -> 1)
 */
export const extractClozeIndexes = (text) => {
  if (!text) return [];
  const regex = /\{\{c(\d+)::.*?\}\}/g;
  const indexes = [];
  let match;

  while ((match = regex.exec(text)) !== null) {
    indexes.push(parseInt(match[1]));
  }

  return indexes;
};

/**
 * Kiểm tra xem chuỗi cloze có hợp lệ không (bắt đầu từ 1, không nhảy số)
 */
export const isValidClozeSequence = (indexes) => {
  if (!indexes || indexes.length === 0) return false;

  const unique = [...new Set(indexes)].sort((a, b) => a - b);

  // Phải bắt đầu từ 1
  if (unique[0] !== 1) return false;

  // Không được skip số (ví dụ: 1, 2, 4 là sai)
  for (let i = 0; i < unique.length; i++) {
    if (unique[i] !== i + 1) return false;
  }

  return true;
};

/**
 * Kiểm tra xem văn bản có chứa ít nhất một thẻ cloze hợp lệ không
 */
export const hasClozeDeletion = (text) => {
  return /\{\{c\d+::[^}]+\}\}/.test(text);
};
