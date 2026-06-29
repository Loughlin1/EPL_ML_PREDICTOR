const Header = ({ season, availableSeasons, onSeasonChange }) => {
  return (
    <header className="flex items-center justify-between gap-4 pb-3 mb-3 border-b border-gray-200">
      <div className="flex items-center gap-3 min-w-0">
        <a href="#">
          <img src="/assets/icons/premier_league_icon.png" alt="Logo" className="object-cover size-10 rounded shrink-0" />
        </a>
        <h1 className="text-lg md:text-xl font-bold text-gray-900 whitespace-nowrap">⚽️ EPL Match Result Predictor</h1>
      </div>

      <div className="flex items-center gap-3 shrink-0">
        {availableSeasons.length > 0 && (
          <div className="flex items-center gap-2">
            <label className="text-sm font-medium text-gray-500 hidden sm:block">Season</label>
            <select
              value={season || ''}
              onChange={(e) => onSeasonChange(e.target.value)}
              className="px-2 py-1.5 border border-gray-300 rounded bg-white hover:border-gray-400 cursor-pointer text-sm"
            >
              {availableSeasons.map((s) => (
                <option key={s} value={s}>{s}</option>
              ))}
            </select>
          </div>
        )}
        <a
          href="https://github.com/Loughlin1/EPL_ML_PREDICTOR/tree/main"
          target="_blank"
          className="flex items-center gap-1.5 bg-gray-100 text-gray-600 text-sm px-3 py-1.5 rounded hover:bg-gray-200 transition-colors"
        >
          <img src="/assets/icons/github_icon.png" alt="GitHub" className="object-cover size-4" />
          <span className="hidden sm:inline">GitHub</span>
        </a>
      </div>
    </header>
  );
};

export default Header;