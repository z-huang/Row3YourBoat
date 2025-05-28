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
  const [userInfo, setUserInfo] = useState(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState(null);

  // 2. 首次 mount 時解析 URL 拿 token
  useEffect(() => {
    const fetchUserInfo = async () => {
      try {
        // Get token from URL
        const urlParams = new URLSearchParams(window.location.search);
        const parsedToken = urlParams.get('token');
        console.log('Token from URL:', parsedToken);
        
        if (parsedToken) {
          setToken(parsedToken);
        }
          if (!parsedToken) {
          console.log('No token found in URL');
          setIsLoading(false);
          return;
        }

        // Fetch user info using token
        const apiUrl = `/api/slack-events/token/${parsedToken}`;
        console.log('Making request to:', apiUrl);
        
        try {
          console.log('Starting fetch request...');
          const response = await fetch(apiUrl, {
            method: 'GET',
            headers: {
              'Accept': 'application/json',
              'Content-Type': 'application/json'
            }
          });
          
          console.log('Response received:', {
            status: response.status,
            statusText: response.statusText,
            headers: Object.fromEntries(response.headers.entries())
          });

          if (!response.ok) {
            const errorText = await response.text();
            console.error('Error response body:', errorText);
            throw new Error(`HTTP error! status: ${response.status}, body: ${errorText}`);
          }

          const data = await response.json();
          console.log('Parsed response data:', data);
          
          // Verify data structure
          if (!data.id || !data.user_id || !data.name || !data.url) {
            console.error('Invalid data structure received:', data);
            throw new Error('Invalid data structure received');
          }

          setUserInfo(data);
          // Update slackData with the URL
          setSlackData(prev => ({
            ...prev,
            myURL: data.url
          }));
          console.log('Updated slackData with URL:', data.url);
        } catch (error) {
          console.error('Detailed error:', {
            message: error.message,
            stack: error.stack,
            name: error.name
          });
          setError(error.message);
        }
      } catch (error) {
        console.error('Error in fetchUserInfo:', error);
        setError(error.message);
      } finally {
        setIsLoading(false);
      }
    };

    fetchUserInfo();
  }, []);

  // 3. 在所有 fetch 都加上 Authorization header
  useEffect(() => {
    if (!token || !userInfo) return;  // token 還沒拿到就別叫 API

    let timerId;
    async function loadData() {
      try {
        const headers = { 'Authorization': `Bearer ${token}` };

        if (activeTab === "count") {
        const res = await fetch(
          `/api/stats/slack/user/${userInfo.user_id}/today`,
          { headers }
        );
        if (!res.ok) throw new Error(res.status);
        const me = await res.json();
        setSlackData(prev => ({ ...prev, myCount: me.count }));
      }else if (activeTab === "friends") {
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
  }, [activeTab, token, userInfo]);

  // 根據後端給的 mode 決定要顯示哪些 tab
  const visibleTabs = ['count'];
  if (mode !== 'A') {
    visibleTabs.push('friends', 'ranking');
  }

  return (
    <div className="dashboard-container">
      <h1 className="welcome-text">🏖 Row Row Row Your Boat</h1>
      <div className="top-button-group">
      </div>

      <Tabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        tabs={visibleTabs}
      />

      <div className="content">
        {activeTab === "count" && <MySlackCount count={slackData.myCount} url={slackData.myURL} />}
        {activeTab === "friends" && <FriendsBoat friends={slackData.onlineFriends} />}
        {activeTab === "ranking" && <SlackRanking ranking={slackData.rankingTop10} />}
      </div>
    </div>
  );
};

export default App;
