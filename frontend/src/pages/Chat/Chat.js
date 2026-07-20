import React, {
  useCallback,
  useContext,
  useEffect,
  useRef,
  useState,
  useMemo,
} from "react";
import { useTranslation } from "react-i18next";
import { useNavigate } from "react-router-dom";
import toast from "react-hot-toast";
import api from "../../api/api";
import chatApi, {
  getChatWebSocketUrl,
  refreshAccessToken,
} from "../../api/chatApi";
import { AuthContext } from "../../context/AuthContext";
import "./Chat.css";

function formatTime(isoString) {
  if (!isoString) return "";

  const date = new Date(isoString);
  const today = new Date();

  const isToday =
    date.getFullYear() === today.getFullYear() &&
    date.getMonth() === today.getMonth() &&
    date.getDate() === today.getDate();

  if (isToday) {
    return date.toLocaleTimeString([], {
      hour: "2-digit",
      minute: "2-digit",
    });
  }

  return date.toLocaleDateString("vi-VN", {
    day: "2-digit",
    month: "2-digit",
    year: "numeric",
  });
}

function displayName(user) {
  if (!user) return "";
  const fullName = `${user.first_name || ""} ${user.last_name || ""}`.trim();
  return fullName || user.username;
}

function conversationTitle(conversation, t) {
  if (!conversation) return "";
  return conversation.name || t("chat.unknown_user");
}

function messageTypeLabel(type) {
  switch (type) {
    case "image":
      return "Ảnh";
    case "video":
      return "Video";
    case "audio":
      return "Audio";
    case "file":
      return "File";
    default:
      return "";
  }
}

function conversationPreview(conversation, currentUserId) {
  if (!conversation) return "";

  if (conversation.is_deleted) {
    return "Đã xóa tin nhắn";
  }

  const hasReply = Boolean(conversation.reply_to_message_id);
  const content = (conversation.content || "").trim();
  const typeLabel = messageTypeLabel(conversation.message_type);

  if (hasReply) {
    return "Đã trả lời tin nhắn";
  }

  let preview = content;
  if (!preview && typeLabel) {
    preview = `[${typeLabel}]`;
  }

  if (!preview) return "";

  if (conversation.sender_id === currentUserId) {
    return `Bạn: ${preview}`;
  }

  return preview;
}

function messagePreviewText(message) {
  if (!message) return "";
  if (message.is_deleted) return "Người dùng đã xóa tin nhắn này";
  const content = (message.content || "").trim();
  if (content) return content;
  const typeLabel = messageTypeLabel(message.type);
  if (typeLabel) return `[${typeLabel}]`;
  const firstFile = message.attachments?.[0]?.file_name;
  return firstFile || "";
}

