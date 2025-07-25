import React, { useEffect, useState } from 'react';
import { getMatchweek, getFixtures, postPredictions, postPoints } from './api';
import MatchTable from './components/MatchTable';

function App() {
  const [matchweek, setMatchweek] = useState(1);
  const [allFixtures, setAllFixtures] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [pointsThisWeek, setPointsThisWeek] = useState(0);
  const [totalPoints, setTotalPoints] = useState(0);

  useEffect(() => {
    const fetchData = async () => {
      try {
        const mwRes = await getMatchweek();
        const mw = mwRes.data.current_matchweek;
        setMatchweek(mw);

        const fixturesRes = await getFixtures();
        const fixtureData = fixturesRes.data;

        const predsRes = await postPredictions(fixtureData);
        const predictionData = predsRes.data;

        const pointsRes = await postPoints(predictionData);
        const allPts = pointsRes.data.points;

        setAllFixtures(fixtureData);
        setPredictions(predictionData);
        setTotalPoints(allPts);
      } catch (error) {
        console.error('Error fetching initial data', error);
      }
    };

    fetchData();
  }, []);

  const filtered = predictions.filter((p) => p.Wk === matchweek);

  const updateWeekPoints = async (weekData) => {
    try {
      const res = await postPoints(weekData);
      setPointsThisWeek(res.data.points || 0);
    } catch {
      setPointsThisWeek(0);
    }
  };

  useEffect(() => {
    if (predictions.length > 0) {
      const weekData = predictions.filter((p) => p.Wk === matchweek);
      updateWeekPoints(weekData);
    }
  }, [matchweek, predictions]);

  const handlePrev = () => {
    if (matchweek > 1) setMatchweek((prev) => prev - 1);
  };

  const handleNext = () => {
    if (matchweek < 38) setMatchweek((prev) => prev + 1);
  };

  return (
    <div className="p-6 max-w-screen-xl mx-auto">
      <h1 className="text-3xl font-bold mb-2">⚽️ EPL Match Result Predictor</h1>
      <p className="mb-6 text-gray-600">
        Visualize match predictions and Superbru scoring
      </p>

      <div className="mb-4 flex justify-between items-center">
        <h2 className="text-xl font-semibold">Matchweek {matchweek} Results</h2>
        <div className="space-x-2">
          <button onClick={handlePrev} disabled={matchweek === 1} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">⏪ Last</button>
          <button onClick={handleNext} disabled={matchweek === 38} className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300">Next ⏩</button>
        </div>
      </div>

      <div className="mb-4">
        <p>Superbru points this week: <strong>{pointsThisWeek}</strong></p>
        <p>Superbru points all weeks so far: <strong>{totalPoints}</strong></p>
      </div>

      <MatchTable data={filtered} />
    </div>
  );
}

export default App;