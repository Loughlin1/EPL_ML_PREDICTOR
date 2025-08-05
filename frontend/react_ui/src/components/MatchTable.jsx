import React from 'react';
import clsx from 'clsx';

const teamLogos = {
  'Arsenal' : 'arsenal.svg',
  'Aston Villa': 'aston_villa.webp',
  'Bournemouth': 'bournemouth.svg',
  'Chelsea': 'chelsea.svg',
  'Brentford': 'brentford.webp',
  'Brighton': 'brighton.svg',
  'Crystal Palace': 'crystal_palace.svg',
  'Everton': 'everton.svg',
  'Fulham': 'fulham.svg',
  'Ipswich Town': 'ipswich_town.svg',
  'Leeds United': 'leeds_united.svg',
  'Leicester City': 'leicester_city.webp',
  'Liverpool': 'liverpool.svg',
  'Manchester City': 'manchester_city.svg',
  'Manchester Utd': 'manchester_united.svg',
  'Newcastle Utd': 'newcastle_united.svg',
  "Nott'ham Forest": 'nottingham_forest.webp',
  'Southampton': 'southampton.svg',
  'Tottenham': "tottenham_hotspurs.svg",
  'West Ham': 'west_ham.svg',
  'Wolves': "wolves.svg",
};

const renderTeamCell = (teamName) => {
  const logo = '/assets/logos/' + teamLogos[teamName];
  return (
    <div className="flex items-center space-x-2 pr-5">
      {logo && (
        <img src={logo} alt={teamName} className="w-5 h-5 object-contain" />
      )}
      <span>{teamName}</span>
    </div>
  );
};

const MatchTable = ({ data }) => {
  const columns = [
    'Day', 'Date', 'Time', 'HomeTeam', 'AwayTeam', 'Score', 'Result',
    'PredScore', 'PredResult', 'Venue',
  ];

  const getRowClass = (row) => {
    if (row.Score && row.Score === row.PredScore) return 'bg-green-200';
    if (row.Score && row.Result === row.PredResult) return 'bg-yellow-200';
    return '';
  };

  return (
    <div className="w-full max-w-6xl overflow-x-auto bg-white shadow rounded-xl">
      <table className="min-w-full border-collapse text-xs md:text-sm">
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
                  {col === 'Date'
                    ? new Date(row[col]).toLocaleDateString()
                    : col === 'HomeTeam' || col === 'AwayTeam'
                      ? renderTeamCell(row[col])
                      : row[col]}
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