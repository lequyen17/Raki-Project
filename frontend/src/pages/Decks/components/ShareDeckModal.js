import React, { useCallback, useEffect, useRef, useState } from "react";
import { useTranslation } from "react-i18next";
import api from "../../../api/api";
import { mapApiError } from "../../../utils/errorMapper";
import Button from "../../../components/Common/Button/Button.js";

const SHARE_MODES = ["private", "public", "restricted"];
const ROLES = ["viewer", "editor"];

const ShareDeckModal = ({
  deckId,
  deckName,
  onClose,
  onSaved,
}) => {
  const { t } = useTranslation();
  const [loading, setLoading] = useState(true);
  const [saving, setSaving] = useState(false);
  const [error, setError] = useState("");

  const [shareMode, setShareMode] = useState("private");
  const [accessType, setAccessType] = useState("free");
  const [coinPrice, setCoinPrice] = useState("");
  const [collaborators, setCollaborators] = useState([]);

  const [inviteUsername, setInviteUsername] = useState("");
  const [inviteRole, setInviteRole] = useState("viewer");
  const [inviting, setInviting] = useState(false);
  const [removingUserId, setRemovingUserId] = useState(null);

  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searchLoading, setSearchLoading] = useState(false);
  const [showSearchDropdown, setShowSearchDropdown] = useState(false);
  const searchTimeoutRef = useRef(null);
  const searchContainerRef = useRef(null);

  const applySettings = useCallback((data) => {
    setShareMode(data.share_mode || "private");
    setAccessType(data.access_type || (data.coin_price > 0 ? "premium" : "free"));
    setCoinPrice(data.coin_price > 0 ? String(data.coin_price) : "");
    setCollaborators(data.collaborators || []);
  }, []);

  const fetchSettings = useCallback(async () => {
    try {
      setLoading(true);
      setError("");
      const res = await api.get(`/api/decks/${deckId}/share/`);
      applySettings(res.data);
    } catch (err) {
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "decks.share.error_load")
          : t("decks.share.error_load"),
      );
    } finally {
      setLoading(false);
    }
  }, [deckId, applySettings, t]);

  useEffect(() => {
    fetchSettings();
  }, [fetchSettings]);

  useEffect(() => {
    const handleClickOutside = (e) => {
      if (
        searchContainerRef.current &&
        !searchContainerRef.current.contains(e.target)
      ) {
        setShowSearchDropdown(false);
      }
    };
    document.addEventListener("mousedown", handleClickOutside);
    return () => document.removeEventListener("mousedown", handleClickOutside);
  }, []);

  const runUserSearch = (query) => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    const trimmed = query.trim();
    if (trimmed.length < 2) {
      setSearchResults([]);
      setSearchLoading(false);
      return;
    }

    searchTimeoutRef.current = setTimeout(async () => {
      try {
        setSearchLoading(true);
        const res = await api.get("/api/users/search/", { params: { q: trimmed } });
        setSearchResults(res.data?.results || []);
      } catch {
        setSearchResults([]);
      } finally {
        setSearchLoading(false);
      }
    }, 300);
  };

  const handleSearchChange = (value) => {
    setSearchQuery(value);
    setInviteUsername(value);
    setShowSearchDropdown(true);
    runUserSearch(value);
  };

  const handleSelectUser = (user) => {
    setInviteUsername(user.username);
    setSearchQuery(user.username);
    setShowSearchDropdown(false);
    setSearchResults([]);
  };

  const handleSave = async () => {
    if (shareMode === "public" && accessType === "premium") {
      const price = parseInt(coinPrice, 10);
      if (!price || price <= 0) {
        setError(t("decks.share.coin_price_invalid"));
        return;
      }
    }

    try {
      setSaving(true);
      setError("");
      const payload = {
        share_mode: shareMode,
        coin_price:
          shareMode === "public" && accessType === "premium"
            ? parseInt(coinPrice, 10)
            : 0,
      };
      const res = await api.put(`/api/decks/${deckId}/share/`, payload);
      applySettings(res.data);
      onSaved?.(res.data);
      onClose();
    } catch (err) {
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "decks.share.error_save")
          : t("decks.share.error_save"),
      );
    } finally {
      setSaving(false);
    }
  };

  const handleInvite = async () => {
    const username = inviteUsername.trim();
    if (!username) {
      return;
    }

    try {
      setInviting(true);
      setError("");
      const res = await api.post(`/api/decks/${deckId}/collaborators/`, {
        username,
        role: inviteRole,
      });
      applySettings(res.data);
      setInviteUsername("");
      setSearchQuery("");
      setSearchResults([]);
      if (shareMode !== "restricted") {
        setShareMode("restricted");
      }
      onSaved?.(res.data);
    } catch (err) {
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "decks.share.error_invite")
          : t("decks.share.error_invite"),
      );
    } finally {
      setInviting(false);
    }
  };

  const handleRemoveCollaborator = async (userId) => {
    try {
      setRemovingUserId(userId);
      setError("");
      const res = await api.delete(
        `/api/decks/${deckId}/collaborators/${userId}/`,
      );
      applySettings(res.data);
      onSaved?.(res.data);
    } catch (err) {
      setError(
        err.response?.data?.error
          ? mapApiError(err.response.data.error, t, "decks.share.error_remove")
          : t("decks.share.error_remove"),
      );
    } finally {
      setRemovingUserId(null);
    }
  };

  return (
    <div className="deck-modal-overlay" onClick={onClose}>
      <div
        className="deck-modal deck-share-modal"
        onClick={(e) => e.stopPropagation()}
      >
        <div className="deck-share-modal-header">
          <div>
            <h2 className="deck-modal-title">{t("decks.share.title")}</h2>
            <p className="deck-share-deck-name">{deckName}</p>
          </div>
          <button
            type="button"
            className="deck-share-close-btn"
            onClick={onClose}
            aria-label={t("common.cancel")}
          >
            ×
          </button>
        </div>

        {loading ? (
          <p className="decks-state">{t("common.loading")}</p>
        ) : (
          <>
            <div className="deck-share-tabs" role="tablist">
              {SHARE_MODES.map((mode) => (
                <button
                  key={mode}
                  type="button"
                  role="tab"
                  aria-selected={shareMode === mode}
                  className={`deck-share-tab ${shareMode === mode ? "active" : ""}`}
                  onClick={() => setShareMode(mode)}
                >
                  {t(`decks.share.mode_${mode}`)}
                </button>
              ))}
            </div>

            <p className="deck-share-mode-desc">
              {t(`decks.share.mode_${shareMode}_desc`)}
            </p>

            {shareMode === "public" && (
              <div className="deck-share-section">
                <span className="deck-modal-label">{t("decks.share.access_type")}</span>
                <div className="deck-share-radio-group">
                  <label className="deck-share-radio">
                    <input
                      type="radio"
                      name="accessType"
                      value="free"
                      checked={accessType === "free"}
                      onChange={() => setAccessType("free")}
                    />
                    {t("decks.share.access_free")}
                  </label>
                  <label className="deck-share-radio">
                    <input
                      type="radio"
                      name="accessType"
                      value="premium"
                      checked={accessType === "premium"}
                      onChange={() => setAccessType("premium")}
                    />
                    {t("decks.share.access_premium")}
                  </label>
                </div>

                {accessType === "premium" && (
                  <div className="deck-share-coin-field">
                    <label className="deck-modal-label" htmlFor="coin-price">
                      {t("decks.share.coin_price_label")}
                    </label>
                    <input
                      id="coin-price"
                      type="number"
                      min="1"
                      className="deck-modal-input"
                      placeholder={t("decks.share.coin_price_placeholder")}
                      value={coinPrice}
                      onChange={(e) => setCoinPrice(e.target.value)}
                    />
                  </div>
                )}
              </div>
            )}

            {(shareMode === "restricted" || collaborators.length > 0) && (
              <div className="deck-share-section">
                <span className="deck-modal-label">{t("decks.share.members")}</span>

                <div className="deck-share-invite-row">
                  <div className="deck-share-search" ref={searchContainerRef}>
                    <input
                      type="text"
                      className="deck-modal-input"
                      placeholder={t("decks.share.username_placeholder")}
                      value={searchQuery}
                      onChange={(e) => handleSearchChange(e.target.value)}
                      onFocus={() => setShowSearchDropdown(true)}
                    />
                    {showSearchDropdown && (searchLoading || searchResults.length > 0) && (
                      <ul className="deck-share-search-dropdown">
                        {searchLoading && (
                          <li className="deck-share-search-item muted">
                            {t("common.loading")}
                          </li>
                        )}
                        {!searchLoading && searchResults.length === 0 && searchQuery.trim().length >= 2 && (
                          <li className="deck-share-search-item muted">
                            {t("decks.share.no_users_found")}
                          </li>
                        )}
                        {searchResults.map((user) => (
                          <li key={user.id}>
                            <button
                              type="button"
                              className="deck-share-search-item"
                              onClick={() => handleSelectUser(user)}
                            >
                              {user.username}
                            </button>
                          </li>
                        ))}
                      </ul>
                    )}
                  </div>

                  <select
                    className="deck-share-role-select"
                    value={inviteRole}
                    onChange={(e) => setInviteRole(e.target.value)}
                  >
                    {ROLES.map((role) => (
                      <option key={role} value={role}>
                        {t(`decks.share.role_${role}`)}
                      </option>
                    ))}
                  </select>

                  <Button
                    type="button"
                    color="blue"
                    onClick={handleInvite}
                    disabled={inviting || !inviteUsername.trim()}
                    isLoading={inviting}
                  >
                    {t("decks.share.invite")}
                  </Button>
                </div>

                {collaborators.length > 0 ? (
                  <ul className="deck-share-member-list">
                    {collaborators.map((member) => (
                      <li key={member.user_id} className="deck-share-member-item">
                        <div className="deck-share-member-info">
                          <span className="deck-share-member-name">
                            {member.username}
                          </span>
                          <span className="deck-share-member-role">
                            {t(`decks.share.role_${member.role}`)}
                          </span>
                        </div>
                        <button
                          type="button"
                          className="deck-share-remove-btn"
                          onClick={() => handleRemoveCollaborator(member.user_id)}
                          disabled={removingUserId === member.user_id}
                          aria-label={t("decks.share.remove_member")}
                        >
                          {removingUserId === member.user_id ? "…" : "×"}
                        </button>
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="deck-share-empty-members">
                    {t("decks.share.no_members")}
                  </p>
                )}
              </div>
            )}

            {error && <p className="deck-modal-error">{error}</p>}

            <div className="deck-modal-actions">
              <Button
                type="button"
                variant="outline"
                color="red"
                onClick={onClose}
                disabled={saving}
              >
                {t("common.cancel")}
              </Button>
              <Button
                type="button"
                color="blue"
                onClick={handleSave}
                disabled={saving}
                isLoading={saving}
              >
                {t("common.save")}
              </Button>
            </div>
          </>
        )}
      </div>
    </div>
  );
};

export default ShareDeckModal;
