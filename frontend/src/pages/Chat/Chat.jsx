import { useState } from "react";
import Navbar from "../../components/Navbar/Navbar";
import ChatBox from "../../components/ChatBox/ChatBox";
import ChatSidebar from "../../components/ChatSidebar/ChatSidebar";
import "./chat.css";

const Chat = () => {
  const [selectedSessionId, setSelectedSessionId] = useState(null);
  const [refreshKey, setRefreshKey] = useState(0);
  const [isSidebarOpen, setIsSidebarOpen] = useState(false);

  const handleSessionSelect = (sessionId) => {
    setSelectedSessionId(sessionId);
    setIsSidebarOpen(false);
  };

  const handleNewChat = () => {
    setSelectedSessionId(null);
    setIsSidebarOpen(false);
  };

  const handleSessionCreated = (newSessionId) => {
    setSelectedSessionId(newSessionId);
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
          isOpen={isSidebarOpen}
          onClose={() => setIsSidebarOpen(false)}
        />
        <div
          className={`sidebar-overlay ${isSidebarOpen ? "show" : ""}`}
          onClick={() => setIsSidebarOpen(false)}
          aria-hidden={!isSidebarOpen}
        />
        <ChatBox
          sessionId={selectedSessionId}
          onSessionCreated={handleSessionCreated}
          onToggleSidebar={() => setIsSidebarOpen((prev) => !prev)}
          isSidebarOpen={isSidebarOpen}
        />
      </div>
    </div>
  );
};

export default Chat;
