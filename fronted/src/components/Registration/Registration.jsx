import React, { useState } from 'react';
import './Registration.css';

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
      const response = await fetch('/api/auth/register', {
        method: 'POST',
        headers: { 
          'Content-Type': 'application/json',
          'accept': 'application/json'
        },
        body: JSON.stringify({
          email: formData.email,
          username: formData.username,
          password: formData.password,
          is_active: true,
          is_superuser: false,
          is_verified: false
        }),
        credentials: 'include'
      });
      
      let data = null;
      const contentType = response.headers.get('content-type');
      
      if (contentType && contentType.includes('application/json')) {
        data = await response.json();
      }
      
      if (response.status === 201) {
        console.log('Registration successful:', data);
        window.location.href = '/';
      } else if (response.status === 400) {
        if (data && data.detail === 'REGISTER_USER_ALREADY_EXISTS') {
          setError('Пользователь с таким email или именем уже существует');
        } else {
          setError('Ошибка регистрации. Проверьте введенные данные.');
        }
      } else {
        setError('Ошибка регистрации. Попробуйте позже.');
      }
    } catch (error) {
      console.error('Error:', error);
      setError('Не удается подключиться к серверу. Проверьте интернет-соединение.');
    } finally {
      setLoading(false);
    }
  };

  const handleGitHubLogin = () => {
    window.location.href = '/api/auth/github';
  };

  return (
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
  );
};

export default Registration;