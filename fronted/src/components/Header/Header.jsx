import "./Header.css";
import logoSvg from "../../assets/img/logotip.svg";

const Header = () => {
  return (
    <header className="header">
      <div className="container">
        <div className="logo-wrapper">
          <img src={logoSvg} alt="Mocky Logo" className="header-logo" />
          <span className="logo-text">Mocky</span>
        </div>

        <nav className="nav-menu">
          <a href="#">частые вопросы</a>
          <a href="#">возможности</a>
          <a href="#">цены</a>
          <button className="login-button">ВОЙТИ</button>
        </nav>
      </div>
    </header>
  );
};

export default Header;
