import React from "react";
import "./Start.css";
import axios from 'axios';
import { useNavigate } from "react-router-dom";
import { useState } from "react";
import logotip from "../assets/img/logotip.svg";
import profileIconCard from "../assets/img/profile.svg";
import papka from "../assets/img/papka.svg";
import papka2 from "../assets/img/papka2.svg";
import papka3 from "../assets/img/papka3.svg";
import logoStart from "../assets/img/LogoStart.svg";
import lines from "../assets/img/lines.svg";
import blueline from "../assets/img/blueline.svg";
import blueline2 from "../assets/img/blueline2.svg";

const StartPage = () => {
  const navigate = useNavigate();
  const [activeInterviews, setActiveInterviews] = useState(null);

  const fetchActiveInterviews = async () => {
    try {
      // axios делает запрос и сразу кладет результат в свойство data
      const response = await axios.get('/api/interviews/active');

      setActiveInterviews(response.data); 
      console.log('Получены данные:', response.data);

    } catch (error) {
      // ошибка поймается автоматически, если FastAPI вернет код 4xx или 5xx
      console.error('Ошибка при загрузке собеседований:', error.response?.data || error.message);
    }
  };

  const handleStartClick = () => {
    navigate("/work"); 
  };
  return (
    <div className="start-page">
      {/* Шапка */}
      <header className="start-header">
        <div className="logo-section">
          <img src={logotip} alt="Mocky Logo" className="main-logo-img" />
          <span className="logo-text">Mocky</span>
        </div>
        <div className="profile-section">
          <img src={logoStart} alt="Profile" className="profile-img" />
        </div>
      </header>

      <main className="grid-container">
        {/* Левый блок: Начать собеседование */}
        <section className="card large-card start-interview">
          <img src={blueline} alt="" className="decor-line" />
          <img src={profileIconCard} alt="" className="decor-profile" />
          <div className="card-info">
            <div className="image-box">
              <img
                src={papka}
                alt="Start Interview"
                className="card-illustration"
              />
              <img scr={blueline} className="line-illustration" />
            </div>
            <h2>Начать собеседование</h2>
            <p>Загрузи резюме на основе которого ИИ составит твое интервью</p>
          </div>
          <div className="arrow-circle" onClick={handleStartClick}>
            <span>↗</span>
          </div>
        </section>

        {/* Центральная колонка */}
        <div className="center-column">
          <section className="card small-card archive">
            <div className="card-info">
              <h3>Архив</h3>
              <p>
                Здесь хранятся
                <br />
                ранее начатые
                <br />
                собеседования
              </p>
            </div>
            <img src={papka2} alt="Archive" className="mini-card-img" />
          </section>

          <section className="card small-card active-jobs">
            <div className="card-info">
              <h3>Активные собеседования</h3>
              <p>К ним ещё можно вернуться</p>
            </div>
            <button className="arrow-circle" onClick={fetchActiveInterviews}>↗</button>
          </section>

          <section className="card small-card finished-jobs">
            <div className="card-info">
              <h3>Завершенные собеседования</h3>
              <p>Перечитайте интервью в архиве</p>
            </div>
            <div className="arrow-circle">↗</div>
          </section>
        </div>

        {/* Правый блок: Статистика */}
        <section className="card large-card stats">
          <img src={blueline2} alt="" className="decor-line-stats" />
          <div className="card-info">
            <div className="image-box">
              <img
                src={papka3}
                alt="Statistics"
                className="card-illustration"
              />
            </div>
            <h2>Расширенная статистика</h2>
            <p>Получи доступ к расширенной статистике, приобретая подписку</p>
          </div>
          <div className="arrow-circle">↗</div>
        </section>
      </main>
    </div>
  );
};

export default StartPage;
