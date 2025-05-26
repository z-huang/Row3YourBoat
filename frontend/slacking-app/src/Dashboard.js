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
  // // 假資料
  // useEffect(() => {
  //   // 暫時模擬從後端取得資料
  //   const mockData = {
  //     mode: 'B',
  //     myCount: 7,
  //     friendsCounts: [
  //       { name: '小明', count: 5 },
  //       { name: '阿美', count: 3 },
  //       { name: '我', count: 7 }
  //     ],
  //     onlineFriends: ['小明', '阿美', '我'],
  //     rankingTop10: [
  //       { name: '阿強', count: 10 },
  //       { name: '小美', count: 9 },
  //       { name: '我', count: 7 },
  //       { name: '小明', count: 5 },
  //       { name: '阿美', count: 3 },
  //       { name: '大頭', count: 2 },
  //       { name: '阿良', count: 2 },
  //       { name: '小方', count: 1 },
  //       { name: '阿豹', count: 1 },
  //       { name: '小慧', count: 1 }
  //     ]
  //   };
  
  //   // 模擬 delay
  //   setTimeout(() => {
  //     setMode(mockData.mode);
  //     setSlackData({
  //       myCount: mockData.myCount,
  //       friendsCounts: mockData.friendsCounts,
  //       onlineFriends: mockData.onlineFriends,
  //       rankingTop10: mockData.rankingTop10
  //     });
  //   }, 500); // 模擬 500ms delay
  // }, []);

  // 加入 fetch slack data API
  // useEffect(() => {
  //   fetch("/api/slack-data")
  //     .then((res) => res.json())
  //     .then((data) => {
  //       setSlackData({
  //         myCount: data.myCount,
  //         onlineFriends: data.onlineFriends,
  //         rankingTop10: data.rankingTop10,
  //       });
  //     })
  //     .catch((err) => {
  //       console.error("取得划水資料失敗:", err);
  //     });
  // }, []);


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
        body: JSON.stringify({ mode: selectedMode }),
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

function BlockSetting({ blockedUrls, setBlockedUrls }) {
  const navigate = useNavigate();
  const [newUrl, setNewUrl] = useState("");
  const [isUpdating, setIsUpdating] = useState(false);

  async function handleAdd() {
    const trimmedUrl = newUrl.trim();
    if (!trimmedUrl) return alert("請輸入網址");

    setIsUpdating(true);
    try {
      const res = await fetch("/api/add-blocked-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: trimmedUrl }),
      });
      if (!res.ok) throw new Error("新增失敗");

      setBlockedUrls([...blockedUrls, trimmedUrl]);
      setNewUrl("");
    } catch (err) {
      console.error(err);
      alert("新增失敗，請稍後再試");
    } finally {
      setIsUpdating(false);
    }
  }

  async function handleDelete(urlToDelete) {
    setIsUpdating(true);
    try {
      const res = await fetch("/api/remove-blocked-url", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ url: urlToDelete }),
      });
      if (!res.ok) throw new Error("刪除失敗");

      setBlockedUrls(blockedUrls.filter((url) => url !== urlToDelete));
    } catch (err) {
      console.error(err);
      alert("刪除失敗，請稍後再試");
    } finally {
      setIsUpdating(false);
    }
  }

  return (
    <div className="block-setting-container">
      <h1>Block setting</h1>
  
      <h3>目前被封鎖的網址</h3>
  
      {/* ✅ 狀態提示要獨立放，避免被左對齊拉偏 */}
      {blockedUrls.length === 0 ? (
        <p className="no-blocked-url">尚無封鎖網址</p>
      ) : (
        <ul>
          {blockedUrls.map((url, idx) => (
            <li key={idx}>
              {url}
              <button
                onClick={() => handleDelete(url)}
                disabled={isUpdating}
                className="delete-button"
              >
                刪除
              </button>
            </li>
          ))}
        </ul>
      )}
  
      {/* 新增網址區塊 */}
      <div className="block-add-url">
        <h3 className="add-url-title">新增封鎖網址：</h3>
        <div className="input-button-row">
          <input
            type="text"
            value={newUrl}
            onChange={(e) => setNewUrl(e.target.value)}
            placeholder="輸入網址，如 example.com"
            disabled={isUpdating}
          />
          <button
            onClick={handleAdd}
            disabled={isUpdating || !newUrl.trim()}
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
  const [blockedUrls, setBlockedUrls] = useState([]);

  useEffect(() => {
    async function fetchState() {
      try {
        const curMode = await fetch("/api/curMode");
        const dataMode = await curMode.json();
        setMode(dataMode.mode);

        const curBlockedUrls = await fetch("/api/blocked_sites");
        const dataBlockedUrls = await curBlockedUrls.json();
        setBlockedUrls(dataBlockedUrls.urls);
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
        element={<BlockSetting blockedUrls={blockedUrls} setBlockedUrls={setBlockedUrls} />}
      />
    </Routes>
  );
}

export default function Dashboard() {
  return <State />;
}
