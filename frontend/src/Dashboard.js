// Dashboard.js
import React, { useState, useEffect } from "react";
import { Routes, Route, useNavigate } from "react-router-dom";
import './Dashboard.css';
import Tabs from './components/Tabs';
import MySlackCount from './components/MySlackinDB';
import FriendsBoat from './components/FriendsBoat';
import SlackRanking from './components/SlackRanking';

// 首頁
function HomePage({ slackData, activeTab, setActiveTab }) {
  const navigate = useNavigate();
  const visibleTabs = ["count", "friends", "ranking"];

  return (
    <div className="dashboard-container">
      <h1 className="welcome-text">🏖 Row Row Row Your Boat</h1>
      <div className="top-button-group">
        <button className="top-button" onClick={() => navigate("mode_setting")}>Mode setting</button>
        <button className="top-button" onClick={() => navigate("block_setting")}>Block setting</button>
      </div>
      <div className="floating-button-group">
        <button onClick={async () => {
    try {
      const res = await fetch("/api/send_report", { method: "POST" });
      if (!res.ok) throw new Error(await res.text());
      const { detail } = await res.json();
      alert(detail);
    } catch (err) {
      console.error("寄送失敗", err);
      alert("寄送失敗，請稍後再試");
    }
  }}>✉️ 寄信</button>
        <button onClick={() => { sessionStorage.removeItem("isAuthenticated"); navigate("/login"); }}>登出</button>
      </div>

      <Tabs activeTab={activeTab} setActiveTab={setActiveTab} tabs={visibleTabs} />
      <div className="content">
        {activeTab === "count" && <MySlackCount count={slackData.myCount} />}
        {activeTab === "friends" && <FriendsBoat friends={slackData.onlineFriends} />}
        {activeTab === "ranking" && <SlackRanking ranking={slackData.rankingTop10} />}
      </div>
    </div>
  );
}

// Mode setting
export function ModeSetting({ mode, setMode }) {
  const navigate = useNavigate();
  const [isUpdating, setIsUpdating] = useState(false);
  const [selectedMode, setSelectedMode] = useState(mode);
  const modeLabels = { A: "直接模式", B: "監督模式", C: "混合模式" };

  const handleConfirm = async () => {
    setIsUpdating(true);
    try {
      const res = await fetch("/api/mode", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ access_mode: selectedMode }),
      });
      if (!res.ok) throw new Error("更新模式失敗");
      setMode(selectedMode);
    } catch (err) {
      alert("更新失敗");
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="mode-setting-container">
      <h1>Mode setting</h1>
      <p>🔍 目前模式：<strong>{mode ? modeLabels[mode] : "載入中..."}</strong></p>
      <div className="mode-select-row">
        <label htmlFor="modeSelect">設定新的 Mode：</label>
        <select
          id="modeSelect"
          value={selectedMode}
          onChange={(e) => setSelectedMode(e.target.value)}
          disabled={isUpdating || !mode}
        >
          {Object.keys(modeLabels).map((m) => (
            <option key={m} value={m}>{modeLabels[m]}</option>
          ))}
        </select>
      </div>
      <div className="button-group">
        <button onClick={handleConfirm} disabled={isUpdating}>確認更改</button>
        <button onClick={() => navigate("..")}>回前頁</button>
      </div>
    </div>
  );
}

// Block setting
export function BlockSetting({ blockedSites, setBlockedSites }) {
  const navigate = useNavigate();
  const [newHost, setNewHost] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  const handleAdd = async () => {
    const host = newHost.trim();
    if (!host) return alert("請輸入網址");
    setIsUpdating(true);
    try {
      const res = await fetch("/api/blocked_sites", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ host }),
      });
      if (!res.ok) throw new Error("新增失敗");
      const created = await res.json(); // { id, host }
      setBlockedSites(prev => [...prev, created]);
      setNewHost("");
    } catch (err) {
      alert("新增失敗");
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  const handleDelete = async (id) => {
    if (!window.confirm("確定要刪除？")) return;
    setIsUpdating(true);
    try {
      const res = await fetch(`/api/blocked_sites/${id}`, { method: "DELETE" });
      if (!res.ok) throw new Error("刪除失敗");
      setBlockedSites(prev => prev.filter(site => site.id !== id));
    } catch (err) {
      alert("刪除失敗");
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  };

  return (
    <div className="block-setting-container">
      <h1>Block setting</h1>
      {blockedSites.length === 0 ? (
        <p>尚無封鎖網址</p>
      ) : (
        <ul>
          {blockedSites.map(site => (
            <li key={site.id}>
              {site.host}
              <button onClick={() => handleDelete(site.id)} disabled={isUpdating}>刪除</button>
            </li>
          ))}
        </ul>
      )}
      <div className="input-button-row">
        <input
          type="text"
          value={newHost}
          onChange={(e) => setNewHost(e.target.value)}
          placeholder="輸入網址"
          disabled={isUpdating}
        />
        <button className="primary-button" onClick={handleAdd} disabled={isUpdating || !newHost.trim()}>新增</button>
      </div>
      <div class="back-button-wrapper">
        <button className="primary-button" onClick={() => navigate("..")}>回前頁</button>
      </div>
    </div>
  );
}

// 最外層 Dashboard Layout
export default function Dashboard() {
  const [mode, setMode] = useState(null);
  const [blockedSites, setBlockedSites] = useState([]);
  const [activeTab, setActiveTab] = useState("count");
  const [slackData, setSlackData] = useState({
    myCount: 0,
    onlineFriends: [],
    rankingTop10: [],
  });

  useEffect(() => {
    async function fetchState() {
      try {
        const res1 = await fetch("/api/mode");
        const data1 = await res1.json();
        setMode(data1.access_mode);

        const res2 = await fetch("/api/blocked_sites");
        const data2 = await res2.json();
        setBlockedSites(data2);
      } catch (err) {
        console.error("初始化失敗", err);
      }
    }
    fetchState();
  }, []);

  useEffect(() => {
    let timerId;
    async function loadData() {
      try {
        if (activeTab === "count") {
          const res = await fetch("/api/stats/slack/me/today", { credentials: "include" });
          const me = await res.json();
          setSlackData(prev => ({ ...prev, myCount: me.count }));
        } else if (activeTab === "friends") {
          const res = await fetch("/api/stats/slack/online-friends", { credentials: "include" });
          const users = await res.json();
          setSlackData(prev => ({ ...prev, onlineFriends: users.map(u => u.name) }));
        } else if (activeTab === "ranking") {
          const res = await fetch("/api/stats/slack/users/today/top10");
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
  }, [activeTab]);

  return (
    <Routes>
      <Route path="/" element={<HomePage slackData={slackData} activeTab={activeTab} setActiveTab={setActiveTab} />} />
      <Route path="mode_setting" element={<ModeSetting mode={mode} setMode={setMode} />} />
      <Route path="block_setting" element={<BlockSetting blockedSites={blockedSites} setBlockedSites={setBlockedSites} />} />
    </Routes>
  );
}