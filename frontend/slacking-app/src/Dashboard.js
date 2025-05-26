import React, { useState, useEffect } from "react";
import {
  BrowserRouter as Router,
  Routes,
  Route,
  useNavigate,
} from "react-router-dom";
import './Dashboard.css';

// component加入
import Tabs from './components/Tabs';
import MySlackCount from './components/MySlackCount';
import FriendsBoat from './components/FriendsBoat';
import SlackRanking from './components/SlackRanking';

// DashBoard 主架構
function Home() {
  const navigate = useNavigate();

  // 加上 Tabs 的狀態
  const [activeTab, setActiveTab] = useState("count");
  const [mode, setMode] = useState(null);
  const [slackData, setSlackData] = useState({
    myCount: 0,
    onlineFriends: [],
    rankingTop10: [],
  });

   const fetchMyToday = async () => {
    const res = await fetch("/api/stats/slack/me/today", { credentials: "include" });
    if (!res.ok) throw new Error("fetch /me/today 失敗");
    return res.json(); // { user_id, count, total_minutes }
  };
  const fetchUsersToday = async () => {
    const res = await fetch("/api/stats/slack/users/today");
    if (!res.ok) throw new Error("fetch /users/today 失敗");
    return res.json(); // [ { user_id, count, total_minutes }, … ]
  };
  const fetchTodayTop10 = async () => {
    const res = await fetch("/api/stats/slack/users/today/top10");
    if (!res.ok) throw new Error("fetch /users/today/top10 失敗");
    return res.json(); // 前十名
  };

  useEffect(() => {
    async function loadData() {
      try {
        if (activeTab === "count") {
          const me = await fetchMyToday();
          setSlackData((prev) => ({ ...prev, myCount: me.count }));
        }
        if (activeTab === "friends") {
          const users = await fetchUsersToday();
          setSlackData((prev) => ({
            ...prev,
            onlineFriends: users.map((u) => `#${u.user_name}`),
          }));
        }
        if (activeTab === "ranking") {
          const top10 = await fetchTodayTop10();
          setSlackData((prev) => ({
            ...prev,
            rankingTop10: top10.map((u) => ({
              name: u.user_name, 
              count: u.total_minutes,
            })),
          }));
        }
      } catch (err) {
        console.error("取得 Slack 資料失敗", err);
      }
    }
    loadData();
  }, [activeTab]);

  // 設定可視分頁；這邊無論模式為何都可以看到
  const visibleTabs = ["count", "friends", "ranking"];

  return (
    <div className="dashboard-container">
      <h1 className="welcome-text">🏖 Slacking 划水Server</h1>
      <div className="top-button-group">
        <button className="mode-setting-button" onClick={() => navigate("/mspage")}>
          Mode setting
        </button>
        <button className="blockUrl-setting-button" onClick={() => navigate("/bspage")}>
          Block setting
        </button>
        <button className="mail-button" onClick={() => window.location.href = "mailto:admin@example.com"}>
          ✉️ 寄信
        </button>
      </div>

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
}

function ModeSetting({ mode, setMode }) {
  const navigate = useNavigate();
  const [isUpdating, setIsUpdating] = useState(false);
  const [selectedMode, setSelectedMode] = useState(mode);

  const modes = ["A", "B", "C"];
  const modeLabels = {
    A: "直接模式",
    B: "監督模式",
    C: "混合模式",
  };

  async function handleConfirm() {
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
      alert("更新模式失敗，請稍後再試");
      console.error(err);
    } finally {
      setIsUpdating(false);
    }
  }

  return (
    <div className="mode-setting-container">
      <h1>Mode setting</h1>
      <p>
        🔍 目前模式：
        <strong>{mode ? modeLabels[mode] : "載入中..."}</strong>
      </p>
  
      {/* 將 label 與 select 放在同一行 */}
      <div className="mode-select-row">
        <label htmlFor="modeSelect">設定新的 Mode：</label>
        <select
          id="modeSelect"
          value={selectedMode}
          onChange={(e) => setSelectedMode(e.target.value)}
          disabled={isUpdating || !mode}
        >
          {modes.map((m) => (
            <option key={m} value={m}>
              {modeLabels[m]}
            </option>
          ))}
        </select>
      </div>
  
      <div className="button-group">
        <button className="comfirm-button" onClick={handleConfirm} disabled={isUpdating || !selectedMode}>
          確認更改
        </button>
  
        <button className="back-button" onClick={() => navigate("/")}>
          回前頁
        </button>
      </div>
    </div>
  );
}

