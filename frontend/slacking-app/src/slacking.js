import React, { useState, useEffect } from 'react';
import Tabs from './components/Tabs';
import MySlackCount from './components/MySlackCount';
import FriendsBoat from './components/FriendsBoat';
import SlackRanking from './components/SlackRanking';

const App = () => {
  const [activeTab, setActiveTab] = useState('count');
  const [mode, setMode] = useState(null);
  const [slackData, setSlackData] = useState({
    myCount: 0,
    friendsCounts: [],
    onlineFriends: [],
    rankingTop10: []
  });

  const fetchMyToday = async () => {
    const res = await fetch('/api/stats/slack/me/today', {
      credentials: 'include'
    });
    if (!res.ok) throw new Error('fetch /me/today 失敗');
    return res.json(); // { user_id, count, total_minutes }
  };

  const fetchUsersToday = async () => {
    const res = await fetch('/api/stats/slack/users/today');
    if (!res.ok) throw new Error('fetch /users/today 失敗');
    return res.json(); // [ { user_id, count, total_minutes }, … ]
  };

  const fetchTodayTop10 = async () => {
    const res = await fetch('/api/stats/slack/users/today/top10');
    if (!res.ok) throw new Error('fetch /users/today/top10 失敗');
    return res.json(); // 前十名
  };

  // useEffect(() => {
  // // 暫時模擬從後端取得資料
  // const mockData = {
  //   mode: 'B',
  //   myCount: 7,
  //   friendsCounts: [
  //     { name: '小明', count: 5 },
  //     { name: '阿美', count: 3 },
  //     { name: '我', count: 7 }
  //   ],
  //   onlineFriends: ['小明', '阿美', '我'],
  //   rankingTop10: [
  //     { name: '阿強', count: 10 },
  //     { name: '小美', count: 9 },
  //     { name: '我', count: 7 },
  //     { name: '小明', count: 5 },
  //     { name: '阿美', count: 3 },
  //     { name: '大頭', count: 2 },
  //     { name: '阿良', count: 2 },
  //     { name: '小方', count: 1 },
  //     { name: '阿豹', count: 1 },
  //     { name: '小慧', count: 1 }
  //   ]
  // };

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


  // useEffect(() => {
  //   // 假設 API 是 /api/slack-data
  //   fetch('/api/slack-data')
  //     .then(res => res.json())
  //     .then(data => {
  //       setMode(data.mode);
  //       setSlackData({
  //         myCount: data.myCount,
  //         friendsCounts: data.friendsCounts,
  //         onlineFriends: data.onlineFriends,
  //         rankingTop10: data.rankingTop10
  //       });
  //     })
  //     .catch(err => {
  //       console.error('取得划水資料失敗:', err);
  //     });
  // }, []);

  useEffect(() => {
    async function loadData() {
      try {
        if (activeTab === 'count') {
          const me = await fetchMyToday();
          setSlackData(prev => ({ ...prev, myCount: me.count }));
        }
        if (activeTab === 'friends') {
          const users = await fetchUsersToday();
          setSlackData(prev => ({
            ...prev,
            friendsCounts: users.map(u => ({ name: `#${u.user_id}`, count: u.count })),
            onlineFriends: users.map(u => `#${u.user_id}`)
          }));
        }
        if (activeTab === 'ranking') {
          const top10 = await fetchTodayTop10();
          setSlackData(prev => ({
            ...prev,
            rankingTop10: top10.map(u => ({
              name: u.user_name, 
              count: u.total_minutes
            }))
          }));
        }
      } catch (err) {
        console.error('取得 Slack 資料失敗', err);
      }
    }
    loadData();
  }, [activeTab]);

  // 根據 mode A 隱藏特定分頁
  const visibleTabs = ['count'];
  if (mode !== 'A') {
    visibleTabs.push('friends', 'ranking');
  }

  return (
    <div className="app">
      <h1>🏖 Slacking 划水 server</h1>

      <Tabs
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        tabs={visibleTabs}
      />

      <div className="content">
        {activeTab === 'count' && <MySlackCount count={slackData.myCount} />}
        {activeTab === 'friends' && <FriendsBoat friends={slackData.onlineFriends} />}
        {activeTab === 'ranking' && <SlackRanking ranking={slackData.rankingTop10} />}
      </div>
    </div>
  );
};

export default App;
