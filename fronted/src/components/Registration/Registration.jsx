import React, { useState } from 'react';
import './Registration.css';

// Импорты
import LogoIcon from '../../assets/img/logo.svg';
import GithubIcon from '../../assets/img/github-icon.svg';
import WhiteStarsGroup from '../../assets/img/whiteStarsGroup.svg';

const Registration = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: ''
  });

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      const response = await fetch('YOUR_BACKEND_URL/api/register', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(formData)
      });
      const data = await response.json();
      if (response.ok) {
        console.log('Registration successful:', data);
      }
    } catch (error) {
      console.error('Error:', error);
    }
  };

  const handleGitHubLogin = () => {
    window.location.href = 'YOUR_BACKEND_URL/api/auth/github';
  };

  return (
    <div className="register-page">
      <div className="register-container">
        {/* Фоновое изображение SVG */}
        <div 
          className="white-stars-bg"
          style={{ backgroundImage: `url(${WhiteStarsGroup})` }}
        ></div>
        
        {/* Контент */}
        <div className="register-content">
          {/* Логотип */}
          <div className="logo-wrapper">
            <img src={LogoIcon} alt="Mocky Logo" className="logo-image" />
          </div>

          {/* Форма регистрации */}
          <form onSubmit={handleSubmit} className="register-form">
            <div className="input-field">
              <input
                type="email"
                name="email"
                placeholder="почта"
                value={formData.email}
                onChange={handleChange}
                required
              />
            </div>

            <div className="input-field">
              <input
                type="text"
                name="username"
                placeholder="имя пользователя"
                value={formData.username}
                onChange={handleChange}
                required
              />
            </div>

            <div className="input-field">
              <input
                type="password"
                name="password"
                placeholder="пароль"
                value={formData.password}
                onChange={handleChange}
                required
              />
            </div>

            <div className="buttons-row">
              <button 
                type="button" 
                onClick={handleGitHubLogin} 
                className="github-button"
              >
                <img src={GithubIcon} alt="GitHub" className="github-icon" />
              </button>
              
              <button type="submit" className="create-button">
                создать
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Registration;