import React, { useEffect, useState } from 'react';
import { getMatchweek, getFixtures, postPredictions, postPoints, getTopPoints, postEvaluation } from './api';
import MatchTable from './components/MatchTable';

function App() {
  const [matchweek, setMatchweek] = useState(1);
  const [allFixtures, setAllFixtures] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [pointsThisWeek, setPointsThisWeek] = useState(0);
  const [totalPoints, setTotalPoints] = useState(0);
  const [totalCorrectScoresPercentage, setTotalCorrectScoresPercentage] = useState(0);
  const [totalCorrectResultsPercentage, setTotalCorrectResultsPercentage] = useState(0);
  const [correctScoresPercentageThisWeek, setCorrectScoresPercentageThisWeek] = useState(0);
  const [correctResultsPercentageThisWeek, setCorrectResultsPercentageThisWeek] = useState(0);
  const [globalTopPoints, setGlobalTop] = useState(0);
  const [globalTop250Points, setGlobalTop250] = useState(0);

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

        const topPtsRes = await getTopPoints();
        const { global_top, global_top_250 } = topPtsRes.data;

        const totalEvaluationRes = await postEvaluation(predictionData);
        console.log(totalEvaluationRes)
        setAllFixtures(fixtureData);
        setPredictions(predictionData);
        setTotalPoints(allPts);
        setGlobalTop(global_top);
        setGlobalTop250(global_top_250);
        setTotalCorrectResultsPercentage(totalEvaluationRes.data.CorrectResults);
        setTotalCorrectScoresPercentage(totalEvaluationRes.data.CorrectScores);
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
      const evaluationRes = await postEvaluation(weekData);
      setCorrectScoresPercentageThisWeek(evaluationRes.data.CorrectScores || 0);
      setCorrectResultsPercentageThisWeek(evaluationRes.data.CorrectResults || 0);
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
    <div className="p-6 max-w-screen-xl mx-auto w-full">
      <h1 className="text-3xl font-bold mb-2">⚽️ EPL Match Result Predictor</h1>

      <p className="mb-6 text-gray-600">
        Visualize match predictions and Superbru scoring
      </p>

      <div className="mb-4 w-full flex items-center flex-wrap gap-4">
        <h2 className="text-xl font-semibold whitespace-nowrap">
          Matchweek {matchweek} Results
        </h2>
        <div className="flex gap-2">
          <button
            onClick={handlePrev}
            disabled={matchweek === 1}
            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
          >
            ⏪ Last
          </button>
          <button
            onClick={handleNext}
            disabled={matchweek === 38}
            className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
          >
            Next ⏩
          </button>
        </div>
      </div>

      <div className="mb-4 w-full flex items-center flex-wrap gap-10">
        <div>
          <h3><strong>This Week's Performance</strong></h3>
          <p>
            Percentage of correct scores: <strong>{correctScoresPercentageThisWeek}%</strong>
          </p>
          <p>
            Percentage of correct results (W/D/L): <strong>{correctResultsPercentageThisWeek}%</strong>
          </p>
          <h3><strong>SuperBru This Week</strong></h3>

          <p>
            Points from predictions: <strong>{pointsThisWeek}</strong>
          </p>
        </div>
        <div>
          <h3><strong>This Season's Performance</strong></h3>
          <p>
            Percentage of correct scores: <strong>{totalCorrectScoresPercentage}%</strong>
          </p>
          <p>
            Percentage of correct results (W/D/L): <strong>{totalCorrectResultsPercentage}%</strong>
          </p>
          <h3><strong>SuperBru This Season</strong></h3>
          <p>
            Points from predictions: <strong>{totalPoints}</strong>
          </p>
          <p>
            Global Top points: <strong>{globalTopPoints}</strong>
          </p>
          <p>
            Global Top 250 points: <strong>{globalTop250Points}</strong>
          </p>
        </div>
      </div>

      <div className="overflow-auto">
        <MatchTable data={filtered} />
      </div>
    </div>
  );
}

export default App;