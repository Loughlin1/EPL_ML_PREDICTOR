import { useEffect, useState } from 'react';
import {
  Chart as ChartJS,
  CategoryScale, LinearScale, PointElement, LineElement,
  Tooltip, Legend, Filler,
} from 'chart.js';
import { Line } from 'react-chartjs-2';
import { getSeasonSummary, getTopPoints } from '../api';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, Tooltip, Legend, Filler);

const METRICS = [
  { key: 'Correct_Result_%',   label: 'Correct results %',  unit: '%',  decimals: 1 },
  { key: 'Correct_Scores_%',   label: 'Correct scores %',   unit: '%',  decimals: 1 },
  { key: 'superbru_points',    label: 'Superbru points',    unit: ' pts', decimals: 0 },
  { key: 'MAE_Total',          label: 'Goal MAE',           unit: '',   decimals: 2, lowerIsBetter: true },
];

function shortSeason(s) {
  const [a, b] = s.split('-');
  return `${a.slice(2)}-${b.slice(2)}`;
}

export default function SeasonHistoryModal({ availableSeasons, onClose }) {
  const [activeMetric, setActiveMetric] = useState(METRICS[0]);
  const [summaries, setSummaries] = useState({});
  const [leaderboards, setLeaderboards] = useState({});
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchAll = async () => {
      setLoading(true);
      const results = await Promise.allSettled(
        availableSeasons.map(async (s) => {
          const [sumRes, lbRes] = await Promise.all([
            getSeasonSummary(s),
            getTopPoints(s),
          ]);
          return { season: s, summary: sumRes.data, leaderboard: lbRes.data };
        })
      );
      const sums = {};
      const lbs = {};
      results.forEach((r) => {
        if (r.status === 'fulfilled') {
          sums[r.value.season] = r.value.summary;
          lbs[r.value.season] = r.value.leaderboard;
        }
      });
      setSummaries(sums);
      setLeaderboards(lbs);
      setLoading(false);
    };
    fetchAll();
  }, [availableSeasons]);

  const labels = availableSeasons.map(shortSeason);

  const getValue = (season, metric) => {
    const sum = summaries[season];
    if (!sum) return null;
    if (metric.key === 'superbru_points') return sum.superbru_points ?? null;
    return sum.model_performance?.[metric.key] ?? null;
  };

  const modelData = availableSeasons.map((s) => getValue(s, activeMetric));
  const globalTop10 = availableSeasons.map((s) => leaderboards[s]?.global_top_10_pct ?? null);
  const ukTop10 = availableSeasons.map((s) => leaderboards[s]?.uk_top_10_pct ?? null);

  const showBenchmarks = activeMetric.key === 'superbru_points';

  const chartData = {
    labels,
    datasets: [
      {
        label: 'This model',
        data: modelData,
        borderColor: '#534AB7',
        backgroundColor: 'rgba(83,74,183,0.08)',
        borderWidth: 2,
        pointRadius: 4,
        pointHoverRadius: 6,
        tension: 0.3,
        fill: true,
      },
      ...(showBenchmarks ? [
        {
          label: 'Global top 10%',
          data: globalTop10,
          borderColor: '#888780',
          borderWidth: 1.5,
          borderDash: [5, 4],
          pointRadius: 0,
          tension: 0,
          fill: false,
        },
        {
          label: 'UK top 10%',
          data: ukTop10,
          borderColor: '#B4B2A9',
          borderWidth: 1.5,
          borderDash: [3, 3],
          pointRadius: 0,
          tension: 0,
          fill: false,
        },
      ] : []),
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    interaction: { mode: 'index', intersect: false },
    plugins: {
      legend: { display: showBenchmarks, position: 'bottom', labels: { boxWidth: 12, font: { size: 11 } } },
      tooltip: {
        callbacks: {
          label: (ctx) => {
            const v = ctx.parsed.y;
            if (v == null) return null;
            return ` ${ctx.dataset.label}: ${v.toFixed(activeMetric.decimals)}${activeMetric.unit}`;
          },
        },
      },
    },
    scales: {
      x: {
        grid: { color: 'rgba(0,0,0,0.05)' },
        ticks: { font: { size: 11 }, color: '#888' },
      },
      y: {
        grid: { color: 'rgba(0,0,0,0.05)' },
        ticks: {
          font: { size: 11 },
          color: '#888',
          callback: (v) => `${v.toFixed(activeMetric.decimals)}${activeMetric.unit}`,
        },
      },
    },
  };

  return (
    <div
      className="fixed inset-0 z-50 flex items-end sm:items-center justify-center bg-black/40"
      onClick={(e) => e.target === e.currentTarget && onClose()}
    >
      <div className="bg-white rounded-t-2xl sm:rounded-2xl w-full sm:max-w-3xl max-h-[90vh] overflow-y-auto shadow-xl p-6">
        <div className="flex items-center justify-between mb-5">
          <h2 className="text-base font-medium text-gray-900">Performance across all seasons</h2>
          <button
            onClick={onClose}
            className="text-gray-400 hover:text-gray-600 text-xl leading-none"
            aria-label="Close"
          >
            ×
          </button>
        </div>

        <div className="flex flex-wrap gap-2 mb-5">
          {METRICS.map((m) => (
            <button
              key={m.key}
              onClick={() => setActiveMetric(m)}
              className={`text-xs px-3 py-1.5 rounded-md border transition-colors ${
                activeMetric.key === m.key
                  ? 'bg-gray-100 border-gray-300 text-gray-900 font-medium'
                  : 'border-gray-200 text-gray-500 hover:border-gray-300'
              }`}
            >
              {m.label}
            </button>
          ))}
        </div>

        {loading ? (
          <div className="flex items-center justify-center h-64 gap-3 text-gray-400">
            <div className="w-6 h-6 border-2 border-gray-200 border-t-purple-600 rounded-full animate-spin" />
            <span className="text-sm">Loading season data…</span>
          </div>
        ) : (
          <>
            <div style={{ height: 280 }}>
              <Line data={chartData} options={chartOptions} />
            </div>
            {activeMetric.lowerIsBetter && (
              <p className="text-xs text-gray-400 mt-2">Lower is better for this metric.</p>
            )}
            {showBenchmarks && (
              <p className="text-xs text-gray-400 mt-2">
                Leaderboard benchmarks are estimates while Superbru login is disabled.
              </p>
            )}
          </>
        )}
      </div>
    </div>
  );
}
