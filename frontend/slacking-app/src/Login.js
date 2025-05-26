// Login.js
import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Login = ({ onLoginSuccess }) => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleLogin = async (e) => {
    e.preventDefault();

    try {
      const res = await fetch('api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok) {
        onLoginSuccess(); // 通知 App.js 切換畫面
        navigate('/');
      } else {
        setError(data.message || '登入失敗');
      }
    } catch (err) {
      setError('無法連接伺服器');
    }
  };

  return (
    <div className="app-container">
      <div className="login-container">
        <h2>🏖 Slacking 划水Server</h2>
        <form onSubmit={handleLogin}>
          <input
            type="text"
            placeholder="帳號或電子郵件"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="密碼"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button type="submit">登入</button>
          {error && <p className="error">{error}</p>}
        </form>
      </div>
    </div>
  );
};

export default Login;