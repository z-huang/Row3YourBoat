import React, { useState } from 'react';
import { useNavigate } from 'react-router-dom';
import './Login.css';

const Register = () => {
  const [username, setUsername] = useState('');
  const [password, setPassword] = useState('');
  const [confirmPassword, setConfirmPassword] = useState('');
  const [confirmEmail, setConfirmPEmail] = useState('');
  const [email, setEmail] = useState('');
  const [error, setError] = useState('');
  const navigate = useNavigate();

  const handleRegister = (e) => {
    e.preventDefault();

    if (password !== confirmPassword) {
      setError('密碼與確認密碼不一致');
      return;
    }

    // 這邊加上後端API

    console.log('註冊成功！', { username, password });
    navigate('/login');
  };

  return (
    <div className="app-container">
      <div className="login-container">
        <h2>🚣‍♀️ 註冊帳號</h2>
        <form onSubmit={handleRegister}>
          <input
            type="email"
            placeholder="信箱"
            value={confirmEmail}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <input
            type="text"
            placeholder="帳號"
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
          <input
            type="password"
            placeholder="確認密碼"
            value={confirmPassword}
            onChange={(e) => setConfirmPassword(e.target.value)}
            required
          />
          <button type="submit">註冊</button>
          {error && <p className="error">{error}</p>}
        </form>
        <p>
          已經有帳號了嗎？{' '}
          <span className="link" onClick={() => navigate('/login')}>回登入頁</span>
        </p>
      </div>
    </div>
  );
};

export default Register;