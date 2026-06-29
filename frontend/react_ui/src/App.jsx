import React, { useEffect, useState } from 'react';
import {
  getSeasons, getSeasonSummary, getSeasonMatchweek,
  getMatchweekData, getTopPoints, getModelEvaluation
} from './api';
import Header from './components/Header';
import MatchweekMenuBar from './components/MatchweekMenuBar';
import MatchTable from './components/MatchTable';
import StatsPanel from './components/StatsPanel';
import ModelExplanation from './components/ModelExplanation';
import Footer from './components/Footer';

function App() {
  const [season, setSeason] = useState(null);
  const [availableSeasons, setAvailableSeasons] = useState([]);
  const [matchweek, setMatchweek] = useState(1);
  const [matchweekData, setMatchweekData] = useState([]);
  const [seasonSummary, setSeasonSummary] = useState(null);
  const [pointsThisWeek, setPointsThisWeek] = useState(0);
  const [globalTopPoints, setGlobalTop] = useState(0);
  const [globalTop10PctPoints, setGlobalTop10Pct] = useState(0);
  const [ukTop10PctPoints, setUkTop10Pct] = useState(0);
  const [loadingSeason, setLoadingSeason] = useState(true);
  const [loadingWeek, setLoadingWeek] = useState(false);

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

  useEffect(() => {
    if (!season) return;
    const fetchSeasonData = async () => {
      setLoadingSeason(true);
      try {
        const [summaryRes, mwRes, topPtsRes] = await Promise.all([
          getSeasonSummary(season),
          getSeasonMatchweek(season),
          getTopPoints(season),
        ]);
        setSeasonSummary(summaryRes.data);
        setMatchweek(mwRes.data.current_matchweek);
        const { global_top, global_top_10_pct, uk_top_10_pct } = topPtsRes.data;
        setGlobalTop(global_top);
        setGlobalTop10Pct(global_top_10_pct);
        setUkTop10Pct(uk_top_10_pct);
      } catch (error) {
        console.error('Error fetching season data', error);
      } finally {
        setLoadingSeason(false);
      }
    };
    fetchSeasonData();
  }, [season]);

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
          <StatsPanel
            seasonSummary={seasonSummary}
            globalTopPoints={globalTopPoints}
            globalTop10PctPoints={globalTop10PctPoints}
            ukTop10PctPoints={ukTop10PctPoints}
            availableSeasons={availableSeasons}
          />

          <div id="predictions" className="overflow-auto min-w-full">
            <MatchweekMenuBar
              matchweek={matchweek}
              handlePrev={handlePrev}
              handleNext={handleNext}
              handleJump={setMatchweek}
            />
            {!loadingWeek && pointsThisWeek > 0 && (
              <p className="text-sm text-gray-500 mt-1 mb-2">
                Superbru points this matchweek: <span className="font-medium text-gray-800">{pointsThisWeek}</span>
              </p>
            )}
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
