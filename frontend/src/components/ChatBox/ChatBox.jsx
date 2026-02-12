import { useState, useEffect, useRef } from "react";
import API_BASE_URL from "../../config";
import "./ChatBox.css";

const ChatBox = ({
  sessionId,
  onSessionCreated,
  onToggleSidebar,
  isSidebarOpen,
}) => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const [loadingHistory, setLoadingHistory] = useState(true);
  const messagesEndRef = useRef(null);
  const inputRef = useRef(null);

  // Fetch chat history or specific session
  useEffect(() => {
    if (!sessionId) {
      setMessages([]);
      setLoadingHistory(false);
      return;
    }

    const fetchChatHistory = async () => {
      try {
        setLoadingHistory(true);
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
          const allMessages = [];

          // Load only the selected session
          const selectedChat = data.chats?.find(
            (chat) => chat._id === sessionId,
          );
          if (selectedChat && selectedChat.messages) {
            selectedChat.messages.forEach((msg) => {
              allMessages.push({
                role: msg.role,
                content: msg.content,
                timestamp: new Date(msg.timestamp),
              });
            });
          }

          // Sort messages by timestamp (oldest first)
          allMessages.sort(
            (a, b) => new Date(a.timestamp) - new Date(b.timestamp),
          );
          setMessages(allMessages);
        }
      } catch (error) {
        console.error("Error fetching chat history:", error);
      } finally {
        setLoadingHistory(false);
      }
    };

    fetchChatHistory();
  }, [sessionId]);

  // Auto-scroll to the bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input, timestamp: new Date() };
    setMessages((prevMessages) => [...prevMessages, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const baseUrl = API_BASE_URL.replace(/\/$/, "");
      const token = localStorage.getItem("access_token");
      const messageText = input;

      const response = await fetch(`${baseUrl}/api/chat/`, {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
          Authorization: `Bearer ${token}`,
        },
        body: JSON.stringify({ message: messageText, session_id: sessionId }),
      });

      if (!response.ok) {
        if (response.status === 401) {
          // Token expired or invalid, redirect to login
          localStorage.clear();
          window.location.href = "/login";
          return;
        }
        throw new Error("Failed to fetch response");
      }

      const data = await response.json();
      if (!data.response) {
        throw new Error("Empty response from the server");
      }
      const botMessage = {
        role: "bot",
        content: data.response,
        timestamp: new Date(),
      };
      setMessages((prevMessages) => [...prevMessages, botMessage]);
      inputRef.current?.focus();

      // Notify parent that a new session was created
      if (!sessionId && data.session_id && onSessionCreated) {
        onSessionCreated(data.session_id);
      }
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages((prevMessages) => [
        ...prevMessages,
        {
          role: "bot",
          content: "Sorry, something went wrong. Please try again later.",
          timestamp: new Date(),
        },
      ]);
    } finally {
      setLoading(false);
    }
  };

  const handleSuggestionClick = (suggestion) => {
    setInput(suggestion);
    inputRef.current?.focus();
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-header">
        <div className="header-content">
          <button
            className="sidebar-toggle"
            type="button"
            onClick={onToggleSidebar}
            aria-label="Toggle chat history"
            aria-expanded={isSidebarOpen}
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
            >
              <line x1="3" y1="6" x2="21" y2="6"></line>
              <line x1="3" y1="12" x2="21" y2="12"></line>
              <line x1="3" y1="18" x2="21" y2="18"></line>
            </svg>
          </button>
          <div className="header-icon">🎓</div>
          <div className="header-text">
            <h2>Degree Dialog</h2>
            <p className="header-subtitle">Your AI College Advisor</p>
          </div>
        </div>
      </div>
      <div className="chatbox-messages">
        {loadingHistory ? (
          <div className="skeleton-stack" aria-hidden="true">
            <div className="skeleton-bubble skeleton-left"></div>
            <div className="skeleton-bubble skeleton-right"></div>
            <div className="skeleton-bubble skeleton-left"></div>
            <div className="skeleton-bubble skeleton-right"></div>
            <div className="skeleton-bubble skeleton-left"></div>
          </div>
        ) : messages.length === 0 ? (
          <div className="empty-state">
            <div className="empty-icon">💬</div>
            <h3>Welcome to Degree Dialog!</h3>
            <p>
              I&apos;m here to help you with college admissions, courses,
              scholarships, and more. Ask me anything!
            </p>
            <div className="suggestions">
              <div
                className="suggestion-chip"
                onClick={() =>
                  handleSuggestionClick("Tell me about scholarships")
                }
              >
                Tell me about scholarships
              </div>
              <div
                className="suggestion-chip"
                onClick={() =>
                  handleSuggestionClick("How do I apply to college?")
                }
              >
                How do I apply to college?
              </div>
              <div
                className="suggestion-chip"
                onClick={() =>
                  handleSuggestionClick("What are the best courses?")
                }
              >
                What are the best courses?
              </div>
            </div>
          </div>
        ) : null}
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role === "user" ? "user" : "bot"}`}
          >
            <div className="message-content">
              <div className="message-text">{msg.content}</div>
            </div>
          </div>
        ))}
        {loading && (
          <div className="message bot">
            <div className="message-content">
              <div className="typing-indicator">
                <span></span>
                <span></span>
                <span></span>
              </div>
            </div>
          </div>
        )}
        <div ref={messagesEndRef} />
      </div>
      <div className="chatbox-input">
        <div className="input-wrapper">
          <input
            ref={inputRef}
            type="text"
            value={input}
            onChange={(e) => setInput(e.target.value)}
            onKeyPress={(e) =>
              e.key === "Enter" && !e.shiftKey && sendMessage()
            }
            placeholder="Ask about college, admissions, scholarships..."
            aria-label="Type your message"
            disabled={loading}
          />
          <button
            onClick={sendMessage}
            disabled={loading || !input.trim()}
            className="send-button"
          >
            <svg
              width="20"
              height="20"
              viewBox="0 0 24 24"
              fill="none"
              stroke="currentColor"
              strokeWidth="2"
              strokeLinecap="round"
              strokeLinejoin="round"
            >
              <line x1="22" y1="2" x2="11" y2="13"></line>
              <polygon points="22 2 15 22 11 13 2 9 22 2"></polygon>
            </svg>
          </button>
        </div>
      </div>
    </div>
  );
};

export default ChatBox;
