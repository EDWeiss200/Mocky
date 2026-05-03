import React from "react";
import "./Work.css";

// Импорт иконок из папки assets
import logotip from "../assets/img/logotip.svg";
import logoStart from "../assets/img/LogoStart.svg";
import gearwheel from "../assets/img/gearwheel.svg"; // Шестеренка
import bubbles from "../assets/img/bubbles.svg";   // Пузыри (анализ)
import headCheck from "../assets/img/headCheck.svg"; // Голова с галкой

const Work = () => {
  return (
    <div className="work-page">
      <header className="work-header">
        <div className="logo-section">
          <img src={logotip} alt="Mocky" className="main-logo-img" />
          <span className="logo-text">Mocky</span>
        </div>
        <div className="header-right">
          <div className="status-orb"></div>
          <img src={logoStart} alt="Profile" className="profile-img" />
        </div>
      </header>

      <h1 className="page-title">Начало работы</h1>

      <main className="cards-container">
        {/* Карточка 1: Новое собеседование */}
        <section className="work-card">
          <div className="card-image-wrapper">
            <img src={gearwheel} alt="" className="card-main-img gear-img" />
          </div>
          <div className="card-content">
            <h2>Новое собеседование</h2>
            <p>Загрузите резюме, чтобы ии смог его проанализировать и составить подходящие вопросы</p>
          </div>
          <div className="card-footer">
            <button className="action-btn file-btn">
              загрузить файл <span>+</span>
            </button>
          </div>
        </section>

        {/* Карточка 2: Анализ резюме */}
        <section className="work-card">
          <div className="card-image-wrapper">
            <img src={bubbles} alt="" className="card-main-img bubbles-img" />
          </div>
          <div className="card-content">
            <h2>Анализ резюме</h2>
            <p>ИИ разберёт резюме, выделит твои сильные и слабые места и подскажет</p>
          </div>
          <div className="card-footer footer-right">
            <button className="arrow-btn">↗</button>
          </div>
        </section>

        {/* Карточка 3: Собеседование по специальности */}
        <section className="work-card">
          <div className="card-image-wrapper">
            <img src={headCheck} alt="" className="card-main-img head-img" />
          </div>
          <div className="card-content">
            <h2>Собеседование по специальности</h2>
            <p>Вставьте ссылку на вакансию, и ИИ подготовит вопросы на основе требований работодателя</p>
          </div>
          <div className="card-footer">
            <button className="action-btn link-btn">
              вставьте ссылку <span>+</span>
            </button>
          </div>
        </section>
      </main>
    </div>
  );
};

export default Work;