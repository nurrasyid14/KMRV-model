import React from 'react';
import { history } from '../data/realData';

const WIDTH = 1000;
const HEIGHT = 260;
const PAD = { left: 48, right: 24, top: 20, bottom: 40 };

export default function SstAnomalyChart({ regionKey, label }) {
  const series = history.map((point) => point.sst[regionKey]);
  const min = Math.min(...series);
  const max = Math.max(...series);
  const bound = Math.max(Math.abs(min), Math.abs(max), 0.5) + 0.3;
  const yMin = -bound;
  const yMax = bound;
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;

  const getX = (index) => PAD.left + (index / (history.length - 1)) * innerW;
  const getY = (value) => PAD.top + innerH - ((value - yMin) / (yMax - yMin)) * innerH;

  const line = series.map((value, index) => `${getX(index)},${getY(value)}`).join(' L ');
  const lastValue = series[series.length - 1];
  const ticks = [yMin, 0, yMax].map((value) => Number(value.toFixed(1)));

  const yearTicks = history
    .map((point, index) => ({ point, index }))
    .filter(({ point }) => point.date.endsWith('-01'));

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="chart-svg"
      role="img"
      aria-label={`Anomali SST ${label} ${history[0].date} sampai ${history[history.length - 1].date}`}
    >
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
            {tick > 0 ? `+${tick.toString().replace('.', ',')}` : tick.toString().replace('.', ',')}
          </text>
        </g>
      ))}

      <path d={`M ${line}`} fill="none" stroke="#ea580c" strokeWidth="2" strokeLinejoin="round" strokeLinecap="round" />
      <circle cx={getX(history.length - 1)} cy={getY(lastValue)} r="4" fill="#ea580c" stroke="#ffffff" strokeWidth="1.5" />

      {yearTicks.map(({ point, index }) => (
        <text
          key={point.date}
          x={getX(index)}
          y={HEIGHT - 16}
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
