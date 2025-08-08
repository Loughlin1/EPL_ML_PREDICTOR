import React, { useEffect, useState } from 'react';
import { getMatchweek, getFixtures, postPredictions, postPoints, getTopPoints, postEvaluation, getModelEvaluation } from './api';
import Header from './components/Header';
import MatchweekMenuBar from './components/MatchweekMenuBar';
import MatchTable from './components/MatchTable';
import ModelPerformanceStats from './components/ModelPerformanceStats';
import SuperbruPoints from './components/SuperbruPoints';
import ModelExplanation from './components/ModelExplanation';
import CollapsibleHeader from './components/CollapsibleHeader';
import Footer from './components/Footer';

function App() {
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
      setThisWeekPredictionsEvaluation(evaluationRes.data || []);
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

  const handlePrev = (matchweek) => {
    if (matchweek > 1) setMatchweek((prev) => prev - 1);
  };

  const handleNext = (matchweek) => {
    if (matchweek < 38) setMatchweek((prev) => prev + 1);
  };

  return (
    <div className="p-6 grid max-w-screen-xl mx-auto w-full">
      <Header></Header>
      <h1 className="text-3xl font-bold mb-2">⚽️ EPL Match Result Predictor</h1>
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
      <div id="predictions" className="overflow-auto">
        <MatchweekMenuBar matchweek={matchweek} handlePrev={handlePrev} handleNext={handleNext}/>
        <MatchTable data={filtered} />
      </div>
      <div id="model">
        <ModelExplanation />
      </div>
      <Footer />
    </div>
  );
}

export default App;