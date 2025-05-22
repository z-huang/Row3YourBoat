const Tabs = ({ activeTab, setActiveTab, tabs }) => {
  const tabLabels = {
    count: '今日划水',
    friends: '在划水的朋友',
    ranking: '划水排行榜',
  };

  return (
    <div className="tabs">
      {tabs.map(tab => (
        <button
          key={tab}
          onClick={() => setActiveTab(tab)}
          className={activeTab === tab ? 'active' : ''}
        >
          {tabLabels[tab]}
        </button>
      ))}
    </div>
  );
};

export default Tabs;
