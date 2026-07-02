import React, { useCallback, useContext, useEffect, useRef, useState } from "react";
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
  return date.toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" });
}

function displayName(user) {
  if (!user) return "";
  const fullName = `${user.first_name || ""} ${user.last_name || ""}`.trim();
  return fullName || user.username;
}

function Chat() {
  const { t } = useTranslation();
  const navigate = useNavigate();
  const { currentUser } = useContext(AuthContext);

  const [conversations, setConversations] = useState([]);
  const [activeConversation, setActiveConversation] = useState(null);
  const [messages, setMessages] = useState([]);
  const [loadingConversations, setLoadingConversations] = useState(true);
  const [loadingMessages, setLoadingMessages] = useState(false);
  const [messageInput, setMessageInput] = useState("");
  const [searchQuery, setSearchQuery] = useState("");
  const [searchResults, setSearchResults] = useState([]);
  const [searching, setSearching] = useState(false);

  const wsRef = useRef(null);
  const wsReconnectAttemptRef = useRef(0);
  const messagesEndRef = useRef(null);
  const searchTimeoutRef = useRef(null);
  const activeConversationIdRef = useRef(null);

  const scrollToBottom = () => {
    messagesEndRef.current?.scrollIntoView({ behavior: "smooth" });
  };

  const fetchConversations = useCallback(async () => {
    try {
      setLoadingConversations(true);
      const res = await chatApi.get("/conversations");
      setConversations(res.data.results || []);
    } catch (err) {
      console.error(err);
      toast.error(t("chat.load_conversations_error"));
    } finally {
      setLoadingConversations(false);
    }
  }, [t]);

  const connectWebSocket = useCallback(
    (conversationId, isReconnect = false) => {
    if (wsRef.current) {
      wsRef.current.close();
      wsRef.current = null;
    }

    if (!isReconnect) wsReconnectAttemptRef.current = 0;

    const ws = new WebSocket(getChatWebSocketUrl(conversationId));
    wsRef.current = ws;

    ws.onmessage = (event) => {
      try {
        const payload = JSON.parse(event.data);
        if (payload.type === "message" && payload.data) {
          setMessages((prev) => {
            if (prev.some((m) => m.id === payload.data.id)) return prev;
            return [...prev, payload.data];
          });
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
        activeConversationIdRef.current === conversationId
      ) {
        wsReconnectAttemptRef.current += 1;
        try {
          await refreshAccessToken();
          connectWebSocket(conversationId, true);
          fetchConversations();
          return;
        } catch (e) {
          localStorage.clear();
          navigate("/login");
          return;
        }
      }
    };
  },
    [t, fetchConversations, navigate],
  );

  useEffect(() => {
    activeConversationIdRef.current = activeConversation?.id ?? null;
  }, [activeConversation]);

  const openConversation = useCallback(
    async (conversation) => {
      setActiveConversation(conversation);
      setLoadingMessages(true);

      try {
        const res = await chatApi.get(`/conversations/${conversation.id}/messages`);
        setMessages(res.data.results || []);
        await chatApi.post(`/conversations/${conversation.id}/read`);
        connectWebSocket(conversation.id);
        fetchConversations();
      } catch (err) {
        console.error(err);
        toast.error(t("chat.load_messages_error"));
      } finally {
        setLoadingMessages(false);
      }
    },
    [connectWebSocket, fetchConversations, t],
  );

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

  const handleSendMessage = async (e) => {
    e.preventDefault();
    const content = messageInput.trim();
    if (!content || !activeConversation) return;

    setMessageInput("");

    if (wsRef.current && wsRef.current.readyState === WebSocket.OPEN) {
      wsRef.current.send(JSON.stringify({ content }));
      return;
    }

    try {
      const res = await chatApi.post(
        `/conversations/${activeConversation.id}/messages`,
        { content },
      );
      setMessages((prev) => [...prev, res.data]);
      fetchConversations();
    } catch (err) {
      console.error(err);
      toast.error(t("chat.send_error"));
      setMessageInput(content);
    }
  };

  useEffect(() => {
    if (!currentUser) {
      navigate("/login");
      return;
    }
    fetchConversations();
  }, [currentUser, fetchConversations, navigate]);

  useEffect(() => {
    scrollToBottom();
  }, [messages]);

  useEffect(() => {
    return () => {
      if (wsRef.current) {
        wsRef.current.close();
      }
    };
  }, []);

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

  return (
    <div className="chat-page">
      <div className="chat-container">
        <aside className="chat-sidebar">
          <div className="chat-sidebar__header">
            <h1>{t("chat.title")}</h1>
            <p>{t("chat.subtitle")}</p>
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
                  <button
                    key={user.id}
                    type="button"
                    className="chat-search__item"
                    onClick={() => startConversation(user)}
                  >
                    {user.username}
                  </button>
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
                const name = displayName(conv.other_user) || t("chat.unknown_user");
                const preview = conv.last_message?.content || t("chat.no_messages");

                return (
                  <button
                    key={conv.id}
                    type="button"
                    className={`chat-conversation-item${isActive ? " chat-conversation-item--active" : ""}`}
                    onClick={() => openConversation(conv)}
                  >
                    <div className="chat-conversation-item__top">
                      <span className="chat-conversation-item__name">{name}</span>
                      {conv.unread_count > 0 && (
                        <span className="chat-conversation-item__badge">
                          {conv.unread_count}
                        </span>
                      )}
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
                <h2>{displayName(activeConversation.other_user)}</h2>
              </div>

              <div className="chat-messages">
                {loadingMessages ? (
                  <div className="chat-empty">{t("common.loading")}</div>
                ) : messages.length === 0 ? (
                  <div className="chat-empty">{t("chat.start_chatting")}</div>
                ) : (
                  messages.map((msg) => {
                    const isMine = msg.sender_id === currentUser?.id;
                    return (
                      <div
                        key={msg.id}
                        className={`chat-message${isMine ? " chat-message--mine" : ""}`}
                      >
                        <div className="chat-message__bubble">
                          <p>{msg.content}</p>
                          <span className="chat-message__time">
                            {formatTime(msg.created_at)}
                          </span>
                        </div>
                      </div>
                    );
                  })
                )}
                <div ref={messagesEndRef} />
              </div>

              <form className="chat-input-form" onSubmit={handleSendMessage}>
                <input
                  type="text"
                  placeholder={t("chat.type_message")}
                  value={messageInput}
                  onChange={(e) => setMessageInput(e.target.value)}
                />
                <button type="submit" disabled={!messageInput.trim()}>
                  {t("chat.send")}
                </button>
              </form>
            </>
          )}
        </main>
      </div>
    </div>
  );
}

export default Chat;
