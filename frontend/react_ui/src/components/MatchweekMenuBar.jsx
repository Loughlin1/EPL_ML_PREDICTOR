
const MatchweekMenuBar = ({matchweek, handlePrev, handleNext}) => {
  return (
    <div className="mb-4 w-full flex items-center flex-wrap gap-4">
      <h2 className="text-xl font-semibold whitespace-nowrap">
        Matchweek {matchweek} Results
      </h2>
      <div className="flex gap-2 text-sm md:text-base lg:text-lg">
        <button
          onClick={() => handlePrev(matchweek)}
          disabled={matchweek === 1}
          className="px-4 py-2 bg-gray-200 rounded hover:bg-gray-300 disabled:opacity-50"
        >
          ⏪ Last
        </button>
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