function BlockSetting({ blockedSites, setBlockedSites }) {
  const navigate = useNavigate();
  const [newHost, setNewHost] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  // 新增封鎖網址
  async function handleAdd() {
    const host = newHost.trim();
    if (!host) return alert("請輸入網址");

    setIsUpdating(true);
    try {
      const res = await fetch("/api/blocked_sites", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ host }),
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "新增失敗");
      }
      const created = await res.json(); // { id, host }
      setBlockedSites(prev => [...prev, created]);
      setNewHost("");
    } catch (err) {
      console.error(err);
      alert("新增失敗: " + err.message);
    } finally {
      setIsUpdating(false);
    }
  }

  // 刪除封鎖網址
  async function handleDelete(id) {
    if (!window.confirm("確定要刪除這個封鎖網址？")) return;

    setIsUpdating(true);
    try {
      const res = await fetch(`/api/blocked_sites/${id}`, {
        method: "DELETE",
      });
      if (!res.ok) {
        const err = await res.json();
        throw new Error(err.detail || "刪除失敗");
      }
      setBlockedSites(prev => prev.filter(s => s.id !== id));
    } catch (err) {
      console.error(err);
      alert("刪除失敗: " + err.message);
    } finally {
      setIsUpdating(false);
    }
  }

  return (
    <div className="block-setting-container">
      <h1>Block setting</h1>

      <h3>目前被封鎖的網址</h3>
      {blockedSites.length === 0 ? (
        <p className="no-blocked-url">尚無封鎖網址</p>
      ) : (
        <ul>
          {blockedSites.map(site => (
            <li key={site.id}>
              {site.host}
              <button
                onClick={() => handleDelete(site.id)}
                disabled={isUpdating}
                className="delete-button"
              >
                刪除
              </button>
            </li>
          ))}
        </ul>
      )}

      <div className="block-add-url">
        <h3 className="add-url-title">新增封鎖網址：</h3>
        <div className="input-button-row">
          <input
            type="text"
            value={newHost}
            onChange={e => setNewHost(e.target.value)}
            placeholder="輸入網址，如 example.com"
            disabled={isUpdating}
          />
          <button
            onClick={handleAdd}
            disabled={isUpdating || !newHost.trim()}
          >
            新增
          </button>
        </div>
      </div>

      <div className="back-button-wrapper">
        <button className="back-button" onClick={() => navigate("/")}>
          回前頁
        </button>
      </div>
    </div>
  );
}

// ⬇ 包起來一層 State 管理
function State() {
  const [mode, setMode] = useState("A");
  const [blockedSites, setBlockedSites] = useState([]);

  useEffect(() => {
    async function fetchState() {
      try {
        const curMode = await fetch("/api/mode");
        const dataMode = await curMode.json();
        setMode(dataMode.access_mode);

        const res = await fetch("/api/blocked_sites");
        const data = await res.json(); // [{id,host},…]
        setBlockedSites(data);
      } catch (error) {
        console.error("載入資料錯誤", error);
      }
    }
    fetchState();
  }, []);


  return (
    <Routes>
      <Route path="/" element={<Home />} />
      <Route path="/mspage" element={<ModeSetting mode={mode} setMode={setMode} />} />
      <Route
        path="/bspage"
        element={<BlockSetting blockedSites={blockedSites} setBlockedSites={setBlockedSites} />}
      />
    </Routes>
  );
}

export default function Dashboard() {
  return <State />;
}