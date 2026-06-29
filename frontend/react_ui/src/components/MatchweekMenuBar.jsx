
const MatchweekMenuBar = ({matchweek, handlePrev, handleNext, handleJump}) => {
  return (
    <div className="mb-4 w-full flex items-center flex-wrap gap-4">
      <h2 className="text-xl font-semibold whitespace-nowrap">
        Matchweek {matchweek} Results
      </h2>
      <div className="flex items-center gap-2 text-sm md:text-base lg:text-lg">
        <button
          onClick={() => handlePrev(matchweek)}
          disabled={matchweek === 1}
          className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
        >
          ⏪ Last
        </button>
        <select
          value={matchweek}
          onChange={(e) => handleJump(Number(e.target.value))}
          className="px-3 py-2 border border-gray-300 rounded bg-white hover:border-gray-400 cursor-pointer"
        >
          {Array.from({length: 38}, (_, i) => i + 1).map((w) => (
            <option key={w} value={w}>Week {w}</option>
          ))}
        </select>
        <button
          onClick={() => handleNext(matchweek)}
          disabled={matchweek === 38}
          className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
        >
          Next ⏩
        </button>
      </div>
    </div>
  );
};
export default MatchweekMenuBar;