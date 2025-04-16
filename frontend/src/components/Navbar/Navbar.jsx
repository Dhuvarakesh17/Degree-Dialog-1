import "react";
import "./Navbar.css";

const Navbar = () => {
  return (
    <nav className="navbar">
      <div className="navbar-brand">Degree Dialog</div>
      <div className="navbar-links">
        <a href="/" className="navbar-link">
          Home
        </a>
        <a href="/chat" className="navbar-link">
          Chat
        </a>
      </div>
    </nav>
  );
};

export default Navbar;