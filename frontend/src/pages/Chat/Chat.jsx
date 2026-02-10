import { useState } from "react";
import Navbar from "../../components/Navbar/Navbar";
import ChatBox from "../../components/ChatBox/ChatBox";
import ChatSidebar from "../../components/ChatSidebar/ChatSidebar";
import "./chat.css";

const Chat = () => {
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);

  const handleSessionSelect = (sessionId) => {
    setSelectedSessionId(sessionId);
  };

  const handleNewChat = () => {
    setSelectedSessionId(null);
  };

  const handleSessionCreated = () => {
    // Refresh the sidebar to show the new session
    setRefreshKey((prev) => prev + 1);
  };

  return (
    <div className="chat-page">
      <Navbar />
      <div className="chat-container">
        <ChatSidebar
          key={refreshKey}
          selectedSessionId={selectedSessionId}
          onSessionSelect={handleSessionSelect}
          onNewChat={handleNewChat}
        />
        <ChatBox
          sessionId={selectedSessionId}
          onSessionCreated={handleSessionCreated}
        />
      </div>
    </div>
  );
};

export default Chat;
