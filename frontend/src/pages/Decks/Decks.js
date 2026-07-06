import React, { useEffect, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useTranslation } from "react-i18next";
import api from "../../api/api";
import { getApiErrorCode, mapApiError } from "../../utils/errorMapper";
import DeckLeft from "./components/DeckLeft";
import DeckRight from "./components/DeckRight";
import CreateDeck from "./components/CreateDeck";
import EditDeck from "./components/EditDeck";
import ShareDeckModal from "./components/ShareDeckModal";
import "./Decks.css";

const buildDeckTree = (items) => {
  const byId = new Map();
  const roots = [];

  items.forEach((item) => byId.set(item.id, { ...item, children: [] }));
  items.forEach((item) => {
    const node = byId.get(item.id);
    if (item.parent_id && byId.has(item.parent_id)) {
      byId.get(item.parent_id).children.push(node);
    } else {
      roots.push(node);
    }
  });

  return roots;
};

const Decks = () => {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const [decks, setDecks] = useState([]);
  const [searchText, setSearchText] = useState("");

  const [showCreateModal, setShowCreateModal] = useState(false);
  const [newDeck, setNewDeck] = useState({ name: "", description: "" });
  const [createError, setCreateError] = useState("");

  const [expandedIds, setExpandedIds] = useState(() => new Set());
  const [draggingDeckId, setDraggingDeckId] = useState(null);
  const [dropTargetId, setDropTargetId] = useState(null);
  const [moveError, setMoveError] = useState("");
  const [selectedDeckId, setSelectedDeckId] = useState(null);
  const [selectedDeckInfo, setSelectedDeckInfo] = useState(null);
  const [statsLoading, setStatsLoading] = useState(false);
  const [statsError, setStatsError] = useState("");
  const [showEditModal, setShowEditModal] = useState(false);
  const [editDeck, setEditDeck] = useState({ name: "", description: "" });
  const [editError, setEditError] = useState("");
  const [isEditing, setIsEditing] = useState(false);
  const [deletingDeck, setDeletingDeck] = useState(false);
  const [showShareModal, setShowShareModal] = useState(false);
  const [unlearningDeck, setUnlearningDeck] = useState(false);

  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [isCreating, setIsCreating] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    if (!token) {
      navigate("/login");
      return;
    }

    const fetchDecks = async () => {
      try {
        setLoading(true);
        setError("");
        const res = await api.get("/api/decks/");
        setDecks(res.data?.results || []);
      } catch (err) {
        if (err.response?.status === 401) {
          localStorage.removeItem("access_token");
          navigate("/login");
          return;
        }
        setError(t("decks.error_load"));
      } finally {
        setLoading(false);
      }
    };

    fetchDecks();
  }, []);

  const filteredDecks = useMemo(() => {
    const keyword = searchText.trim().toLowerCase();
    if (!keyword) {
      return decks;
    }

    return decks.filter((deck) => {
      const name = (deck.name || "").toLowerCase();
      const description = (deck.description || "").toLowerCase();
      return name.includes(keyword) || description.includes(keyword);
    });
  }, [decks, searchText]);

  const treeDecks = useMemo(
    () => buildDeckTree(filteredDecks),
    [filteredDecks],
  );

  const toggleExpanded = (deckId) => {
    setExpandedIds((prev) => {
      const next = new Set(prev);
      if (next.has(deckId)) {
        next.delete(deckId);
      } else {
        next.add(deckId);
      }
      return next;
    });
  };

  const handleOpenCreateModal = () => {
    setCreateError("");
    setNewDeck({ name: "", description: "" });
    setShowCreateModal(true);
  };

  const handleCloseCreateModal = () => {
    if (isCreating) {
      return;
    }
    setShowCreateModal(false);
    setCreateError("");
  };

  const handleCreateDeck = async (e) => {
    e.preventDefault();
    const payload = {
      name: newDeck.name.trim(),
      description: newDeck.description.trim(),
    };

    if (!payload.name) {
      setCreateError(t("decks.error_name_required"));
      return;
    }

    if (payload.name.length > 100) {
      setCreateError(t("decks.error_name_max"));
      return;
    }

    try {
      setIsCreating(true);
      setCreateError("");
      const res = await api.post("/api/decks/", payload);
      setDecks((prev) => [res.data, ...prev]);
      setShowCreateModal(false);
      setNewDeck({ name: "", description: "" });
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setCreateError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_create")
          : t("decks.error_create"),
      );
    } finally {
      setIsCreating(false);
    }
  };

  const handleOpenEditModal = () => {
    if (!selectedDeckId) {
      return;
    }
    const deckInList = decks.find((deck) => deck.id === selectedDeckId);
    setEditDeck({
      name: selectedDeckInfo?.name || deckInList?.name || "",
      description:
        selectedDeckInfo?.description || deckInList?.description || "",
    });
    setEditError("");
    setShowEditModal(true);
  };

  const handleCloseEditModal = () => {
    if (isEditing) {
      return;
    }
    setShowEditModal(false);
    setEditError("");
  };

  const handleEditDeck = async (e) => {
    e.preventDefault();
    if (!selectedDeckId) {
      setEditError(t("decks.error_no_deck_selected"));
      return;
    }

    const payload = {
      name: editDeck.name.trim(),
      description: editDeck.description.trim(),
    };

    if (!payload.name) {
      setEditError(t("decks.error_name_required"));
      return;
    }
    if (payload.name.length > 100) {
      setEditError(t("decks.error_name_max"));
      return;
    }

    try {
      setIsEditing(true);
      setEditError("");
      const res = await api.put(`/api/decks/${selectedDeckId}/`, payload);
      const updatedDeck = res.data;

      setDecks((prev) =>
        prev.map((deck) =>
          deck.id === selectedDeckId
            ? {
                ...deck,
                name: updatedDeck?.name ?? payload.name,
                description: updatedDeck?.description ?? payload.description,
              }
            : deck,
        ),
      );

      setSelectedDeckInfo((prev) =>
        prev
          ? {
              ...prev,
              name: updatedDeck?.name ?? payload.name,
              description: updatedDeck?.description ?? payload.description,
            }
          : prev,
      );
      setShowEditModal(false);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setEditError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_update")
          : t("decks.error_update"),
      );
    } finally {
      setIsEditing(false);
    }
  };

  const handleDragStart = (e, deckId) => {
    e.dataTransfer.setData("text/plain", "");
    e.dataTransfer.effectAllowed = "move";
    setDraggingDeckId(deckId);
    setMoveError("");
  };

  const handleDragEnd = () => {
    setDraggingDeckId(null);
    setDropTargetId(null);
  };

  const handleDropOnDeck = async (targetDeckId) => {
    if (!draggingDeckId || draggingDeckId === targetDeckId) {
      setMoveError(t("decks.error_move_same"));
      return;
    }

    try {
      setMoveError("");
      await api.post("/api/decks/move/", {
        deck_id: draggingDeckId,
        parent_id: targetDeckId,
      });

      setDecks((prev) =>
        prev.map((deck) =>
          deck.id === draggingDeckId
            ? { ...deck, parent_id: targetDeckId }
            : deck,
        ),
      );
      setExpandedIds((prev) => new Set(prev).add(targetDeckId));
    } catch (err) {
      setMoveError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_move")
          : t("decks.error_move"),
      );
    } finally {
      setDraggingDeckId(null);
      setDropTargetId(null);
    }
  };

  const handleDropToRoot = async () => {
    if (!draggingDeckId) {
      return;
    }

    try {
      setMoveError("");
      await api.post("/api/decks/move/", {
        deck_id: draggingDeckId,
        parent_id: null,
      });

      setDecks((prev) =>
        prev.map((deck) =>
          deck.id === draggingDeckId ? { ...deck, parent_id: null } : deck,
        ),
      );
    } catch (err) {
      setMoveError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_move")
          : t("decks.error_move"),
      );
    } finally {
      setDraggingDeckId(null);
      setDropTargetId(null);
    }
  };

  const isInsideDeckRow = (target) => {
    return Boolean(target?.closest && target.closest(".deck-tree-row"));
  };

  const handleSelectDeck = async (deckId) => {
    setStatsError("");
    setStatsLoading(true);
    try {
      const res = await api.get(`/api/decks/${deckId}/`);
      setSelectedDeckId(deckId);
      setSelectedDeckInfo(res.data);
    } catch (err) {
      setSelectedDeckId(null);
      setSelectedDeckInfo(null);
      setStatsError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_stats")
          : t("decks.error_stats"),
      );
    } finally {
      setStatsLoading(false);
    }
  };

  const handleDeleteDeck = async () => {
    if (!window.confirm(t("decks.confirm_delete"))) {
      return;
    }
    try {
      setDeletingDeck(true);
      await api.delete(`/api/decks/${selectedDeckId}/`);
      const res = await api.get("/api/decks/");
      setDecks(res.data?.results || []);
      setSelectedDeckId(null);
      setSelectedDeckInfo(null);
      setStatsError("");
    } catch (err) {
      setStatsError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_delete")
          : t("decks.error_delete"),
      );
    } finally {
      setDeletingDeck(false);
    }
  };

  const handleStopLearning = async () => {
    if (!selectedDeckId || selectedDeckInfo?.role !== "viewer") {
      return;
    }
    if (!window.confirm(t("decks.confirm_stop_learning"))) {
      return;
    }

    try {
      setUnlearningDeck(true);
      setStatsError("");
      await api.post(`/api/decks/${selectedDeckId}/unlearn/`);
      const res = await api.get("/api/decks/");
      setDecks(res.data?.results || []);
      setSelectedDeckId(null);
      setSelectedDeckInfo(null);
    } catch (err) {
      if (err.response?.status === 401) {
        localStorage.removeItem("access_token");
        navigate("/login");
        return;
      }
      setStatsError(
        getApiErrorCode(err.response?.data)
          ? mapApiError(getApiErrorCode(err.response?.data), t, "decks.error_stop_learning")
          : t("decks.error_stop_learning"),
      );
    } finally {
      setUnlearningDeck(false);
    }
  };

  const handleOpenShareModal = () => {
    if (!selectedDeckId) {
      return;
    }
    setShowShareModal(true);
  };

  const handleCloseShareModal = () => {
    setShowShareModal(false);
  };

  const handleShareSettingsSaved = (shareData) => {
    if (!selectedDeckId || !shareData) {
      return;
    }

    setDecks((prev) =>
      prev.map((deck) =>
        deck.id === selectedDeckId
          ? {
              ...deck,
              coin_price: shareData.coin_price || 0,
              share_mode: shareData.share_mode,
            }
          : deck,
      ),
    );
    setSelectedDeckInfo((prev) =>
      prev
        ? {
            ...prev,
            coin_price: shareData.coin_price || 0,
            share_mode: shareData.share_mode,
          }
        : prev,
    );
  };

  return (
    <div
      className="decks-page"
      onDragOver={(e) => {
        if (!draggingDeckId) {
          return;
        }
        if (!isInsideDeckRow(e.target)) {
          e.preventDefault();
          e.dataTransfer.dropEffect = "move";
          setDropTargetId("root");
        }
      }}
      onDrop={(e) => {
        if (!draggingDeckId) {
          return;
        }
        if (!isInsideDeckRow(e.target)) {
          e.preventDefault();
          handleDropToRoot();
        }
      }}
    >
      <div className="decks-layout">
        <DeckLeft
          searchText={searchText}
          setSearchText={setSearchText}
          handleOpenCreateModal={handleOpenCreateModal}
          loading={loading}
          error={error}
          moveError={moveError}
          treeDecks={treeDecks}
          expandedIds={expandedIds}
          toggleExpanded={toggleExpanded}
          dropTargetId={dropTargetId}
          setDropTargetId={setDropTargetId}
          draggingDeckId={draggingDeckId}
          handleDragStart={handleDragStart}
          handleDragEnd={handleDragEnd}
          handleDropOnDeck={handleDropOnDeck}
          selectedDeckId={selectedDeckId}
          handleSelectDeck={handleSelectDeck}
        />
        <DeckRight
          selectedDeckId={selectedDeckId}
          selectedDeckInfo={selectedDeckInfo}
          statsLoading={statsLoading}
          statsError={statsError}
          handleOpenEditModal={handleOpenEditModal}
          deletingDeck={deletingDeck}
          handleDeleteDeck={handleDeleteDeck}
          onOpenShareModal={handleOpenShareModal}
          unlearningDeck={unlearningDeck}
          handleStopLearning={handleStopLearning}
        />
      </div>

      {showCreateModal && (
        <CreateDeck
          handleCloseCreateModal={handleCloseCreateModal}
          handleCreateDeck={handleCreateDeck}
          newDeck={newDeck}
          setNewDeck={setNewDeck}
          createError={createError}
          isCreating={isCreating}
        />
      )}
      {showEditModal && (
        <EditDeck
          handleCloseEditModal={handleCloseEditModal}
          handleEditDeck={handleEditDeck}
          editDeck={editDeck}
          setEditDeck={setEditDeck}
          editError={editError}
          isEditing={isEditing}
        />
      )}
      {showShareModal && selectedDeckId && selectedDeckInfo && (
        <ShareDeckModal
          deckId={selectedDeckId}
          deckName={selectedDeckInfo.name}
          onClose={handleCloseShareModal}
          onSaved={handleShareSettingsSaved}
        />
      )}
    </div>
  );
};

export default Decks;
