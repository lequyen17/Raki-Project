/**
 * Maps backend error codes to translated messages.
 *
 * Backend returns { "status", "message", "data" } on success,
 * or { "status": "error", "message": "ERROR_CODE", "data": null } on failure.
 * Legacy payment endpoints may still return { "error": "..." }.
 * This utility converts the code into a user-facing translated string.
 *
 * @param {string|undefined} errorCode - The error code from backend response
 * @param {Function} t - The i18next translation function
 * @param {string} fallbackKey - Translation key to use if code is not mapped
 * @returns {string} Translated error message
 */

const ERROR_CODE_MAP = {
  // Accounts
  USERNAME_TAKEN: "apiErrors.USERNAME_TAKEN",
  EMAIL_TAKEN: "apiErrors.EMAIL_TAKEN",
  CONFIRM_PASSWORD_MISMATCH: "apiErrors.CONFIRM_PASSWORD_MISMATCH",
  PHONE_INVALID_FORMAT: "apiErrors.PHONE_INVALID_FORMAT",
  PROFILE_UPDATE_FAILED: "apiErrors.PROFILE_UPDATE_FAILED",
  REGISTER_FAILED: "apiErrors.REGISTER_FAILED",
  OTP_INVALID: "apiErrors.OTP_INVALID",
  OTP_EXPIRED: "apiErrors.OTP_EXPIRED",
  OTP_NOT_FOUND: "apiErrors.OTP_NOT_FOUND",

  // Decks
  DECK_NOT_FOUND: "apiErrors.DECK_NOT_FOUND",
  DECK_NOT_FOUND_OR_NOT_VIEWER: "apiErrors.DECK_NOT_FOUND_OR_NOT_VIEWER",
  PARENT_DECK_NOT_FOUND: "apiErrors.PARENT_DECK_NOT_FOUND",
  DECK_MOVE_SELF: "apiErrors.DECK_MOVE_SELF",
  DECK_MOVE_SUBDECK: "apiErrors.DECK_MOVE_SUBDECK",
  USER_NOT_FOUND: "apiErrors.USER_NOT_FOUND",
  CANNOT_SHARE_WITH_SELF: "apiErrors.CANNOT_SHARE_WITH_SELF",
  USER_ALREADY_OWNER: "apiErrors.USER_ALREADY_OWNER",
  COLLABORATOR_NOT_FOUND: "apiErrors.COLLABORATOR_NOT_FOUND",
  INVALID_COIN_PRICE: "apiErrors.INVALID_COIN_PRICE",
  INSUFFICIENT_COINS: "apiErrors.INSUFFICIENT_COINS",

  // Cards
  CARD_NOT_FOUND: "apiErrors.CARD_NOT_FOUND",
  INVALID_QUALITY: "apiErrors.INVALID_QUALITY",

  // Notes / NoteTypes
  FIELD_REQUIRED: "apiErrors.FIELD_REQUIRED",
  FIELD_NAME_EMPTY: "apiErrors.FIELD_NAME_EMPTY",
  FIELD_NAME_DUPLICATE: "apiErrors.FIELD_NAME_DUPLICATE",
  TEMPLATE_REQUIRED: "apiErrors.TEMPLATE_REQUIRED",
  TEMPLATE_NAME_REQUIRED: "apiErrors.TEMPLATE_NAME_REQUIRED",
  FRONT_DESIGN_REQUIRED: "apiErrors.FRONT_DESIGN_REQUIRED",
  BACK_DESIGN_REQUIRED: "apiErrors.BACK_DESIGN_REQUIRED",
  FIELD_TAG_REQUIRED: "apiErrors.FIELD_TAG_REQUIRED",
  TYPE_IN_ANSWER_BACK_ONLY: "apiErrors.TYPE_IN_ANSWER_BACK_ONLY",
  CLOZE_REQUIRED: "apiErrors.CLOZE_REQUIRED",
  CLOZE_INVALID_NUMBERS: "apiErrors.CLOZE_INVALID_NUMBERS",
  NOTETYPE_NOT_FOUND: "apiErrors.NOTETYPE_NOT_FOUND",
  NOTE_FIELD_REQUIRED: "apiErrors.NOTE_FIELD_REQUIRED",
};

export function getApiErrorCode(responseData) {
  if (!responseData) return undefined;
  return responseData.error ?? responseData.message;
}

export function mapApiError(errorCode, t, fallbackKey) {
  if (!errorCode) {
    return t(fallbackKey);
  }

  const translationKey = ERROR_CODE_MAP[errorCode];
  if (translationKey) {
    return t(translationKey);
  }

  // If the error is not a known code (e.g. a raw DRF message), use fallback
  return t(fallbackKey);
}
