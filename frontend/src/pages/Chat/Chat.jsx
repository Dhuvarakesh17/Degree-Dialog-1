import React from "react";
import Navbar from "../../components/Navbar/Navbar";
import ChatBox from "../../components/ChatBox/ChatBox";
// import "./Chat.css";

const Chat = () => {
  return (
    <div className="chat-page">
      <Navbar />
      <ChatBox />
    </div>
  );
};

export default Chat;