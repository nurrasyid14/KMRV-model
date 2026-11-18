import React from 'react';
import { history, meta } from '../data/realData';

const WIDTH = 1000;
const HEIGHT = 220;
const PAD = { left: 48, right: 24, top: 16, bottom: 36 };

export default function OniHistoryChart() {
  const yMin = -2;
  const yMax = 3.5;
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;

  const getX = (index) => PAD.left + (index / (history.length - 1)) * innerW;
  const getY = (value) => {
    const clamped = Math.max(yMin, Math.min(yMax, value));
    return PAD.top + innerH - ((clamped - yMin) / (yMax - yMin)) * innerH;
  };

  const line = history.map((point, index) => `${getX(index)},${getY(point.oni)}`).join(' L ');
  const last = history[history.length - 1];
  const testStart = history.findIndex((point) => point.split === 'test');
  const ticks = [-2, -1, 0, 1, 2, 3];

  const episodes = [];
  let runStart = null;
  let runSign = 0;
  history.forEach((point, index) => {
    const sign = point.oni >= 0.5 ? 1 : point.oni <= -0.5 ? -1 : 0;
    if (sign !== runSign) {
      if (runSign !== 0 && runStart !== null && index - runStart >= 6) {
        episodes.push({ start: runStart, end: index - 1, sign: runSign });
      }
      runStart = sign === 0 ? null : index;
      runSign = sign;
    }
  });
  if (runSign !== 0 && runStart !== null && history.length - runStart >= 6) {
    episodes.push({ start: runStart, end: history.length - 1, sign: runSign });
  }

  const majorEpisodes = [...episodes]
    .sort((a, b) => (b.end - b.start) - (a.end - a.start))
    .slice(0, 3)
    .sort((a, b) => a.start - b.start);

  const yearTicks = history
    .map((point, index) => ({ point, index }))
    .filter(({ point }) => point.date.endsWith('-01'));

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="chart-svg"
      role="img"
      aria-label={`ONI bulanan ${meta.datasetStart} sampai ${meta.datasetEnd}`}
    >
      <rect
        x={getX(testStart)}
        y={PAD.top}
        width={WIDTH - PAD.right - getX(testStart)}
        height={innerH}
        fill="#f1f5f9"
        opacity="0.7"
      />
      <text x={getX(testStart) + 8} y={PAD.top + innerH - 8} fill="#94a3b8" fontSize="11" fontFamily="var(--font-outlier)">
        Data uji
      </text>

      <rect
        x={PAD.left}
        y={PAD.top}
        width={innerW}
        height={Math.max(0, getY(0.5) - PAD.top)}
        fill="#fff7ed"
        opacity="0.55"
      />
      <rect
        x={PAD.left}
        y={getY(-0.5)}
        width={innerW}
        height={Math.max(0, PAD.top + innerH - getY(-0.5))}
        fill="#f0f9ff"
        opacity="0.55"
      />

      {majorEpisodes.map((episode) => {
        const middle = (episode.start + episode.end) / 2;
        const startYear = history[episode.start].date.slice(0, 4);
        const endYear = history[episode.end].date.slice(0, 4);
        const years = startYear === endYear ? startYear : `${startYear}–${endYear}`;
        const x = Math.min(Math.max(getX(middle), PAD.left + 70), WIDTH - PAD.right - 70);
        return (
          <text
            key={`${episode.start}-${episode.sign}`}
            x={x}
            y={PAD.top + 12}
            textAnchor="middle"
            fill={episode.sign > 0 ? '#c2410c' : '#0369a1'}
            fontSize="10"
            fontWeight="600"
            fontFamily="var(--font-outlier)"
          >
            {episode.sign > 0 ? 'El Niño' : 'La Niña'} {years}
          </text>
        );
      })}

      {ticks.map((tick) => (
        <g key={tick}>
          <line
            x1={PAD.left}
            y1={getY(tick)}
            x2={WIDTH - PAD.right}
            y2={getY(tick)}
            stroke={tick === 0 ? '#cbd5e1' : '#f1f5f9'}
            strokeWidth="1"
          />
          <text
            x={PAD.left - 8}
            y={getY(tick) + 4}
            textAnchor="end"
            fill="#94a3b8"
            fontSize="11"
            fontFamily="var(--font-outlier)"
          >
            {tick > 0 ? `+${tick}` : tick}
          </text>
        </g>
      ))}

      <line x1={PAD.left} y1={getY(0.5)} x2={WIDTH - PAD.right} y2={getY(0.5)} stroke="#fdba74" strokeWidth="1.2" strokeDasharray="4 4" />
      <line x1={PAD.left} y1={getY(-0.5)} x2={WIDTH - PAD.right} y2={getY(-0.5)} stroke="#7dd3fc" strokeWidth="1.2" strokeDasharray="4 4" />
      <text x={WIDTH - PAD.right} y={getY(0.5) - 6} textAnchor="end" fill="#ea580c" fontSize="10" fontFamily="var(--font-outlier)">+0,5 El Niño</text>
      <text x={WIDTH - PAD.right} y={getY(-0.5) + 14} textAnchor="end" fill="#0284c7" fontSize="10" fontFamily="var(--font-outlier)">−0,5 La Niña</text>

      <path d={`M ${line}`} fill="none" stroke="#0f172a" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={getX(history.length - 1)} cy={getY(last.oni)} r="4" fill="#2563eb" stroke="#ffffff" strokeWidth="1.5" />

      {yearTicks.map(({ point, index }) => (
        <text
          key={point.date}
          x={getX(index)}
          y={HEIGHT - 18}
          textAnchor="middle"
          fill="#94a3b8"
          fontSize="11"
          fontFamily="var(--font-outlier)"
        >
          {point.date.slice(0, 4)}
        </text>
      ))}
    </svg>
  );
}
