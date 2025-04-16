import "react";
import "./HeroSection.css";

const HeroSection = () => {
  return (
    <div className="hero-section">
      <h1>Welcome to Degree Dialog</h1>
      <p>Your personal chatbot for academic guidance.</p>
      <a href="/chat" className="cta-button">
        Start Chatting
      </a>
    </div>
  );
};

export default HeroSection;