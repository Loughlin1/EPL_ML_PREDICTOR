const SuperbruPoints = ({pointsThisWeek, totalPoints, globalTopPoints, globalTop250Points}) => {
    return (
      <div className="mb-4 w-full flex gap-10 align-top">
        <div>
          <h3><strong>SuperBru This Week</strong></h3>
          <p>
            Points from predictions: <strong>{pointsThisWeek}</strong>
          </p>
        </div>
        <div>
          <h3><strong>SuperBru This Season</strong></h3>
          <p>
            Points from predictions: <strong>{totalPoints}</strong>
          </p>
        </div>
        <div>
          <h3><strong>SuperBru Leaderboard</strong></h3>
          <p>
            Global Top points: <strong>{globalTopPoints}</strong>
          </p>
          <p>
            Global Top 250 points: <strong>{globalTop250Points}</strong>
          </p>
        </div>
      </div>
    );
};
export default SuperbruPoints;