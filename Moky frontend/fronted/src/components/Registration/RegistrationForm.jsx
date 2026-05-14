import React, { useState } from 'react';
import './RegistrationForm.css';
import axios from 'axios';

import LogoIcon from '../../assets/img/logo.svg';
import GithubIcon from '../../assets/img/github-icon.svg';
import WhiteStarsGroup from '../../assets/img/whiteStarsGroup.svg';

const Registration = () => {
  const [formData, setFormData] = useState({
    email: '',
    username: '',
    password: ''
  });
  
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(false);

  const api = axios.create({
  baseURL: import.meta.env.VITE_API_URL || '',
  withCredentials: true,
  headers: {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
  }
});
  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({
      ...prev,
      [name]: value
    }));
    setError('');
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setError('');
    
    try {
      const response = await api.post('/api/auth/register', {
        email: formData.email,
        username: formData.username,
        password: formData.password,
        is_active: true,
        is_superuser: false,
        is_verified: false
      });
      
      console.log('Registration successful:', response.data);
      window.location.href = '/';
      
    } catch (error) {
      console.error('Error:', error);
      
      if (error.response) {
        switch (error.response.status) {
          case 400:
            if (error.response.data?.detail === 'REGISTER_USER_ALREADY_EXISTS') {
              setError('Пользователь с таким email или именем уже существует');
            } else {
              setError('Ошибка регистрации. Проверьте введенные данные.');
            }
            break;
          case 401:
            setError('Неавторизованный доступ');
            break;
          case 500:
            setError('Ошибка сервера. Попробуйте позже.');
            break;
          default:
            setError('Ошибка регистрации. Попробуйте позже.');
        }
      } else if (error.request) {
        setError('Не удается подключиться к серверу. Проверьте интернет-соединение.');
      } else {
        setError('Ошибка при отправке запроса');
      }
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubLogin = () => {
    window.location.href = '/api/auth/github';
  };
  return (
    <div className="register-page">
      <div className="register-page">
      <div className="register-container">
        <div 
          className="white-stars-bg"
          style={{ backgroundImage: `url(${WhiteStarsGroup})` }}
        ></div>
        
        <div className="register-content">
          <div className="logo-wrapper">
            <img src={LogoIcon} alt="Mocky Logo" className="logo-image" />
          </div>

          <form onSubmit={handleSubmit} className="register-form">
            {error && <div className="error-message">{error}</div>}
            
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
              
              <button type="submit" className="create-button" disabled={loading}>
                {loading ? 'Создание...' : 'создать'}
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  </div>
);
};

export default Registration;