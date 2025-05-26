import './boat.css';

const FriendsBoat = ({ friends }) => (
  <div className="boat-scene">
    <div className="boat">
      {friends.map((name, idx) => (
        <div className="person" key={idx}>{name}</div>
      ))}
    </div>
  </div>
);

export default FriendsBoat;
