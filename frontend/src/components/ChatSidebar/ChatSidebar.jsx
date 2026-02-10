import { useState, useEffect } from "react";
import API_BASE_URL from "../../config";
import "./ChatSidebar.css";

const ChatSidebar = ({ selectedSessionId, onSessionSelect, onNewChat }) => {
  const [sessions, setSessions] = useState([]);
  const [loading, setLoading] = useState(true);

  // Fetch all chat sessions
  const fetchSessions = async () => {
    try {
      setLoading(true);
      const baseUrl = API_BASE_URL.replace(/\/$/, "");
      const token = localStorage.getItem("access_token");

      const response = await fetch(`${baseUrl}/api/chat/history/`, {
        method: "GET",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
      });

      if (response.ok) {
        const data = await response.json();
        if (data.chats && Array.isArray(data.chats)) {
          setSessions(data.chats);
        }
      }
    } catch (error) {
      console.error("Error fetching sessions:", error);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchSessions();
  }, []);

  const handleNewChat = () => {
    onNewChat();
    fetchSessions();
  };

  const formatDate = (dateString) => {
    const date = new Date(dateString);
    const today = new Date();
    const yesterday = new Date(today);
    yesterday.setDate(yesterday.getDate() - 1);

    if (date.toDateString() === today.toDateString()) {
      return date.toLocaleTimeString("en-US", {
        hour: "2-digit",
        minute: "2-digit",
      });
    } else if (date.toDateString() === yesterday.toDateString()) {
      return "Yesterday";
    } else {
      return date.toLocaleDateString("en-US", {
        month: "short",
        day: "numeric",
      });
    }
  };

  const getSessionPreview = (chatEntry) => {
    if (chatEntry.messages && chatEntry.messages.length > 0) {
      const firstUserMessage = chatEntry.messages.find(
        (m) => m.role === "user",
      );
      return firstUserMessage
        ? firstUserMessage.content.substring(0, 50)
        : "New conversation";
    }
    return "New conversation";
  };

  const handleClearHistory = async () => {
    if (
      confirm(
        "Are you sure you want to delete all chat history? This cannot be undone.",
      )
    ) {
      try {
        const baseUrl = API_BASE_URL.replace(/\/$/, "");
        const token = localStorage.getItem("access_token");

        const response = await fetch(`${baseUrl}/api/chat/clear/`, {
          method: "DELETE",
          headers: {
            "Content-Type": "application/json",
            Authorization: `Bearer ${token}`,
          },
        });

        if (response.ok) {
          setSessions([]);
          onNewChat();
        }
      } catch (error) {
        console.error("Error clearing history:", error);
      }
    }
  };

  return (
    <div className="chat-sidebar">
      <div className="sidebar-header">
        <h2>Degree Dialog</h2>
        <button
          className="new-chat-btn"
          onClick={handleNewChat}
          title="Start a new chat"
        >
          <svg
            width="20"
            height="20"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <line x1="12" y1="5" x2="12" y2="19"></line>
            <line x1="5" y1="12" x2="19" y2="12"></line>
          </svg>
          New Chat
        </button>
      </div>

      <div className="sessions-container">
        {loading ? (
          <div className="loading">Loading sessions...</div>
        ) : sessions.length === 0 ? (
          <div className="empty-sessions">No chat history yet</div>
        ) : (
          <div className="sessions-list">
            {sessions.map((session) => (
              <div
                key={session._id}
                className={`session-item ${selectedSessionId === session._id ? "active" : ""}`}
                onClick={() => onSessionSelect(session._id)}
                title={getSessionPreview(session)}
              >
                <div className="session-preview">
                  {getSessionPreview(session)}
                </div>
                <div className="session-date">
                  {formatDate(session.created_at)}
                </div>
              </div>
            ))}
          </div>
        )}
      </div>

      <div className="sidebar-footer">
        <button
          className="clear-history-btn"
          onClick={handleClearHistory}
          disabled={sessions.length === 0}
          title="Delete all chat history"
        >
          <svg
            width="16"
            height="16"
            viewBox="0 0 24 24"
            fill="none"
            stroke="currentColor"
            strokeWidth="2"
          >
            <polyline points="3 6 5 6 21 6"></polyline>
            <path d="M19 6v14a2 2 0 0 1-2 2H7a2 2 0 0 1-2-2V6m3 0V4a2 2 0 0 1 2-2h4a2 2 0 0 1 2 2v2"></path>
            <line x1="10" y1="11" x2="10" y2="17"></line>
            <line x1="14" y1="11" x2="14" y2="17"></line>
          </svg>
          Clear History
        </button>
      </div>
    </div>
  );
};

export default ChatSidebar;
