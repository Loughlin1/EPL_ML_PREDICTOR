import React, { useEffect, useState } from 'react';
import { getMatchweek, getSeasons, getFixtures, postPredictions, postPoints, getTopPoints, postEvaluation, getModelEvaluation } from './api';
import Header from './components/Header';
import MatchweekMenuBar from './components/MatchweekMenuBar';
import MatchTable from './components/MatchTable';
import ModelPerformanceStats from './components/ModelPerformanceStats';
import SuperbruPoints from './components/SuperbruPoints';
import ModelExplanation from './components/ModelExplanation';
import CollapsibleHeader from './components/CollapsibleHeader';
import Footer from './components/Footer';

function App() {
  const [season, setSeason] = useState(null);
  const [availableSeasons, setAvailableSeasons] = useState([]);
  const [matchweek, setMatchweek] = useState(1);
  const [allFixtures, setAllFixtures] = useState([]);
  const [predictions, setPredictions] = useState([]);
  const [pointsThisWeek, setPointsThisWeek] = useState(0);
  const [totalPoints, setTotalPoints] = useState(0);
  const [totalPredictonsEvaluation, setTotalPredictionsEvaluation] = useState([]);
  const [thisWeekPredictonsEvaluation, setThisWeekPredictionsEvaluation] = useState([]);
  const [globalTopPoints, setGlobalTop] = useState(0);
  const [globalTop250Points, setGlobalTop250] = useState(0);
  const [modelValidationPerf, setModelValidationPerf] = useState([]);
  const [loading, setLoading] = useState(true);

  // On mount: load available seasons then trigger the main data fetch
  useEffect(() => {
    const init = async () => {
      try {
        const seasonsRes = await getSeasons();
        const seasons = seasonsRes.data.seasons;
        setAvailableSeasons(seasons);
        // Default to the latest season
        const latest = seasons[seasons.length - 1];
        setSeason(latest);
      } catch (error) {
        console.error('Error fetching seasons', error);
      }
    };
    init();
  }, []);

  // Re-fetch fixtures + predictions whenever the selected season changes
  useEffect(() => {
    if (!season) return;
    const fetchData = async () => {
      setLoading(true);
      try {
        const mwRes = await getMatchweek();
        const mw = mwRes.data.current_matchweek;
        setMatchweek(mw);

        const fixturesRes = await getFixtures(season);
        const fixtureData = fixturesRes.data;

        const predsRes = await postPredictions(fixtureData, season);
        const predictionData = predsRes.data;

        const pointsRes = await postPoints(predictionData);
        const allPts = pointsRes.data.points;

        const topPtsRes = await getTopPoints();
        const { global_top, global_top_250 } = topPtsRes.data;

        const modelValPerf = await getModelEvaluation();
        setModelValidationPerf(modelValPerf.data);

        const totalEvaluationRes = await postEvaluation(predictionData);
        setTotalPredictionsEvaluation(totalEvaluationRes.data)
        setAllFixtures(fixtureData);
        setPredictions(predictionData);
        setTotalPoints(allPts);
        setGlobalTop(global_top);
        setGlobalTop250(global_top_250);
      } catch (error) {
        console.error('Error fetching data', error);
      } finally {
        setLoading(false);
      }
    };

    fetchData();
  }, [season]);

  const filtered = predictions.filter((p) => p.week === matchweek);

  const updateWeekPoints = async (weekData) => {
    try {
      const res = await postPoints(weekData);
      setPointsThisWeek(res.data.points || 0);
      const evaluationRes = await postEvaluation(weekData);
      setThisWeekPredictionsEvaluation(evaluationRes.data || []);
    } catch {
      setPointsThisWeek(0);
    }
  };

  useEffect(() => {
    if (predictions.length > 0) {
      const weekData = predictions.filter((p) => p.week === matchweek);
      updateWeekPoints(weekData);
    }
  }, [matchweek, predictions]);

  const handlePrev = (matchweek) => {
    if (matchweek > 1) setMatchweek((prev) => prev - 1);
  };

  const handleNext = (matchweek) => {
    if (matchweek < 38) setMatchweek((prev) => prev + 1);
  };

  return (
    <div className="p-6 grid w-full">
      <Header></Header>
      <div className="flex items-center justify-between flex-wrap gap-4 mb-2">
        <h1 className="text-3xl font-bold">⚽️ EPL Match Result Predictor</h1>
        {availableSeasons.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-600">Season</label>
            <select
              value={season || ''}
              onChange={(e) => setSeason(e.target.value)}
              className="px-3 py-2 border border-gray-300 rounded bg-white hover:border-gray-400 cursor-pointer text-sm"
            >
              {availableSeasons.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}
      </div>
      <p className="mb-6 text-gray-600">
        Visualize match predictions and Superbru scoring
      </p>
      <CollapsibleHeader default_state={true} title={"Performance Stats"} content={
        <div className="mb-4 w-full flex items-center flex-wrap gap-10">
          <div>
            <h3><strong>Model Performance (Validation)</strong></h3>
            <ModelPerformanceStats data={modelValidationPerf} />
          </div>
          <div>
            <h3><strong>This Week's Performance</strong></h3>
            <ModelPerformanceStats data={thisWeekPredictonsEvaluation} />
          </div>
          <div>
            <h3><strong>This Season's Performance</strong></h3>
            <ModelPerformanceStats data={totalPredictonsEvaluation} />
          </div>
        </div>
      } />
      <SuperbruPoints pointsThisWeek={pointsThisWeek} totalPoints={totalPoints} globalTopPoints={globalTopPoints} globalTop250Points={globalTop250Points}/>
      <div id="predictions" className="overflow-auto min-w-full">
        <MatchweekMenuBar matchweek={matchweek} handlePrev={handlePrev} handleNext={handleNext} handleJump={setMatchweek}/>
        {loading ? (
          <div className="flex flex-col items-center justify-center py-16 gap-4 text-gray-500 min-w-full">
            <div className="w-10 h-10 border-4 border-gray-300 border-t-purple-600 rounded-full animate-spin" />
            <p className="text-sm">Loading fixtures and predictions…</p>
          </div>
        ) : (
          <MatchTable data={filtered} />
        )}
      </div>
      <div id="model">
        <ModelExplanation />
      </div>
      <Footer />
    </div>
  );
}

export default App;