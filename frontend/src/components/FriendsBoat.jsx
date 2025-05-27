import './boat.css';
import BoatImg from './image/Boat.png';


const FriendsBoat = ({ friends }) => (
  <div className="boat-scene">
    <div className="boat-wrapper">
      <div className="boat">
        <div className="wake"></div>
        <img className="boat-img" src={BoatImg} alt="Boat" />
        {friends.map((name, idx) => (
          <div className="person" key={idx}>{name}</div>
        ))}
      </div>
    </div>
  </div>
);

export default FriendsBoat;

