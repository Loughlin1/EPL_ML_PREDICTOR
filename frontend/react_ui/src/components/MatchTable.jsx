import React from 'react';
import clsx from 'clsx';

const MatchTable = ({ data }) => {
  const columns = [
    'Day', 'Date', 'Time', 'HomeTeam', 'Score', 'Result',
    'PredScore', 'PredResult', 'AwayTeam', 'Venue',
  ];

  const getRowClass = (row) => {
    if (row.Score && row.Score === row.PredScore) return 'bg-green-200';
    if (row.Score && row.Result === row.PredResult) return 'bg-yellow-200';
    return '';
  };

  return (
    <div className="w-full max-w-6xl overflow-x-auto bg-white shadow rounded-xl">
      <table className="min-w-full border-collapse text-sm">
        <thead className="bg-gray-100 text-left">
          <tr>
            {columns.map((col) => (
              <th key={col} className="p-2 border">{col}</th>
            ))}
          </tr>
        </thead>
        <tbody>
          {data.map((row, idx) => (
            <tr key={idx} className={clsx(getRowClass(row))}>
              {columns.map((col) => (
                <td key={col} className="p-2 border">
                  {col === 'Date' ? new Date(row[col]).toLocaleDateString() : row[col]}
                </td>
              ))}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
};

export default MatchTable;