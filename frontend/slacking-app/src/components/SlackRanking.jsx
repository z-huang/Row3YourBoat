const SlackRanking = ({ ranking }) => (
  <div className="ranking-wrapper">
    <table className="ranking-table">
      <thead>
        <tr>
          <th>名次</th>
          <th>名字</th>
          <th>划水次數</th>
        </tr>
      </thead>
      <tbody>
        {ranking.map((r, index) => (
          <tr key={r.name}>
            <td>{index + 1}</td>
            <td>{r.name}</td>
            <td>{r.count}</td>
          </tr>
        ))}
      </tbody>
    </table>
  </div>
);

export default SlackRanking;
