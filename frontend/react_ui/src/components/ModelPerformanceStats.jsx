function replaceUnderscores(str) {
  return str.replace(/_/g, " ");
}

const ModelPerformanceStats = ({ data }) => {
    return (
        <div className="text-xs sm:text-sm md:text-base lg:text-lg">
            <ul>
                {Object.keys(data).map((key) => (
                <li key={key}>{replaceUnderscores(key)}: {data[key]}</li>
                ))}
            </ul>
        </div>
    );
};


export default ModelPerformanceStats;