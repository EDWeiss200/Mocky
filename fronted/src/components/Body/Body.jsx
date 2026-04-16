import "./Body.css";
import starsImage from "../../assets/img/starsgroup.svg";
import sendIcon from "../../assets/img/send.svg";
import logochat from "../../assets/img/logochat.svg";
import PDfImage from "../../assets/img/pdfchat.svg";
import firsteclipse from "../../assets/img/eclipse1.svg";
import secondeclipse from "../../assets/img/eclipse2.svg";

const Body = () => {
  return (
    <div className="section-wrapper">
      {/* 1. ГЛАВНЫЙ ЭКРАН */}
      <div className="container hero-content">
        <div className="text-block">
          <h1 className="hero-title">
            Твой персональный <br /> ИИ–интервьюер
          </h1>
          <p className="hero-subtitle">
            Ошибайся, учись и закрывай проблемы в знаниях с <br />
            умным ИИ собеседником
          </p>
          <div className="btn-hero">
            <button className="btn-hero_startfree">Начать бесплатно</button>
            <button className="btn-hero_infomore">узнать больше</button>
          </div>
        </div>
        <div className="image-block">
          <img src={starsImage} alt="3D Stars Group" className="hero-stars" />
        </div>
      </div>

      {/* 2. ЧЕРНЫЙ БЛОК С КАРТОЧКАМИ */}
      <div className="feature-block">
        <h2 className="feature-title">Начни путь к новой профессии</h2>

        <div className="feature-cards">
          <div className="first-step-card">
            <div className="first-step-number">1</div>
            <h3 className="first-step-title">Умный анализ резюме</h3>
            <p className="first-step-description">
              Загрузи свое резюме, и ИИ <br /> мгновенно подберет вопросы <br />{" "}
              именно под твой стек <br /> технологий и опыт
            </p>
          </div>

          <div className="second-step-card">
            <div className="second-step-number">2</div>
            <h3 className="second-step-title">
              Живой диалог <br /> с ИИ
            </h3>
            <p className="second-step-description">
              Отвечай на каверзные вопросы <br /> в режиме реального времени и{" "}
              <br /> тренируй навыки устного <br /> технического общения
            </p>
          </div>

          <div className="third-step-card">
            <div className="third-step-number">3</div>
            <h3 className="third-step-title">
              Детальный <br /> фидбек
            </h3>
            <p className="third-step-description">
              Получай итоговый балл и <br /> подробный разбор ответов с <br />{" "}
              рекомендациями, что именно <br /> стоит подтянуть
            </p>
          </div>
        </div>
      </div>

      {/* 3. ДИЗАЙНЕРСКИЙ БЛОК ЧАТА */}
      <div className="chat-visual-section">
        <div className="ai-chat-card">
          {/* Запрос пользователя (вверху справа) */}
          <div className="mock-row user-side">
            <div className="resume-label">
              <span>резюме</span>
              <img src={PDfImage} alt="PDF" className="pdf-svg-icon" />
            </div>
            <p className="mock-user-text">
              Проанализируй моё резюме <br /> и дай справедливый отзыв
            </p>
          </div>

          {/* Ответ ИИ (по центру слева) */}
          <div className="mock-row ai-side">
            <div className="ai-label">
              <img src={logochat} alt="Logochat" className="send-svg" />
              <h4>Анализ</h4>
            </div>
            <p className="mock-ai-text">
              Конечно, я детально изучил твоё резюме и <br /> выделили некоторые
              проблемы умный текс <br />т умный текст умный текст умный текст
              умный текст умный текст умный текст умный текст умный текст умный
              текст умный текст умный текст
            </p>
          </div>

          {/* Строка ввода (внизу) */}
          <div className="mock-input-field">
            <span>Спросите Mocky</span>
            <div className="mock-send-circle">
              <img src={sendIcon} alt="Send" className="send-svg" />
            </div>
          </div>
        </div>
      </div>
      <div className="chat-pagination">
        <img src={firsteclipse} alt="dot" className="pj-dot" />
        <img src={secondeclipse} alt="dot" className="pj-dot" />
      </div>
      <div className="training-info-right">
        <h2 className="training-title">
          Тренируйся с <br /> современным ИИ
        </h2>
        <p className="training-subtitle">
          Ошибайся, учись и закрывай проблемы в <br /> знаниях с умным ИИ
          собеседником.
        </p>

        <div className="mini-cards-row">
          {/* Карточка: Анализ резюме */}
          <div className="mini-card bordered">
            <h3 className="mini-card-title">Анализ резюме</h3>
            <p className="mini-card-text">
              ИИ разберёт резюме, выделит твои сильные и слабые места и
              подскажет, на что обратить внимание.
            </p>
          </div>

          {/* Карточка: Живой диалог */}
          <div className="mini-card">
            <h3 className="mini-card-title">живой диалог</h3>
            <p className="mini-card-text">
              Отвечай на вопросы ИИ, тренируй навыки устного технического
              общения
            </p>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Body;
