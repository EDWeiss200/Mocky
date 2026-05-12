import React, { useState } from 'react';
import './Authorization.css';

import LogoIcon from '../../assets/img/logo.svg';
import GithubIcon from '../../assets/img/github-icon.svg';
import WhiteStarsGroup from '../../assets/img/whiteStarsGroup.svg';

const Authorization = () => {
  const [formData, setFormData] = useState({
    username: '',
    password: ''
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState('');

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
      const formBody = new URLSearchParams();
      formBody.append('username', formData.username);
      formBody.append('password', formData.password);
      
      const response = await fetch('/api/auth/jwt/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/x-www-form-urlencoded',
          'Accept': 'application/json'
        },
        body: formBody,
        credentials: 'include'
      });
      
      const data = await response.json();
      
      if (response.ok) {
        console.log('Authorization successful:', data);
        
        if (data.access_token) {
          localStorage.setItem('access_token', data.access_token);
          localStorage.setItem('token_type', data.token_type || 'bearer');
        }
        
        window.location.href = '/dashboard';
      } else {
        if (data.detail === 'LOGIN_BAD_CREDENTIALS') {
          setError('Неверное имя пользователя или пароль');
        } else if (data.detail === 'LOGIN_USER_NOT_VERIFIED') {
          setError('Пользователь не подтвержден. Проверьте почту.');
        } else {
          setError(data.detail || 'Ошибка входа');
        }
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Не удалось подключиться к серверу');
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubLogin = () => {
    window.location.href = '/api/auth/github/authorize';
  };

  const handleForgotPassword = () => {
    window.location.href = '/forgot-password';
  };

  const handleCreateAccount = () => {
    window.location.href = '/registration';
  };

  return (
    <div className="authorization-page">
      <div className="authorization-container">
        <div 
          className="white-stars-bg"
          style={{ backgroundImage: `url(${WhiteStarsGroup})` }}
        ></div>
        
        <div className="authorization-content">
          <div className="logo-wrapper">
            <img src={LogoIcon} alt="Mocky Logo" className="logo-image" />
          </div>

          <form onSubmit={handleSubmit} className="authorization-form">
            {error && <div className="error-message">{error}</div>}
            
            <div className="input-field">
              <input
                type="text"
                name="username"
                placeholder="имя пользователя"
                value={formData.username}
                onChange={handleChange}
                required
                disabled={loading}
                autoComplete="username"
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
                disabled={loading}
                autoComplete="current-password"
              />
            </div>

            <div className="forgot-password">
              <button 
                type="button" 
                onClick={handleForgotPassword}
                className="forgot-password-btn"
                disabled={loading}
              >
                забыли пароль?
              </button>
            </div>

            <div className="buttons-row">
              <button 
                type="button" 
                onClick={handleGitHubLogin} 
                className="github-button"
                disabled={loading}
              >
                <img src={GithubIcon} alt="GitHub" className="github-icon" />
              </button>
              
              <button 
                type="submit" 
                className="login-button"
                disabled={loading}
              >
                {loading ? 'Вход...' : 'войти'}
              </button>
            </div>
            
            <div className="create-account">
              <button 
                type="button" 
                onClick={handleCreateAccount}
                className="create-account-btn"
                disabled={loading}
              >
                создать аккаунт
              </button>
            </div>
          </form>
        </div>
      </div>
    </div>
  );
};

export default Authorization;