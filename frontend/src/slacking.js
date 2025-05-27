import React, { useState, useEffect } from 'react';
import './slacking.css'
import Tabs from './components/Tabs';
import MySlackCount from './components/MySlackCount';
import FriendsBoat from './components/FriendsBoat';
import SlackRanking from './components/SlackRanking';

const App = () => {
  // 1. 多一個 state 來存 token
  const [token, setToken] = useState(null);
  const [activeTab, setActiveTab] = useState('count');
  const [mode, setMode] = useState(null);
  const [slackData, setSlackData] = useState({
    myCount: 0,
    myURL: '',
    friendsCounts: [],
    onlineFriends: [],
    rankingTop10: []
  });

  // 2. 首次 mount 時解析 URL 拿 token
  useEffect(() => {
    const params = new URLSearchParams(window.location.search);
    const t = params.get('token');
    if (t) {
      setToken(t);
      // （可選）如果你有 user/profile API，可以在這裡呼叫：
      fetch('/api/user/from-token', {
        headers: { 'Authorization': `Bearer ${t}` }
      })
        .then(res => res.ok ? res.json() : Promise.reject(res.status))
        .then(profile => {
          // 假設後端回來有 profile.mode，或其他欄位
          setMode(profile.mode);
          // 也可以 setSlackData({ ... , myURL: profile.url })
        })
        .catch(err => console.warn('取 user profile 失敗', err));
    } else {
      console.error('URL 沒有帶 token');
    }
  }, []);

  // 3. 在所有 fetch 都加上 Authorization header
  useEffect(() => {
    if (!token) return;  // token 還沒拿到就別叫 API

    let timerId;
    async function loadData() {
      try {
        const headers = { 'Authorization': `Bearer ${token}` };

        if (activeTab === "count") {
          const res = await fetch("/api/stats/slack/me/today", {
            credentials: "include",
            headers
          });
          if (!res.ok) throw new Error(res.status);
          const me = await res.json();
          setSlackData(prev => ({ ...prev, myCount: me.count }));
        } else if (activeTab === "friends") {
          const res = await fetch("/api/stats/slack/online-friends", {
            credentials: "include",
            headers
          });
          if (!res.ok) throw new Error(res.status);
          const users = await res.json();
          setSlackData(prev => ({ ...prev, onlineFriends: users.map(u => u.name) }));
        } else if (activeTab === "ranking") {
          const res = await fetch("/api/stats/slack/users/today/top10", {
            headers
          });
          if (!res.ok) throw new Error(res.status);
          const top10 = await res.json();
          setSlackData(prev => ({
            ...prev,
            rankingTop10: top10.map(u => ({ name: u.user_name, count: u.count }))
          }));
        }
      } catch (err) {
        console.error("資料更新失敗", err);
      }
    }

    loadData();
    timerId = setInterval(loadData, 30000);
    return () => clearInterval(timerId);
  }, [activeTab, token]);

  // 根據後端給的 mode 決定要顯示哪些 tab
  const visibleTabs = ['count'];
  if (mode !== 'A') {
    visibleTabs.push('friends', 'ranking');
  }

  return (
    <div className="dashboard-container">
      <h1 className="welcome-text">🏖 Row Row Row Your Boat</h1>
      <Tabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        tabs={visibleTabs}
      />
      <div className="content">
        {activeTab === "count" && <MySlackCount count={slackData.myCount} />}
        {activeTab === "friends" && <FriendsBoat friends={slackData.onlineFriends} />}
        {activeTab === "ranking" && <SlackRanking ranking={slackData.rankingTop10} />}
      </div>
    </div>
  );
};

export default App;
