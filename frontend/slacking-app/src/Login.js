// src/Login.jsx
import React, { useState } from 'react';
import './Login.css'; // 可以自己設計樣式

const Login = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [error, setError] = useState('');

  const handleLogin = async (e) => {
    e.preventDefault();

    // 假設呼叫後端 API
    try {
      const res = await fetch('https://backend.rrryb.orb.local/api/login', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({ username, password }),
      });

      const data = await res.json();

      if (res.ok) {
        alert('登入成功！');
        // 做轉跳或存 token
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
        <h2>划水伺服器</h2>
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