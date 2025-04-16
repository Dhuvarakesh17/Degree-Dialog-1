
import Navbar from "../../components/Navbar/Navbar";
import HeroSection from "../../components/HeroSection/HeroSection";
import "./Home.css";

const Home = () => {
  return (
    <div className="home-page">
      <Navbar />
      <HeroSection />
    </div>
  );
};

export default Home;