import React, { useEffect, useState } from 'react';
import {
  getSeasons, getSeasonSummary, getSeasonMatchweek,
  getMatchweekData, getTopPoints, getModelEvaluation
} from './api';
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
  const [matchweekData, setMatchweekData] = useState([]);
  const [seasonSummary, setSeasonSummary] = useState(null);
  const [pointsThisWeek, setPointsThisWeek] = useState(0);
  const [globalTopPoints, setGlobalTop] = useState(0);
  const [globalTop250Points, setGlobalTop250] = useState(0);
  const [modelValidationPerf, setModelValidationPerf] = useState([]);
  const [loadingSeason, setLoadingSeason] = useState(true);
  const [loadingWeek, setLoadingWeek] = useState(false);

  // On mount: load available seasons
  useEffect(() => {
    const init = async () => {
      try {
        const res = await getSeasons();
        const seasons = res.data.seasons;
        setAvailableSeasons(seasons);
        setSeason(seasons[seasons.length - 1]);
      } catch (error) {
        console.error('Error fetching seasons', error);
      }
    };
    init();
  }, []);

  // When season changes: fetch summary, current matchweek, leaderboard + model validation
  useEffect(() => {
    if (!season) return;
    const fetchSeasonData = async () => {
      setLoadingSeason(true);
      try {
        const [summaryRes, mwRes, topPtsRes, modelValRes] = await Promise.all([
          getSeasonSummary(season),
          getSeasonMatchweek(season),
          getTopPoints(season),
          getModelEvaluation(),
        ]);
        setSeasonSummary(summaryRes.data);
        setMatchweek(mwRes.data.current_matchweek);
        const { global_top, global_top_250 } = topPtsRes.data;
        setGlobalTop(global_top);
        setGlobalTop250(global_top_250);
        setModelValidationPerf(modelValRes.data);
      } catch (error) {
        console.error('Error fetching season data', error);
      } finally {
        setLoadingSeason(false);
      }
    };
    fetchSeasonData();
  }, [season]);

  // When matchweek changes: fetch just that week's data
  useEffect(() => {
    if (!season || !matchweek) return;
    const fetchWeek = async () => {
      setLoadingWeek(true);
      try {
        const res = await getMatchweekData(season, matchweek);
        setMatchweekData(res.data.matches || []);
        setPointsThisWeek(res.data.week_points || 0);
      } catch (error) {
        console.error('Error fetching matchweek data', error);
      } finally {
        setLoadingWeek(false);
      }
    };
    fetchWeek();
  }, [season, matchweek]);

  const handlePrev = () => { if (matchweek > 1) setMatchweek((w) => w - 1); };
  const handleNext = () => { if (matchweek < 38) setMatchweek((w) => w + 1); };

  const totalPoints = seasonSummary?.superbru_points ?? 0;
  const seasonPerf = seasonSummary?.model_performance ?? [];
  const thisWeekPerf = matchweekData.length > 0 ? [] : []; // computed server-side in summary

  return (
    <div className="p-6 grid w-full">
      <Header />
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

      {loadingSeason ? (
        <div className="flex flex-col items-center justify-center py-24 gap-4 text-gray-500 min-w-full">
          <div className="w-10 h-10 border-4 border-gray-300 border-t-purple-600 rounded-full animate-spin" />
          <p className="text-sm">Loading season data…</p>
        </div>
      ) : (
        <>
          <CollapsibleHeader default_state={true} title={"Performance Stats"} content={
            <div className="mb-4 w-full flex items-center flex-wrap gap-10">
              <div>
                <h3><strong>Model Performance (Validation)</strong></h3>
                <ModelPerformanceStats data={modelValidationPerf} />
              </div>
              <div>
                <h3><strong>This Season's Performance</strong></h3>
                <ModelPerformanceStats data={seasonPerf} />
              </div>
            </div>
          } />

          <SuperbruPoints
            pointsThisWeek={pointsThisWeek}
            totalPoints={totalPoints}
            globalTopPoints={globalTopPoints}
            globalTop250Points={globalTop250Points}
          />

          <div id="predictions" className="overflow-auto min-w-full">
            <MatchweekMenuBar
              matchweek={matchweek}
              handlePrev={handlePrev}
              handleNext={handleNext}
              handleJump={setMatchweek}
            />
            {loadingWeek ? (
              <div className="flex flex-col items-center justify-center py-16 gap-4 text-gray-500 min-w-full">
                <div className="w-10 h-10 border-4 border-gray-300 border-t-purple-600 rounded-full animate-spin" />
                <p className="text-sm">Loading matchweek {matchweek}…</p>
              </div>
            ) : (
              <MatchTable data={matchweekData} />
            )}
          </div>
        </>
      )}

      <div id="model">
        <ModelExplanation />
      </div>
      <Footer />
    </div>
  );
}

export default App;
