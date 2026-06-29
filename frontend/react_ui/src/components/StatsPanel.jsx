import { useState } from 'react';
import SeasonHistoryModal from './SeasonHistoryModal';

const fmt = (v, decimals = 1) =>
  v == null || v === '' ? '—' : Number(v).toFixed(decimals);

function SectionLabel({ children }) {
  return (
    <p className="text-xs text-gray-400 uppercase tracking-wide font-medium mb-2">
      {children}
    </p>
  );
}

function MetricCard({ label, value, sub }) {
  return (
    <div className="bg-gray-50 rounded-lg p-3">
      <p className="text-xs text-gray-500 mb-1">{label}</p>
      <p className="text-xl font-medium text-gray-900 leading-tight">{value}</p>
      {sub && <p className="text-xs text-gray-400 mt-0.5">{sub}</p>}
    </div>
  );
}

function BenchmarkBar({ label, value, max, color, isModel }) {
  const pct = max > 0 ? Math.min((value / max) * 100, 100) : 0;
  return (
    <div className="flex items-center gap-3 mb-2">
      <span className={`text-xs w-32 shrink-0 ${isModel ? 'font-medium text-gray-800' : 'text-gray-500'}`}>
        {isModel && <span className="inline-block w-2 h-2 rounded-full bg-purple-600 mr-1.5 align-middle" />}
        {label}
      </span>
      <div className="flex-1 bg-gray-100 rounded-full h-1.5 overflow-hidden">
        <div
          className="h-1.5 rounded-full transition-all duration-500"
          style={{ width: `${pct}%`, backgroundColor: color }}
        />
      </div>
      <span className={`text-xs w-8 text-right tabular-nums ${isModel ? 'font-medium text-purple-700' : 'text-gray-500'}`}>
        {value ?? '—'}
      </span>
    </div>
  );
}

export default function StatsPanel({
  seasonSummary,
  globalTopPoints,
  globalTop10PctPoints,
  ukTop10PctPoints,
  availableSeasons,
}) {
  const [showHistory, setShowHistory] = useState(false);

  const perf = seasonSummary?.model_performance ?? {};
  const totalPoints = seasonSummary?.superbru_points ?? 0;
  const played = seasonSummary?.matches_played ?? 0;
  const total = seasonSummary?.matches_total ?? 380;

  const correctResultPct = fmt(perf['Correct_Result_%']);
  const correctScorePct = fmt(perf['Correct_Scores_%']);
  const correctResultN = perf['Correct_Results'] ?? '—';
  const correctScoreN = perf['Correct_Scores'] ?? '—';
  const mae = fmt(perf['MAE_Total'], 2);

  const benchMax = globalTopPoints || 1;

  const modelName = seasonSummary?.model_name;

  return (
    <div className="w-full mb-4 space-y-4">

      <div>
        <div className="flex items-center gap-3 mb-2">
          <p className="text-xs text-gray-400 uppercase tracking-wide font-medium">Season performance</p>
          {modelName && (
            <span className="text-xs text-purple-700 bg-purple-50 border border-purple-200 rounded-full px-2 py-0.5 font-medium -mt-2">
              {modelName}
            </span>
          )}
        </div>
        <div className="grid grid-cols-2 sm:grid-cols-4 gap-2">
          <MetricCard
            label="Correct results"
            value={`${correctResultPct}%`}
            sub={`${correctResultN} / ${played} matches`}
          />
          <MetricCard
            label="Correct scores"
            value={`${correctScorePct}%`}
            sub={`${correctScoreN} / ${played} matches`}
          />
          <MetricCard
            label="Goal MAE"
            value={mae}
            sub="avg goals off per match"
          />
          <MetricCard
            label="Superbru points"
            value={fmt(totalPoints, 1)}
            sub={`${played} of ${total} matches played`}
          />
        </div>
      </div>

      <div className="bg-gray-50 rounded-lg p-4">
        <SectionLabel>Superbru leaderboard — how we compare (season)</SectionLabel>
        <div className="max-w-lg">
          <BenchmarkBar label="Global top" value={globalTopPoints} max={benchMax} color="#888780" />
          <BenchmarkBar label="UK top 10%" value={ukTop10PctPoints} max={benchMax} color="#B4B2A9" />
          <BenchmarkBar label="Global top 10%" value={globalTop10PctPoints} max={benchMax} color="#D3D1C7" />
          <BenchmarkBar
            label="This model"
            value={Math.round(totalPoints)}
            max={benchMax}
            color="#534AB7"
            isModel
          />
        </div>

        <button
          onClick={() => setShowHistory(true)}
          className="mt-4 inline-flex items-center gap-1.5 text-xs text-purple-700 border border-purple-200 bg-white rounded-md px-3 py-1.5 hover:bg-purple-50 transition-colors"
        >
          <svg width="13" height="13" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
            <polyline points="22 12 18 12 15 21 9 3 6 12 2 12"/>
          </svg>
          View performance across all seasons
        </button>
      </div>

      {showHistory && (
        <SeasonHistoryModal
          availableSeasons={availableSeasons}
          onClose={() => setShowHistory(false)}
        />
      )}
    </div>
  );
}
