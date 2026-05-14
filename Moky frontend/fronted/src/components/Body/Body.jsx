import React, { useState } from "react";
import "./Body.css";

// Импорты ассетов
import starsImage from "../../assets/img/starsgroup.svg";
import sendIcon from "../../assets/img/send.svg";
import logochat from "../../assets/img/logochat.svg";
import PDfImage from "../../assets/img/pdfchat.svg";
import firsteclipse from "../../assets/img/eclipse1.svg";
import secondeclipse from "../../assets/img/eclipse2.svg";
import strelka from "../../assets/img/selectvector.svg";
import star1 from "../../assets/img/star1.svg";
import star2 from "../../assets/img/star2.svg";
import star3 from "../../assets/img/star3.svg";

const Body = () => {
  const faqData = [
    {
      id: 0,
      title: (
        <>
          Что такое Mocky и как это <br /> работает?
        </>
      ),
      cardTitle: "Что такое Mocky",
      description:
        "Mocky — это  ИИ-тренажер для подготовки к техническим и софт-скилл интервью. Он анализирует ваш опыт и помогает закрыть пробелы в знаниях, имитируя реальное собеседование",
    },
    {
      id: 1,
      title: "Это бесплатно?",
      cardTitle: "Это бесплатно?",
      description:
        "Да, у нас есть базовый тариф, который позволяет пройти пробную сессию с ИИ бесплатно",
    },
    {
      id: 2,
      title: (
        <>
          Как ИИ понимает, о чем меня <br /> спрашивать?
        </>
      ),
      cardTitle: "Как это работает?",
      description:
        "Алгоритм анализирует ваше резюме и указанный стек технологий, подбирая вопросы, которые чаще всего задают на реальных интервью для вашего уровня",
    },
    {
      id: 3,
      title: (
        <>
          Могу ли я выбрать <br /> конкретную роль (например, <br /> Frontend
          или DevOps)?
        </>
      ),
      cardTitle: "Выбор роли",
      description:
        "Вы можете выбрать любое направление. ИИ адаптирует вопросы под специфику выбранной профессии, будь то Frontend, Backend или DevOps",
    },
    {
      id: 4,
      title: (
        <>
          Что если я не знаю ответ на <br /> вопрос ИИ?
        </>
      ),
      cardTitle: "Если нет ответа",
      description:
        "Это часть обучения! ИИ зафиксирует пробел, а в конце сессии даст правильный ответ и объяснит тему, чтобы вы были готовы к этому вопросу в будущем",
    },
  ];

  const [activeIndex, setActiveIndex] = useState(0);

  return (
    <div className="section-wrapper">
      {/* 1. ГЛАВНЫЙ ЭКРАН (HERO) */}
      <div className="container hero-content">
        <div className="text-block">
          <h1 className="hero-title">
            Твой персональный <br /> ИИ–интервьюер
          </h1>
          <p className="hero-subtitle">
            Ошибайся, учись и закрывай проблемы в знаниях с <br /> умным ИИ
            собеседником
          </p>
          <div className="btn-hero">
            <button className="btn-hero_startfree">Начать бесплатно</button>
          </div>
        </div>
        <div className="image-block">
          <img src={starsImage} alt="3D Stars Group" className="hero-stars" />
        </div>
      </div>

      {/* 2. БЛОК С ШАГАМИ */}
      <div className="feature-block">
        <h2 className="feature-title">Начни путь к новой профессии</h2>
        <div className="feature-cards">
          <div className="first-step-card">
            <div className="first-step-number">1</div>
            <h3 className="first-step-title">Умный анализ резюме</h3>
            <p className="first-step-description">
              Загрузи свое резюме, и ИИ мгновенно подберет вопросы именно под
              твой стек технологий и опыт
            </p>
          </div>
          <div className="second-step-card">
            <div className="second-step-number">2</div>
            <h3 className="second-step-title">
              Живой диалог <br /> с ИИ
            </h3>
            <p className="second-step-description">
              Отвечай на каверзные вопросы в режиме реального времени и тренируй
              навыки устного технического общения
            </p>
          </div>
          <div className="third-step-card">
            <div className="third-step-number">3</div>
            <h3 className="third-step-title">
              Детальный <br /> фидбек
            </h3>
            <p className="third-step-description">
              Получай итоговый балл и подробный разбор ответов с рекомендациями,
              что именно стоит подтянуть
            </p>
          </div>
        </div>
      </div>

      {/* 3. ИНТЕРАКТИВНЫЙ БЛОК (ЧАТ + ТРЕНИРОВКА) */}
      <div id="features" className="main-interactive-container">
        <div className="chat-visual-wrapper">
          <div className="chat-visual-section">
            <div className="ai-chat-card">
              <div className="mock-row user-side">
                <div className="resume-label">
                  <span>Резюме</span>
                  <img src={PDfImage} alt="PDF" className="pdf-svg-icon" />
                </div>
                <p className="mock-user-text">
                  Проанализируй моё резюме
                  <br />и дай справедливый отзыв
                </p>
              </div>
              <div className="mock-row ai-side">
                <div className="ai-label">
                  <img src={logochat} alt="Logochat" className="send-svg" />
                  <h4>Анализ</h4>
                </div>
                <p className="mock-ai-text">
                  Конечно, я детально изучил твоё резюме и <br /> выделили
                  некоторые проблемы умный текст...
                </p>
              </div>
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
            <div className="mini-card bordered">
              <h3 className="mini-card-title">Анализ резюме</h3>
              <p className="mini-card-text">
                ИИ разберёт резюме, выделит твои сильные и слабые места и
                подскажет, на что обратить внимание
              </p>
            </div>
            <div className="mini-card">
              <h3 className="mini-card-title">Живой диалог</h3>
              <p className="mini-card-text">
                Отвечай на вопросы ИИ, тренируй навыки устного технического
                общения
              </p>
            </div>
          </div>
        </div>
      </div>

      {/* 4. СЕКЦИЯ ТАРИФОВ */}
      <section id="prices" className="plans-section">
        <h2 className="plans-main-title">Планы подписки</h2>
        <div className="plans-cards-container">
          <div className="plan-card">
            <div className="plan-card-top">
              <h3 className="plan-tag">free</h3>
              <p className="plan-subtitle">
                попробуй Mocky <br /> бесплатно
              </p>
              <div className="plan-smart-text">
                Базовый доступ к ИИ-интервью
              </div>
            </div>
            <div className="plan-card-bottom">
              <div className="price-row">
                <span className="price-value">$0</span>
                <button className="plan-btn-go">перейти</button>
              </div>
            </div>
          </div>
          <div className="plan-card">
            <div className="plan-card-top">
              <h3 className="plan-tag">pro</h3>
              <p className="plan-subtitle">
                готовься без <br /> ограничений
              </p>
              <div className="plan-smart-text">
                Неограниченные сессии <br /> и глубокий анализ стека
              </div>
            </div>
            <div className="plan-card-bottom">
              <div className="price-row">
                <span className="price-value">$5</span>
                <button className="plan-btn-go">перейти</button>
              </div>
            </div>
          </div>
          <div className="plan-card">
            <div className="plan-card-top">
              <h3 className="plan-tag">max</h3>
              <p className="plan-subtitle">
                получи доступ ко <br /> всем функциям
              </p>
              <div className="plan-smart-text">
                Персональный план развития <br /> и приоритетная поддержка
              </div>
            </div>
            <div className="plan-card-bottom">
              <div className="price-row">
                <span className="price-value">$20</span>
                <button className="plan-btn-go">перейти</button>
              </div>
            </div>
          </div>
        </div>
        <div className="plans-footer-text">
          <p className="get-premium">get premium</p>
          <p className="smart-text-footer">
            инвестируй в свою карьеру <br /> и получи оффер, которого ты достоин
          </p>
        </div>
      </section>

      {/* 5. ИНТЕРАКТИВНЫЕ ВОПРОСЫ */}
      <section className="faq-interactive-section">
        <h2 id="questions" className="faq-main-title">
          Остались вопросы?
        </h2>
        <div className="faq-content-container">
          <div className="faq-menu-side">
            <div className="faq-buttons-column">
              {faqData.map((item, index) => (
                <div key={item.id} className="faq-nav-wrapper">
                  <div
                    className={`faq-arrow-indicator ${activeIndex === index ? "active" : ""}`}
                  >
                    <img src={strelka} alt="arrow" className="faq-arrow-svg" />
                  </div>
                  <button
                    className={`faq-nav-item ${activeIndex === index ? "active" : ""}`}
                    onClick={() => setActiveIndex(index)}
                  >
                    {item.title}
                  </button>
                </div>
              ))}
            </div>
          </div>

          <div className="faq-display-card">
            <h3 className="faq-display-title">
              {faqData[activeIndex].cardTitle}
            </h3>
            <p className="faq-display-description">
              {faqData[activeIndex].description}
            </p>
          </div>
        </div>
      </section>

      {/* --- 6. ФИНАЛЬНЫЙ БЛОК --- */}
      <section className="final-cta-section">
        <img src={star1} alt="star" className="cta-star star-1" />
        <img src={star2} alt="star" className="cta-star star-2" />
        <img src={star3} alt="star" className="cta-star star-3" />

        <div className="cta-container">
          <h2 className="cta-title">Начни путь к работе мечты</h2>
          <p className="cta-subtitle">
            Твоя уверенность на собеседовании начинается здесь <br />
            Присоединяйся к Mocky и получи оффер уже через пару недель
            тренировок
          </p>
          <button className="cta-btn-start">Начать работу</button>
        </div>
      </section>
    </div>
  );
};

export default Body;
