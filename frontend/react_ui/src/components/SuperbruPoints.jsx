const SuperbruPoints = ({pointsThisWeek, totalPoints, globalTopPoints, globalTop10PctPoints, ukTop10PctPoints}) => {
    return (
      <div className="mb-2 w-full pt-3 flex gap-3 md:gap-10 align-top text-xs sm:text-sm md:text-md lg:text-lg">
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
            Global Top: <strong>{globalTopPoints}</strong>
          </p>
          <p>
            Global Top 10%: <strong>{globalTop10PctPoints}</strong>
          </p>
          <p>
            UK Top 10%: <strong>{ukTop10PctPoints}</strong>
          </p>
        </div>
      </div>
    );
};
export default SuperbruPoints;