function formatFileSize(bytes) {
  if (!bytes && bytes !== 0) return "";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function isImageAttachment(attachment) {
  const mime = (attachment?.mime_type || "").toLowerCase();
  if (mime.startsWith("image/")) return true;
  return /\.(png|jpe?g|gif|webp|bmp|svg)$/i.test(attachment?.file_name || "");
}

function isVideoAttachment(attachment) {
  const mime = (attachment?.mime_type || "").toLowerCase();
  if (mime.startsWith("video/")) return true;
  return /\.(mp4|webm|ogg|mov|m4v)$/i.test(attachment?.file_name || "");
}

function isAudioAttachment(attachment) {
  const mime = (attachment?.mime_type || "").toLowerCase();
  if (mime.startsWith("audio/")) return true;
  return /\.(mp3|wav|ogg|m4a|aac)$/i.test(attachment?.file_name || "");
}

function formatDateTime(isoString) {
  if (!isoString) return "";
  const date = new Date(isoString);
  return date.toLocaleString();
}

function Chat() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { currentUser } = useContext(AuthContext);

  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [participants, setParticipants] = useState([]);
  const [conversationDetail, setConversationDetail] = useState(null);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [hasMoreMessages, setHasMoreMessages] = useState(false);
  const [loadingMoreMessages, setLoadingMoreMessages] = useState(false);
  const shouldScrollToBottomRef = useRef(true);
  const [messageInput, setMessageInput] = useState("");
  const [pendingFiles, setPendingFiles] = useState([]);
  const [sendingMessage, setSendingMessage] = useState(false);
  const fileInputRef = useRef(null);
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);
  const [groupName, setGroupName] = useState("");
  const [selectedGroupUsers, setSelectedGroupUsers] = useState([]);
  const [isCreateGroupModalOpen, setIsCreateGroupModalOpen] = useState(false);
  const [modalSearchQuery, setModalSearchQuery] = useState("");
  const [modalSearchResults, setModalSearchResults] = useState([]);
  const [modalSearching, setModalSearching] = useState(false);
  const [creatingGroup, setCreatingGroup] = useState(false);
  const [replyTarget, setReplyTarget] = useState(null);
  const [editTarget, setEditTarget] = useState(null);
  const [openActionsForMessageId, setOpenActionsForMessageId] = useState(null);
  const [isConversationMenuOpen, setIsConversationMenuOpen] = useState(false);
  const [isConversationInfoOpen, setIsConversationInfoOpen] = useState(false);
  const [renameValue, setRenameValue] = useState("");
  const [memberSearchQuery, setMemberSearchQuery] = useState("");
  const [memberSearchResults, setMemberSearchResults] = useState([]);
  const [memberSearching, setMemberSearching] = useState(false);
  const [isUploadingConversationAvatar, setIsUploadingConversationAvatar] =
    useState(false);
  const memberSearchTimeoutRef = useRef(null);
  const conversationAvatarInputRef = useRef(null);

  const isCurrentUserAdmin = useMemo(() => {
    const list = conversationDetail?.participants || [];
    return list.some(
      (p) => p.user_id === currentUser?.id && Boolean(p.is_admin),
    );
  }, [conversationDetail, currentUser]);

  const watermarksMap = useMemo(() => {
    const map = {};
    participants.forEach((p) => {
      if (p.user_id === currentUser?.id) return;
      if (!p.last_read_message_id) return;

      let effectiveMsgId = null;
      for (let i = messages.length - 1; i >= 0; i--) {
        const m = messages[i];
        if (m.id <= p.last_read_message_id && m.sender_id !== p.user_id) {
          effectiveMsgId = m.id;
          break;
        }
      }

      if (effectiveMsgId) {
        if (!map[effectiveMsgId]) map[effectiveMsgId] = [];
        map[effectiveMsgId].push(p);
      }
    });
    return map;
  }, [participants, messages, currentUser?.id]);

  const wsRef = useRef(null);
  const wsReconnectAttemptRef = useRef(0);
  const messagesContainerRef = useRef(null);
  const searchTimeoutRef = useRef(null);
  const modalSearchTimeoutRef = useRef(null);
  const activeConversationIdRef = useRef(null);

  const fetchConversations = useCallback(async () => {
    try {
      setLoadingConversations(true);
      const res = await chatApi.get("/conversations");
      const sortedResults = [...(res.data.results || [])].sort((a, b) => {
        const aTime = a.message_created_at
          ? new Date(a.message_created_at).getTime()
          : 0;
        const bTime = b.message_created_at
          ? new Date(b.message_created_at).getTime()
          : 0;
        return bTime - aTime;
      });
      setConversations(sortedResults);
    } catch (err) {
      console.error(err);
      toast.error(t("chat.load_conversations_error"));
    } finally {
      setLoadingConversations(false);
    }
  }, [t]);

  const connectWebSocket = useCallback(
    (userId, isReconnect = false) => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }

      if (!isReconnect) wsReconnectAttemptRef.current = 0;

      const ws = new WebSocket(getChatWebSocketUrl(userId));
      wsRef.current = ws;

      ws.onmessage = (event) => {
        try {
          const payload = JSON.parse(event.data);
          if (payload.type === "message" && payload.data) {
            fetchConversations();
            if (
              payload.data.conversation_id === activeConversationIdRef.current
            ) {
              shouldScrollToBottomRef.current = true;
              setMessages((prev) => {
                if (prev.some((m) => m.id === payload.data.id)) return prev;
                return [...prev, payload.data];
              });
            }
            return;
          }

          if (payload.type === "message_update" && payload.data) {
            fetchConversations();
            if (
              payload.data.conversation_id === activeConversationIdRef.current
            ) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === payload.data.id
                    ? { ...msg, ...payload.data }
                    : msg,
                ),
              );
            }
            return;
          }

          if (payload.type === "read_update" && payload.data) {
            if (
              payload.data.conversation_id === activeConversationIdRef.current
            ) {
              setMessages((prev) =>
                prev.map((msg) =>
                  msg.id === payload.data.message_id
                    ? {
                        ...msg,
                        seen_by_ids: payload.data.seen_by_ids || [],
                        seen_count: (payload.data.seen_by_ids || []).filter(id => id !== currentUser?.id).length,
                      }
                    : msg,
                ),
              );
              setParticipants((prev) =>
                prev.map((p) =>
                  (payload.data.seen_by_ids || []).includes(p.user_id)
                    ? {
                        ...p,
                        last_read_message_id: Math.max(
                          p.last_read_message_id || 0,
                          payload.data.message_id
                        ),
                      }
                    : p
                )
              );
            }
            return;
          }

          if (payload.type === "conversation_update" && payload.data) {
            fetchConversations();
            if (payload.data.id === activeConversationIdRef.current) {
              setConversationDetail(payload.data);
              setParticipants(payload.data.participants || []);
              setRenameValue(payload.data.name || "");
              setActiveConversation((prev) =>
                prev
                  ? {
                      ...prev,
                      name: payload.data.name,
                      avatar: payload.data.avatar,
                    }
                  : prev,
              );
              setConversations((prev) =>
                prev.map((conv) =>
                  conv.id === payload.data.id
                    ? {
                        ...conv,
                        name: payload.data.name,
                        avatar: payload.data.avatar,
                      }
                    : conv,
                ),
              );
            }
            return;
          }
        } catch (e) {
          console.error(e);
        }
      };

      ws.onerror = () => {
        toast.error(t("chat.connection_error"));
      };

      ws.onclose = async (event) => {
        // Backend close code 4001 khi JWT hết hạn/invalid
        if (
          event.code === 4001 &&
          wsReconnectAttemptRef.current < 1 &&
          currentUser?.id === userId
        ) {
          wsReconnectAttemptRef.current += 1;
          try {
            await refreshAccessToken();
            connectWebSocket(userId, true);

            return;
          } catch (e) {
            localStorage.clear();
            navigate("/login");
            return;
          }
        }
      };
    },
    [t, navigate, currentUser],
  );

  useEffect(() => {
    activeConversationIdRef.current = activeConversation?.id ?? null;
  }, [activeConversation]);

  const openConversation = useCallback(
    async (conversation) => {
      setActiveConversation(conversation);
      setReplyTarget(null);
      setEditTarget(null);
      setPendingFiles([]);
      setMessageInput("");
      setOpenActionsForMessageId(null);
      setIsConversationMenuOpen(false);
      setIsConversationInfoOpen(false);
      setMemberSearchQuery("");
      setMemberSearchResults([]);
      setLoadingMessages(true);

      try {
        const res = await chatApi.get(
          `/conversations/${conversation.id}/messages`,
        );
        const fetchedParticipants = res.data.participants || [];
        const fetchedMessages = (res.data.results || []).map((msg) => {
          const readers = fetchedParticipants
            .filter((p) => p.last_read_message_id && p.last_read_message_id >= msg.id)
            .map((p) => p.user_id);
          return {
            ...msg,
            seen_by_ids: readers,
            seen_count: readers.filter((id) => id !== currentUser?.id).length,
          };
        });
        
        shouldScrollToBottomRef.current = true;
        setMessages(fetchedMessages);
        setHasMoreMessages(res.data.has_more || false);
        setParticipants(fetchedParticipants);
        const detailRes = await chatApi.get(
          `/conversations/${conversation.id}`,
        );
        setConversationDetail(detailRes.data);
        setRenameValue(detailRes.data?.name || "");
        if (detailRes.data?.avatar) {
          setActiveConversation((prev) =>
            prev && prev.id === conversation.id
              ? { ...prev, avatar: detailRes.data.avatar }
              : prev,
          );
          setConversations((prev) =>
            prev.map((conv) =>
              conv.id === conversation.id
                ? { ...conv, avatar: detailRes.data.avatar }
                : conv,
            ),
          );
        }
        const readRes = await chatApi.post(
          `/conversations/${conversation.id}/read`,
        );
        if (readRes.data?.last_read_message_id) {
          setMessages((prev) =>
            prev.map((msg) =>
              msg.id === readRes.data.last_read_message_id
                ? {
                    ...msg,
                    seen_by_ids: readRes.data.seen_by_ids || [],
                    seen_count: (readRes.data.seen_by_ids || []).filter(id => id !== currentUser?.id).length,
                  }
                : msg,
            ),
          );
          setParticipants((prev) =>
            prev.map((p) =>
              p.user_id === currentUser?.id
                ? { ...p, last_read_message_id: readRes.data.last_read_message_id }
                : p
            )
          );
        }
        fetchConversations();
      } catch (err) {
        console.error(err);
        toast.error(t("chat.load_messages_error"));
      } finally {
        setLoadingMessages(false);
      }
    },
    [fetchConversations, t],
  );

  const loadMoreMessages = async () => {
    if (!activeConversation || loadingMoreMessages || !hasMoreMessages) return;
    if (messages.length === 0) return;

    try {
      setLoadingMoreMessages(true);
      const firstMessageId = messages[0].id;
      const res = await chatApi.get(
        `/conversations/${activeConversation.id}/messages`,
        { params: { before_id: firstMessageId, limit: 20 } },
      );

      const newMessages = res.data.results || [];
      if (newMessages.length > 0) {
        shouldScrollToBottomRef.current = false;
        const container = messagesContainerRef.current;
        const previousScrollHeight = container ? container.scrollHeight : 0;

        const enrichedNewMessages = newMessages.map((msg) => {
          const readers = participants
            .filter((p) => p.last_read_message_id && p.last_read_message_id >= msg.id)
            .map((p) => p.user_id);
          return {
            ...msg,
            seen_by_ids: readers,
            seen_count: readers.filter((id) => id !== currentUser?.id).length,
          };
        });

        setMessages((prev) => [...enrichedNewMessages, ...prev]);
        setHasMoreMessages(res.data.has_more || false);

        if (container) {
          setTimeout(() => {
            container.scrollTop = container.scrollHeight - previousScrollHeight;
          }, 0);
        }
      } else {
        setHasMoreMessages(false);
      }
    } catch (err) {
      console.error(err);
      toast.error(t("chat.load_messages_error"));
    } finally {
      setLoadingMoreMessages(false);
    }
  };

  const startConversation = async (user) => {
    try {
      const res = await chatApi.post("/conversations", {
        other_user_id: user.id,
      });
      setSearchQuery("");
      setSearchResults([]);
      await fetchConversations();
      openConversation(res.data);
    } catch (err) {
      console.error(err);
      toast.error(t("chat.start_conversation_error"));
    }
  };

  const toggleGroupUser = (user) => {
    setSelectedGroupUsers((prev) => {
      const exists = prev.some((item) => item.id === user.id);
      if (exists) return prev.filter((item) => item.id !== user.id);
      return [...prev, user];
    });
  };

  const resetCreateGroupModalState = () => {
    setGroupName("");
    setSelectedGroupUsers([]);
    setModalSearchQuery("");
    setModalSearchResults([]);
    setModalSearching(false);
    setCreatingGroup(false);

    if (modalSearchTimeoutRef.current) {
      clearTimeout(modalSearchTimeoutRef.current);
      modalSearchTimeoutRef.current = null;
    }
  };

  const openCreateGroupModal = () => {
    resetCreateGroupModalState();
    setIsCreateGroupModalOpen(true);
  };

  const closeCreateGroupModal = () => {
    setIsCreateGroupModalOpen(false);
    resetCreateGroupModalState();
  };

  const createGroupConversation = async () => {
    const trimmedName = groupName.trim();
    if (!trimmedName) {
      toast.error(t("chat.group_name_required"));
      return;
    }
    if (selectedGroupUsers.length < 2) {
      toast.error(t("chat.group_members_required"));
      return;
    }

    try {
      setCreatingGroup(true);
      const res = await chatApi.post("/conversations/group", {
        name: trimmedName,
        participant_ids: selectedGroupUsers.map((u) => u.id),
      });
      setGroupName("");
      setSelectedGroupUsers([]);
      setModalSearchQuery("");
      setModalSearchResults([]);
      setIsCreateGroupModalOpen(false);
      setCreatingGroup(false);
      await fetchConversations();
      openConversation(res.data);
    } catch (err) {
      console.error(err);
      toast.error(t("chat.group_create_error"));
      setCreatingGroup(false);
    }
  };

  const handleInputFocus = async () => {
    if (!activeConversation) return;
    try {
      const readRes = await chatApi.post(
        `/conversations/${activeConversation.id}/read`,
      );
      if (readRes.data?.last_read_message_id) {
        setMessages((prev) =>
          prev.map((msg) =>
            msg.id === readRes.data.last_read_message_id
              ? {
                  ...msg,
                  seen_by_ids: readRes.data.seen_by_ids || [],
                  seen_count: (readRes.data.seen_by_ids || []).filter(id => id !== currentUser?.id).length,
                }
              : msg,
          ),
        );
        setParticipants((prev) =>
          prev.map((p) =>
            p.user_id === currentUser?.id
              ? { ...p, last_read_message_id: readRes.data.last_read_message_id }
              : p
          )
        );
      }
    } catch (err) {
      console.error(err);
    }
  };

  const handleSelectFiles = (e) => {
    const selected = Array.from(e.target.files || []);
    if (selected.length === 0) return;

    setPendingFiles((prev) => {
      const existingKeys = new Set(
        prev.map((f) => `${f.name}-${f.size}-${f.lastModified}`),
      );
      const next = [...prev];
      selected.forEach((file) => {
        const key = `${file.name}-${file.size}-${file.lastModified}`;
        if (!existingKeys.has(key)) next.push(file);
      });
      return next;
    });

    // Cho phép chọn lại cùng file
    e.target.value = "";
  };

  const removePendingFile = (index) => {
    setPendingFiles((prev) => prev.filter((_, i) => i !== index));
  };

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const content = messageInput.trim();
    if (!activeConversation || sendingMessage) return;

    if (editTarget) {
      if (!content) return;
      try {
        setSendingMessage(true);
        const res = await chatApi.patch(
          `/conversations/${activeConversation.id}/messages/${editTarget.id}`,
          { content },
        );
        setMessages((prev) =>
          prev.map((item) =>
            item.id === editTarget.id ? { ...item, ...res.data } : item,
          ),
        );
        setEditTarget(null);
        setMessageInput("");
        fetchConversations();
      } catch (err) {
        console.error(err);
        toast.error("Không thể sửa tin nhắn");
      } finally {
        setSendingMessage(false);
      }
      return;
    }

    if (!content && pendingFiles.length === 0) return;

    const replyToMessageId = replyTarget?.id || null;
    const filesToSend = [...pendingFiles];
    const previousInput = content;

    setMessageInput("");
    setPendingFiles([]);
    setSendingMessage(true);

    try {
      if (filesToSend.length > 0) {
        const formData = new FormData();
        if (content) formData.append("content", content);
        if (replyToMessageId != null) {
          formData.append("reply_to_message_id", String(replyToMessageId));
        }
        filesToSend.forEach((file) => formData.append("files", file));

        await chatApi.post(
          `/conversations/${activeConversation.id}/messages`,
          formData,
          {
            // Để browser tự set boundary cho multipart
            transformRequest: [
              (data, headers) => {
                if (headers && typeof headers.delete === "function") {
                  headers.delete("Content-Type");
                } else if (headers) {
                  delete headers["Content-Type"];
                }
                return data;
              },
            ],
          },
        );
      } else {
        await chatApi.post(
          `/conversations/${activeConversation.id}/messages`,
          {
            content,
            reply_to_message_id: replyToMessageId,
          },
        );
      }
      setReplyTarget(null);
    } catch (err) {
      console.error(err);
      toast.error(t("chat.send_error"));
      setMessageInput(previousInput);
      setPendingFiles(filesToSend);
    } finally {
      setSendingMessage(false);
    }
  };

  const handleReplyMessage = (msg) => {
    setReplyTarget(msg);
    setEditTarget(null);
    setOpenActionsForMessageId(null);
  };

  const handleEditMessage = (msg) => {
    setEditTarget(msg);
    setMessageInput(msg.content || "");
    setPendingFiles([]);
    setReplyTarget(null);
    setOpenActionsForMessageId(null);
  };

  const handleDeleteMessage = async (msg) => {
    if (!activeConversation) return;
    try {
      const res = await chatApi.delete(
        `/conversations/${activeConversation.id}/messages/${msg.id}`,
      );
      setMessages((prev) =>
        prev.map((item) =>
          item.id === msg.id ? { ...item, ...res.data } : item,
        ),
      );
      setOpenActionsForMessageId(null);
      fetchConversations();
    } catch (err) {
      console.error(err);
      toast.error("Không thể xóa tin nhắn");
    }
  };

  const participantByUserId = useCallback(
    (userId) => participants.find((p) => p.user_id === userId),
    [participants],
  );

  const applyConversationAvatar = useCallback((conversationId, avatarUrl) => {
    setActiveConversation((prev) =>
      prev && prev.id === conversationId ? { ...prev, avatar: avatarUrl } : prev,
    );
    setConversationDetail((prev) =>
      prev && prev.id === conversationId ? { ...prev, avatar: avatarUrl } : prev,
    );
    setConversations((prev) =>
      prev.map((conv) =>
        conv.id === conversationId ? { ...conv, avatar: avatarUrl } : conv,
      ),
    );
  }, []);

  const handleConversationAvatarClick = () => {
    if (isUploadingConversationAvatar) return;
    conversationAvatarInputRef.current?.click();
  };

  const handleConversationAvatarChange = async (e) => {
    const file = e.target.files?.[0];
    e.target.value = "";
    if (!file || !activeConversation) return;

    if (!file.type.startsWith("image/")) {
      toast.error(t("chat.conversation_avatar_type_error"));
      return;
    }

    try {
      setIsUploadingConversationAvatar(true);
      const formData = new FormData();
      formData.append("avatar", file);

      const res = await chatApi.post(
        `/conversations/${activeConversation.id}/avatar`,
        formData,
        {
          transformRequest: [
            (data, headers) => {
              if (headers && typeof headers.delete === "function") {
                headers.delete("Content-Type");
              } else if (headers) {
                delete headers["Content-Type"];
              }
              return data;
            },
          ],
        },
      );

      const avatarUrl = res.data?.avatar;
      if (!avatarUrl) {
        toast.error(t("chat.conversation_avatar_upload_error"));
        return;
      }

      applyConversationAvatar(activeConversation.id, avatarUrl);
      toast.success(t("chat.conversation_avatar_upload_success"));
    } catch (err) {
      console.error(err);
      toast.error(t("chat.conversation_avatar_upload_error"));
    } finally {
      setIsUploadingConversationAvatar(false);
    }
  };

  const handleUpdateConversationName = async () => {
    if (!activeConversation || !renameValue.trim()) return;
    try {
      const res = await chatApi.patch(
        `/conversations/${activeConversation.id}`,
        {
          name: renameValue.trim(),
        },
      );
      setActiveConversation((prev) =>
        prev
          ? { ...prev, name: res.data.name, avatar: res.data.avatar ?? prev.avatar }
          : prev,
      );
      setConversationDetail((prev) =>
        prev
          ? { ...prev, name: res.data.name, avatar: res.data.avatar ?? prev.avatar }
          : prev,
      );
      setConversations((prev) =>
        prev.map((conv) =>
          conv.id === activeConversation.id
            ? {
                ...conv,
                name: res.data.name,
                avatar: res.data.avatar ?? conv.avatar,
              }
            : conv,
        ),
      );
      setIsConversationMenuOpen(false);
      toast.success("Đã đổi tên đoạn chat");
    } catch (err) {
      console.error(err);
      toast.error("Không thể đổi tên đoạn chat");
    }
  };

  const handleLeaveGroup = async () => {
    if (!activeConversation) return;
    try {
      await chatApi.post(`/conversations/${activeConversation.id}/leave`);
      setActiveConversation(null);
      setConversationDetail(null);
      setMessages([]);
      setParticipants([]);
      setIsConversationInfoOpen(false);
      setIsConversationMenuOpen(false);
      await fetchConversations();
      toast.success("Đã rời nhóm");
    } catch (err) {
      console.error(err);
      toast.error("Không thể rời nhóm");
    }
  };

  const refreshConversationDetail = async (conversationId) => {
    if (!conversationId) return;
    const detailRes = await chatApi.get(`/conversations/${conversationId}`);
    setConversationDetail(detailRes.data);
  };

  const handleAddMember = async (user) => {
    if (!conversationDetail) return;
    try {
      const res = await chatApi.post(
        `/conversations/${conversationDetail.id}/members`,
        { participant_ids: [user.id] },
      );
      setParticipants(res.data.participants || []);
      await refreshConversationDetail(conversationDetail.id);
      toast.success("Đã thêm thành viên");
      setMemberSearchQuery("");
      setMemberSearchResults([]);
    } catch (err) {
      console.error(err);
      if (err.response?.data?.detail === "NOT_ADMIN") {
        toast.error("Chỉ admin mới thêm thành viên được");
        return;
      }
      toast.error("Không thể thêm thành viên");
    }
  };

  const handleToggleAdmin = async (member) => {
    if (!conversationDetail) return;
    try {
      const res = await chatApi.patch(
        `/conversations/${conversationDetail.id}/members/${member.user_id}/admin`,
        { is_admin: !member.is_admin },
      );
      setParticipants(res.data.participants || []);
      await refreshConversationDetail(conversationDetail.id);
      toast.success("Đã cập nhật quyền");
    } catch (err) {
      console.error(err);
      if (err.response?.data?.detail === "NOT_ADMIN") {
        toast.error("Chỉ admin mới đổi quyền được");
        return;
      }
      toast.error("Không thể cập nhật quyền");
    }
  };

  const currentUserId = currentUser?.id;

  useEffect(() => {
    if (!currentUserId) {
      navigate("/login");
      return;
    }

    // Gọi fetchConversations bình thường
    fetchConversations();

    // Khởi tạo kết nối WebSocket
    connectWebSocket(currentUserId);

    // CLEANUP FUNCTION: Chỉ đóng kết nối khi Component thực sự bị hủy (Unmount)
    // hoặc khi currentUser thay đổi (đăng xuất / đổi tài khoản)
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
        wsRef.current = null;
      }
    };
    // CHÚ Ý: Loại bỏ connectWebSocket và fetchConversations ra khỏi dependency của useEffect này
    // để tránh việc re-render component kích hoạt kết nối lại.
  }, [currentUserId, navigate]);

  useEffect(() => {
    if (searchTimeoutRef.current) {
      clearTimeout(searchTimeoutRef.current);
    }

    if (searchQuery.trim().length < 2) {
      setSearchResults([]);
      return;
    }

    searchTimeoutRef.current = setTimeout(async () => {
      try {
        setSearching(true);
        const res = await api.get("/api/users/search/", {
          params: { q: searchQuery.trim() },
        });
        setSearchResults(res.data.results || []);
      } catch (err) {
        console.error(err);
      } finally {
        setSearching(false);
      }
    }, 300);

    return () => {
      if (searchTimeoutRef.current) {
        clearTimeout(searchTimeoutRef.current);
      }
    };
  }, [searchQuery]);

  useEffect(() => {
    if (!isCreateGroupModalOpen) return;

    if (modalSearchTimeoutRef.current) {
      clearTimeout(modalSearchTimeoutRef.current);
    }

    if (modalSearchQuery.trim().length < 2) {
      setModalSearchResults([]);
      return;
    }

    modalSearchTimeoutRef.current = setTimeout(async () => {
      try {
        setModalSearching(true);
        const res = await api.get("/api/users/search/", {
          params: { q: modalSearchQuery.trim() },
        });
        setModalSearchResults(res.data.results || []);
      } catch (err) {
        console.error(err);
        setModalSearchResults([]);
      } finally {
        setModalSearching(false);
      }
    }, 300);

    return () => {
      if (modalSearchTimeoutRef.current) {
        clearTimeout(modalSearchTimeoutRef.current);
        modalSearchTimeoutRef.current = null;
      }
    };
  }, [modalSearchQuery, isCreateGroupModalOpen]);

  useEffect(() => {
    if (!isConversationInfoOpen) return;

    if (memberSearchTimeoutRef.current) {
      clearTimeout(memberSearchTimeoutRef.current);
    }

    if (memberSearchQuery.trim().length < 2) {
      setMemberSearchResults([]);
      return;
    }

    memberSearchTimeoutRef.current = setTimeout(async () => {
      try {
        setMemberSearching(true);
        const res = await api.get("/api/users/search/", {
          params: { q: memberSearchQuery.trim() },
        });
        setMemberSearchResults(res.data.results || []);
      } catch (err) {
        console.error(err);
        setMemberSearchResults([]);
      } finally {
        setMemberSearching(false);
      }
    }, 300);

    return () => {
      if (memberSearchTimeoutRef.current) {
        clearTimeout(memberSearchTimeoutRef.current);
        memberSearchTimeoutRef.current = null;
      }
    };
  }, [memberSearchQuery, isConversationInfoOpen]);

  useEffect(() => {
    if (shouldScrollToBottomRef.current && messagesContainerRef.current) {
      messagesContainerRef.current.scrollTop =
        messagesContainerRef.current.scrollHeight;
    }
  }, [messages]);

  const handleScroll = (e) => {
    if (e.target.scrollTop === 0 && hasMoreMessages && !loadingMoreMessages) {
      loadMoreMessages();
    }
  };

  return (
    <div className="chat-page">
      <div className="chat-container">
        <aside className="chat-sidebar">
          <div className="chat-sidebar__header">
            <h1>{t("chat.title")}</h1>
            <button
              type="button"
              className="chat-create-group-btn"
              onClick={openCreateGroupModal}
            >
              {t("chat.create_group_button")}
            </button>
          </div>

          <div className="chat-search">
            <input
              type="text"
              placeholder={t("chat.search_user")}
              value={searchQuery}
              onChange={(e) => setSearchQuery(e.target.value)}
            />
            {searching && (
              <div className="chat-search__status">{t("common.search")}...</div>
            )}
            {searchResults.length > 0 && (
              <div className="chat-search__results">
                {searchResults.map((user) => (
                  <div
                    key={user.id}
                    className="chat-search__item chat-search__item--actions"
                  >
                    <button
                      type="button"
                      className="chat-search__action"
                      onClick={() => startConversation(user)}
                    >
                      {user.username}
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>

          <div className="chat-conversation-list">
            {loadingConversations ? (
              <div className="chat-empty">{t("common.loading")}</div>
            ) : conversations.length === 0 ? (
              <div className="chat-empty">{t("chat.no_conversations")}</div>
            ) : (
              conversations.map((conv) => {
                const isActive = activeConversation?.id === conv.id;
                const name = conversationTitle(conv, t);
                const preview =
                  conversationPreview(conv, currentUser?.id) ||
                  t("chat.no_messages");
                const avatarFallback = name?.charAt(0)?.toUpperCase() || "?";

                return (
                  <button
                    key={conv.id}
                    type="button"
                    className={`chat-conversation-item${isActive ? " chat-conversation-item--active" : ""}`}
                    onClick={() => openConversation(conv)}
                  >
                    <div className="chat-conversation-item__top">
                      <div className="chat-conversation-item__identity">
                        {conv.avatar ? (
                          <img
                            src={conv.avatar}
                            alt={name}
                            className="chat-conversation-item__avatar"
                          />
                        ) : (
                          <span className="chat-conversation-item__avatar chat-conversation-item__avatar--fallback">
                            {avatarFallback}
                          </span>
                        )}
                        <span className="chat-conversation-item__name">
                          {name}
                        </span>
                      </div>
                      <span className="chat-conversation-item__time">
                        {formatTime(conv.message_created_at)}
                      </span>
                    </div>
                    <p className="chat-conversation-item__preview">{preview}</p>
                  </button>
                );
              })
            )}
          </div>
        </aside>

        <main className="chat-main">
          {!activeConversation ? (
            <div className="chat-placeholder">
              <h2>{t("chat.select_conversation")}</h2>
              <p>{t("chat.select_conversation_hint")}</p>
            </div>
          ) : (
            <>
              <div className="chat-main__header">
                <div className="chat-main__header-identity">
                  {activeConversation.avatar ? (
                    <img
                      src={activeConversation.avatar}
                      alt={conversationTitle(activeConversation, t)}
                      className="chat-main__header-avatar"
                    />
                  ) : (
                    <span className="chat-main__header-avatar chat-main__header-avatar--fallback">
                      {(conversationTitle(activeConversation, t) || "?")
                        .charAt(0)
                        .toUpperCase()}
                    </span>
                  )}
                  <h2>{conversationTitle(activeConversation, t)}</h2>
                </div>
                <div className="chat-main__header-actions">
                  <button
                    type="button"
                    className="chat-main__menu-btn"
                    onClick={() => setIsConversationMenuOpen((prev) => !prev)}
                  >
                    ⋯
                  </button>
                  {isConversationMenuOpen && (
                    <div className="chat-main__menu">
                      <div className="chat-main__menu-rename">
                        <input
                          type="text"
                          value={renameValue}
                          onChange={(e) => setRenameValue(e.target.value)}
                          placeholder="Tên đoạn chat"
                        />
                        <button
                          type="button"
                          onClick={handleUpdateConversationName}
                        >
                          Đổi tên
                        </button>
                      </div>
                      <button
                        type="button"
                        onClick={() => {
                          setIsConversationInfoOpen(true);
                          setIsConversationMenuOpen(false);
                        }}
                      >
                        Xem thông tin nhóm
                      </button>
                      <button type="button" onClick={handleLeaveGroup}>
                        Rời nhóm
                      </button>
                    </div>
                  )}
                </div>
              </div>

              <div
                className="chat-messages"
                ref={messagesContainerRef}
                onScroll={handleScroll}
              >
                {loadingMessages ? (
                  <div className="chat-empty">{t("common.loading")}</div>
                ) : messages.length === 0 ? (
                  <div className="chat-empty">{t("chat.start_chatting")}</div>
                ) : (
                  <>
                    {hasMoreMessages && loadingMoreMessages && (
                      <div
                        className="chat-load-more"
                        style={{ textAlign: "center", padding: "10px" }}
                      >
                        <span
                          style={{
                            color: "var(--color-primary)",
                            fontSize: "0.9rem",
                          }}
                        >
                          Đang tải...
                        </span>
                      </div>
                    )}
                    {messages.map((msg) => {
                      if (msg.type === "system") {
                        return (
                          <div key={msg.id} className="chat-message-system">
                            <span>{msg.content}</span>
                          </div>
                        );
                      }
                      const isMine = msg.sender_id === currentUser?.id;
                      const sender = participantByUserId(msg.sender_id);
                      const replyToMessage = messages.find(
                        (item) => item.id === msg.reply_to_message_id,
                      );
                      const messageReaders = watermarksMap[msg.id] || [];
                      const displayedContent = msg.is_deleted
                        ? "Người dùng đã xóa tin nhắn này"
                        : msg.content;
                      const attachments = msg.is_deleted
                        ? []
                        : msg.attachments || [];
                      return (
                        <div
                          key={msg.id}
                          className={`chat-message${isMine ? " chat-message--mine" : ""}`}
                        >
                          {!isMine && (
                            <div className="chat-message__sender">
                              {sender?.avatar ? (
                                <img
                                  src={sender.avatar}
                                  alt={sender?.name || "user"}
                                  className="chat-message__sender-avatar"
                                />
                              ) : (
                                <span className="chat-message__sender-avatar chat-message__sender-avatar--fallback">
                                  {(sender?.name || "U")
                                    .charAt(0)
                                    .toUpperCase()}
                                </span>
                              )}
                            </div>
                          )}
                          <div className="chat-message__content">
                            <div className="chat-message__bubble">
                              {replyToMessage && (
                                <div className="chat-message__reply-preview">
                                  {messagePreviewText(replyToMessage)}
                                </div>
                              )}
                              {attachments.length > 0 && (
                                <div className="chat-message__attachments">
                                  {attachments.map((att) => {
                                    if (isImageAttachment(att)) {
                                      return (
                                        <a
                                          key={att.id}
                                          href={att.file_url}
                                          target="_blank"
                                          rel="noreferrer"
                                          className="chat-message__attachment-image"
                                        >
                                          <img
                                            src={att.file_url}
                                            alt={att.file_name}
                                          />
                                        </a>
                                      );
                                    }
                                    if (isVideoAttachment(att)) {
                                      return (
                                        <video
                                          key={att.id}
                                          className="chat-message__attachment-video"
                                          src={att.file_url}
                                          controls
                                          preload="metadata"
                                        />
                                      );
                                    }
                                    if (isAudioAttachment(att)) {
                                      return (
                                        <audio
                                          key={att.id}
                                          className="chat-message__attachment-audio"
                                          src={att.file_url}
                                          controls
                                          preload="metadata"
                                        />
                                      );
                                    }
                                    return (
                                      <a
                                        key={att.id}
                                        href={att.file_url}
                                        target="_blank"
                                        rel="noreferrer"
                                        className="chat-message__attachment-file"
                                        download={att.file_name}
                                      >
                                        <span className="chat-message__attachment-file-icon">
                                          📎
                                        </span>
                                        <span className="chat-message__attachment-file-meta">
                                          <strong>{att.file_name}</strong>
                                          <small>
                                            {formatFileSize(att.size)}
                                          </small>
                                        </span>
                                      </a>
                                    );
                                  })}
                                </div>
                              )}
                              {displayedContent ? <p>{displayedContent}</p> : null}
                            </div>
                            <div className="chat-message__meta">
                              <span className="chat-message__time">
                                {formatTime(msg.created_at)}
                              </span>
                              {isMine && (
                                <span className="chat-message__seen">
                                  {msg.seen_count > 0
                                    ? `${t("chat.seen")} ${msg.seen_count}`
                                    : t("chat.sent")}
                                </span>
                              )}
                            </div>
                            {messageReaders.length > 0 && (
                              <div className="chat-message__watermarks">
                                {messageReaders.map((reader) =>
                                  reader.avatar ? (
                                    <img
                                      key={reader.user_id}
                                      src={reader.avatar}
                                      alt={reader.name}
                                      className="chat-message__watermark-avatar"
                                      title={reader.name}
                                    />
                                  ) : (
                                    <span
                                      key={reader.user_id}
                                      className="chat-message__watermark-fallback"
                                      title={reader.name}
                                    >
                                      {reader.name.charAt(0).toUpperCase()}
                                    </span>
                                  )
                                )}
                              </div>
                            )}
                          </div>
                          <div className="chat-message__actions-wrap">
                            <button
                              type="button"
                              className="chat-message__actions-btn"
                              onClick={() =>
                                setOpenActionsForMessageId((prev) =>
                                  prev === msg.id ? null : msg.id,
                                )
                              }
                            >
                              ⋯
                            </button>
                            {openActionsForMessageId === msg.id && (
                              <div className="chat-message__actions-menu">
                                <button
                                  type="button"
                                  onClick={() => handleReplyMessage(msg)}
                                >
                                  Reply
                                </button>
                                {isMine &&
                                  !msg.is_deleted &&
                                  msg.type === "text" && (
                                  <button
                                    type="button"
                                    onClick={() => handleEditMessage(msg)}
                                  >
                                    Edit
                                  </button>
                                )}
                                {isMine && !msg.is_deleted && (
                                  <button
                                    type="button"
                                    className="delete-btn"
                                    onClick={() => handleDeleteMessage(msg)}
                                  >
                                    Delete
                                  </button>
                                )}
                              </div>
                            )}
                          </div>
                        </div>
                      );
                    })}
                  </>
                )}
              </div>

              <form className="chat-input-form" onSubmit={handleSendMessage}>
                {replyTarget && (
                  <div className="chat-input-form__replying">
                    <span>Đang trả lời: {messagePreviewText(replyTarget)}</span>
                    <button type="button" onClick={() => setReplyTarget(null)}>
                      Hủy
                    </button>
                  </div>
                )}
                {editTarget && (
                  <div className="chat-input-form__replying">
                    <span>Đang sửa: {messagePreviewText(editTarget)}</span>
                    <button
                      type="button"
                      onClick={() => {
                        setEditTarget(null);
                        setMessageInput("");
                      }}
                    >
                      Hủy
                    </button>
                  </div>
                )}
                {pendingFiles.length > 0 && !editTarget && (
                  <div className="chat-input-form__files">
                    {pendingFiles.map((file, index) => (
                      <div
                        key={`${file.name}-${file.size}-${file.lastModified}-${index}`}
                        className="chat-input-form__file-chip"
                      >
                        <span className="chat-input-form__file-name">
                          {file.name}
                        </span>
                        <span className="chat-input-form__file-size">
                          {formatFileSize(file.size)}
                        </span>
                        <button
                          type="button"
                          className="chat-input-form__file-remove"
                          onClick={() => removePendingFile(index)}
                          aria-label="Xóa file"
                        >
                          ×
                        </button>
                      </div>
                    ))}
                  </div>
                )}
                <div className="chat-input-form__row">
                  {!editTarget && (
                    <>
                      <input
                        ref={fileInputRef}
                        type="file"
                        className="chat-input-form__file-input"
                        multiple
                        accept="image/*,video/*,audio/*,.pdf,.doc,.docx,.xls,.xlsx,.ppt,.pptx,.txt,.zip,.rar"
                        onChange={handleSelectFiles}
                        tabIndex={-1}
                        aria-hidden="true"
                      />
                      <button
                        type="button"
                        className="chat-input-form__attach-btn"
                        onClick={() => fileInputRef.current?.click()}
                        disabled={sendingMessage}
                        title="Đính kèm file"
                        aria-label="Đính kèm file"
                      >
                        📎
                      </button>
                    </>
                  )}
                  <input
                    type="text"
                    placeholder={t("chat.type_message")}
                    value={messageInput}
                    onChange={(e) => setMessageInput(e.target.value)}
                    onFocus={handleInputFocus}
                    disabled={sendingMessage}
                  />
                  <button
                    type="submit"
                    disabled={
                      sendingMessage ||
                      (editTarget
                        ? !messageInput.trim()
                        : !messageInput.trim() && pendingFiles.length === 0)
                    }
                  >
                    {sendingMessage ? "..." : t("chat.send")}
                  </button>
                </div>
              </form>
            </>
          )}
        </main>
      </div>

      {isCreateGroupModalOpen && (
        <div
          className="chat-modal-overlay"
          role="dialog"
          aria-modal="true"
          onClick={closeCreateGroupModal}
        >
          <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
            <div className="chat-modal__header">
              <h3 className="chat-modal__title">
                {t("chat.create_group_title")}
              </h3>
              <button
                type="button"
                className="chat-modal__close"
                onClick={closeCreateGroupModal}
                aria-label={t("common.cancel")}
              >
                ×
              </button>
            </div>

            <div className="chat-modal__body">
              <input
                type="text"
                className="chat-modal__input"
                placeholder={t("chat.group_name_placeholder")}
                value={groupName}
                onChange={(e) => setGroupName(e.target.value)}
              />

              <div className="chat-modal__user-search">
                <input
                  type="text"
                  className="chat-modal__input"
                  placeholder={t("chat.search_user")}
                  value={modalSearchQuery}
                  onChange={(e) => setModalSearchQuery(e.target.value)}
                />

                {modalSearching && (
                  <div className="chat-modal__status">
                    {t("common.search")}...
                  </div>
                )}

                {modalSearchResults.length > 0 && (
                  <div className="chat-modal__user-results">
                    {modalSearchResults.map((user) => {
                      const isSelected = selectedGroupUsers.some(
                        (item) => item.id === user.id,
                      );
                      return (
                        <div key={user.id} className="chat-modal__user-result">
                          <span className="chat-modal__user-name">
                            {user.username}
                          </span>
                          <button
                            type="button"
                            className="chat-modal__user-toggle"
                            onClick={() => toggleGroupUser(user)}
                          >
                            {isSelected
                              ? t("chat.remove_from_group")
                              : t("chat.add_to_group")}
                          </button>
                        </div>
                      );
                    })}
                  </div>
                )}
              </div>

              <div className="chat-modal__selected">
                {selectedGroupUsers.length === 0 ? (
                  <span className="chat-modal__selected-empty">
                    {t("chat.no_group_members_selected")}
                  </span>
                ) : (
                  <div className="chat-modal__selected-tags">
                    {selectedGroupUsers.map((user) => (
                      <button
                        key={user.id}
                        type="button"
                        className="chat-group-member-tag"
                        onClick={() => toggleGroupUser(user)}
                      >
                        {user.username} x
                      </button>
                    ))}
                  </div>
                )}
              </div>
            </div>

            <div className="chat-modal__actions">
              <button
                type="button"
                className="chat-modal__cancel"
                onClick={closeCreateGroupModal}
                disabled={creatingGroup}
              >
                {t("common.cancel")}
              </button>
              <button
                type="button"
                className="chat-modal__create"
                onClick={createGroupConversation}
                disabled={
                  creatingGroup ||
                  !groupName.trim() ||
                  selectedGroupUsers.length < 2
                }
              >
                {creatingGroup
                  ? t("common.loading")
                  : t("chat.create_group_button")}
              </button>
            </div>
          </div>
        </div>
      )}

      {isConversationInfoOpen && conversationDetail && (
        <div
          className="chat-modal-overlay"
          role="dialog"
          aria-modal="true"
          onClick={() => setIsConversationInfoOpen(false)}
        >
          <div className="chat-modal" onClick={(e) => e.stopPropagation()}>
            <div className="chat-modal__header">
              <h3 className="chat-modal__title">Thông tin đoạn chat</h3>
              <button
                type="button"
                className="chat-modal__close"
                onClick={() => setIsConversationInfoOpen(false)}
              >
                ×
              </button>
            </div>
            <div className="chat-modal__body">
              <div className="chat-conversation-info__avatar-section">
                <div
                  className={`chat-conversation-info__avatar-wrap${isUploadingConversationAvatar ? " chat-conversation-info__avatar-wrap--loading" : ""}`}
                >
                  {conversationDetail.avatar ? (
                    <img
                      src={conversationDetail.avatar}
                      alt={conversationTitle(conversationDetail, t)}
                      className="chat-conversation-info__avatar"
                    />
                  ) : (
                    <span className="chat-conversation-info__avatar chat-conversation-info__avatar--fallback">
                      {(conversationTitle(conversationDetail, t) || "?")
                        .charAt(0)
                        .toUpperCase()}
                    </span>
                  )}
                  {isUploadingConversationAvatar && (
                    <span className="chat-conversation-info__avatar-loading">
                      {t("common.loading")}
                    </span>
                  )}
                  <button
                    type="button"
                    className="chat-conversation-info__avatar-edit"
                    onClick={handleConversationAvatarClick}
                    disabled={isUploadingConversationAvatar}
                    aria-label={t("chat.change_conversation_avatar")}
                    title={t("chat.change_conversation_avatar")}
                  >
                    <svg
                      viewBox="0 0 24 24"
                      width="14"
                      height="14"
                      fill="none"
                      stroke="currentColor"
                      strokeWidth="2"
                      strokeLinecap="round"
                      strokeLinejoin="round"
                      aria-hidden="true"
                    >
                      <path d="M12 20h9" />
                      <path d="M16.5 3.5a2.12 2.12 0 0 1 3 3L7 19l-4 1 1-4Z" />
                    </svg>
                  </button>
                </div>
                <p className="chat-conversation-info__avatar-hint">
                  {t("chat.conversation_avatar_hint")}
                </p>
                <input
                  ref={conversationAvatarInputRef}
                  type="file"
                  accept="image/png,image/jpeg,image/jpg,image/webp,image/gif"
                  className="chat-conversation-info__avatar-input"
                  onChange={handleConversationAvatarChange}
                />
              </div>

              <p>
                <strong>Ngày tạo:</strong>{" "}
                {formatDateTime(conversationDetail.created_at)}
              </p>
              <p>
                <strong>Tạo bởi:</strong> {conversationDetail.created_by_name}
              </p>
              <div className="chat-conversation-info__members">
                {isCurrentUserAdmin && (
                  <div className="chat-conversation-info__add-member">
                    <strong>Thêm thành viên</strong>
                    <input
                      type="text"
                      className="chat-modal__input"
                      placeholder="Tìm user..."
                      value={memberSearchQuery}
                      onChange={(e) => setMemberSearchQuery(e.target.value)}
                    />
                    {memberSearching && (
                      <div className="chat-modal__status">Đang tìm...</div>
                    )}
                    {memberSearchResults.length > 0 && (
                      <div className="chat-conversation-info__add-results">
                        {memberSearchResults.map((user) => (
                          <div
                            key={user.id}
                            className="chat-conversation-info__add-result"
                          >
                            <span>{user.username}</span>
                            <button
                              type="button"
                              onClick={() => handleAddMember(user)}
                            >
                              Thêm
                            </button>
                          </div>
                        ))}
                      </div>
                    )}
                  </div>
                )}
                {(conversationDetail.participants || []).map((member) => (
                  <div
                    key={member.user_id}
                    className="chat-conversation-info__member"
                  >
                    <div>
                      {member.avatar ? (
                        <img
                          src={member.avatar}
                          alt={member.name}
                          className="chat-conversation-info__member-avatar"
                        />
                      ) : (
                        <span className="chat-conversation-info__member-avatar chat-conversation-info__member-avatar--fallback">
                          {member.name.charAt(0).toUpperCase()}
                        </span>
                      )}
                    </div>
                    <div className="chat-conversation-info__member-meta">
                      <strong>{member.name}</strong>
                      <span>Join: {formatDateTime(member.joined_at)}</span>
                      <span>{member.is_admin ? "Admin" : "Member"}</span>
                    </div>
                    {isCurrentUserAdmin &&
                      member.user_id !== currentUser?.id && (
                        <button
                          type="button"
                          className="chat-conversation-info__admin-btn"
                          onClick={() => handleToggleAdmin(member)}
                        >
                          {member.is_admin ? "Bỏ admin" : "Đặt admin"}
                        </button>
                      )}
                  </div>
                ))}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Chat;
