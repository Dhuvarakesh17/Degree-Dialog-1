import { useState, useEffect, useRef } from "react";
import "./ChatBox.css";

const ChatBox = () => {
  const [messages, setMessages] = useState([]);
  const [input, setInput] = useState("");
  const [loading, setLoading] = useState(false);
  const messagesEndRef = useRef(null);

  // Auto-scroll to the bottom when messages change
  useEffect(() => {
    if (messagesEndRef.current) {
      messagesEndRef.current.scrollIntoView({ behavior: "smooth" });
    }
  }, [messages]);

  const sendMessage = async () => {
    if (!input.trim()) return;

    const userMessage = { role: "user", content: input, timestamp: new Date() };
    setMessages([...messages, userMessage]);
    setInput("");
    setLoading(true);

    try {
      const response = await fetch("https://degree-dialog-1-1.onrender.com/api/chat/", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: input }),
      });

      if (!response.ok) {
        throw new Error("Failed to fetch response");
      }

      const data = await response.json();
      const botMessage = { role: "bot", content: data.response, timestamp: new Date() };
      setMessages((prev) => [...prev, botMessage]);
    } catch (error) {
      console.error("Error fetching response:", error);
      setMessages((prev) => [
        ...prev,
        { role: "bot", content: "Sorry, something went wrong. Please try again.", timestamp: new Date() },
      ]);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="chatbox-container">
      <div className="chatbox-header">
        <h2 className="mt-4">Degree Dialog Chatbot</h2>
      </div>
      <div className="chatbox-messages">
        {messages.map((msg, index) => (
          <div
            key={index}
            className={`message ${msg.role === "user" ? "user" : "bot"}`}
          >
            <div className="message-content">{msg.content}</div>
            <div className="message-timestamp">
              {new Date(msg.timestamp).toLocaleTimeString()}
            </div>
          </div>
        ))}
        {loading && <div className="typing-indicator">Bot is typing...</div>}
        <div ref={messagesEndRef} />
      </div>
      <div className="chatbox-input">
        <input
          type="text"
          value={input}
          onChange={(e) => setInput(e.target.value)}
          onKeyPress={(e) => e.key === "Enter" && sendMessage()}
          placeholder="Type a message..."
          aria-label="Type your message"
        />
        <button onClick={sendMessage} disabled={loading}>
          Send
        </button>
      </div>
    </div>
  );
};

export default ChatBox;
