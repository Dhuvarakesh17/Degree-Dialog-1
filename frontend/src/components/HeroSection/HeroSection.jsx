import { useState, useEffect } from "react";
import { Link } from "react-router-dom";
import "./HeroSection.css";

const HeroSection = () => {
  const [isAuthenticated, setIsAuthenticated] = useState(false);

  useEffect(() => {
    const token = localStorage.getItem("access_token");
    setIsAuthenticated(!!token);
  }, []);

  return (
    <div className="hero-section">
      <h1>Welcome to Degree Dialog</h1>
      <p>Your personal AI chatbot for academic guidance.</p>
      <p className="hero-subtitle">
        Get instant answers about college admissions, courses, scholarships, and
        more!
      </p>
      {isAuthenticated ? (
        <Link to="/chat" className="cta-button">
          Start Chatting
        </Link>
      ) : (
        <div className="hero-buttons">
          <Link to="/signup" className="cta-button cta-primary">
            Get Started
          </Link>
          <Link to="/login" className="cta-button cta-secondary">
            Sign In
          </Link>
        </div>
      )}
    </div>
  );
};

export default HeroSection;
