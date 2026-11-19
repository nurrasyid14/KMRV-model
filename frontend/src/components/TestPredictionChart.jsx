import React from 'react';
import { testPredictions } from '../data/realData';

const WIDTH = 1200;
const HEIGHT = 240;
const PAD = { left: 60, right: 40, top: 24, bottom: 58 };

export default function TestPredictionChart({ horizon = '1' }) {
  const rawData = testPredictions[horizon] || [];
  if (rawData.length === 0) {
    return <p className="chart-subtitle">Tidak ada prediksi uji untuk horizon ini.</p>;
  }

  const h = parseInt(horizon, 10) || 1;
  // Sesuaikan jumlah titik prediksi dengan horizon: 1m -> 1 titik, 3m -> 3 titik, 6m -> 6 titik
  const slicedData = rawData.slice(-h);

  const getTargetDate = (dateStr) => {
    const d = new Date(dateStr);
    d.setMonth(d.getMonth() + h);
    const m = String(d.getMonth() + 1).padStart(2, '0');
    const y = String(d.getFullYear()).slice(-2);
    return `${m}/${y}`;
  };

  // Titik jangkar observasi terakhir (Juni 2025: -0.02 °C) agar grafik kontinu
  const points = [
    {
      label: '06/25 (Dasar)',
      isAnchor: true,
      actual_oni: -0.02,
      lstm_oni: -0.02,
    },
    ...slicedData.map((p) => ({
      label: getTargetDate(p.date),
      isAnchor: false,
      actual_oni: p.actual_oni,
      lstm_oni: p.lstm_oni,
    })),
  ];

  const values = points.flatMap((p) => [p.actual_oni, p.lstm_oni]);
  const yMin = Math.min(...values, -0.6) - 0.2;
  const yMax = Math.max(...values, 0.5) + 0.2;
  const innerW = WIDTH - PAD.left - PAD.right;
  const innerH = HEIGHT - PAD.top - PAD.bottom;

  const getX = (index) => PAD.left + (index / Math.max(points.length - 1, 1)) * innerW;
  const getY = (value) => PAD.top + innerH - ((value - yMin) / (yMax - yMin)) * innerH;

  const actualPath = points.map((p, i) => `${getX(i)},${getY(p.actual_oni)}`).join(' L ');
  const predPath = points.map((p, i) => `${getX(i)},${getY(p.lstm_oni)}`).join(' L ');

  return (
    <svg
      viewBox={`0 0 ${WIDTH} ${HEIGHT}`}
      className="chart-svg"
      role="img"
      aria-label={`ONI aktual versus prediksi LSTM pada data uji, horizon ${horizon} bulan`}
    >
      {/* Garis batas ambang ENSO */}
      <line x1={PAD.left} y1={getY(0)} x2={WIDTH - PAD.right} y2={getY(0)} stroke="#e2e8f0" strokeWidth="1" />
      <line x1={PAD.left} y1={getY(0.5)} x2={WIDTH - PAD.right} y2={getY(0.5)} stroke="#fdba74" strokeWidth="1" strokeDasharray="3 3" />
      <line x1={PAD.left} y1={getY(-0.5)} x2={WIDTH - PAD.right} y2={getY(-0.5)} stroke="#7dd3fc" strokeWidth="1" strokeDasharray="3 3" />

      {/* Label sumbu Y */}
      <text x={PAD.left - 10} y={getY(0) + 4} textAnchor="end" fill="#94a3b8" fontSize="11" fontFamily="var(--font-outlier)">0</text>
      <text x={PAD.left - 10} y={getY(0.5) + 4} textAnchor="end" fill="#f97316" fontSize="11" fontFamily="var(--font-outlier)">+0,5</text>
      <text x={PAD.left - 10} y={getY(-0.5) + 4} textAnchor="end" fill="#0284c7" fontSize="11" fontFamily="var(--font-outlier)">-0,5</text>

      {/* Garis Aktual (solid hitam) */}
      <path d={`M ${actualPath}`} fill="none" stroke="#0f172a" strokeWidth="2.5" strokeLinejoin="round" />

      {/* Garis Prediksi LSTM (putus-putus biru) */}
      <path d={`M ${predPath}`} fill="none" stroke="#0284c7" strokeWidth="2.5" strokeDasharray="6 3" strokeLinejoin="round" />

      {/* Titik-titik dan label nilai */}
      {points.map((p, index) => {
        const x = getX(index);
        const yAct = getY(p.actual_oni);
        const yPred = getY(p.lstm_oni);

        return (
          <g key={`pt-${p.label}-${index}`}>
            {/* Titik aktual */}
            <circle cx={x} cy={yAct} r={p.isAnchor ? 4 : 4.5} fill="#0f172a" stroke="#ffffff" strokeWidth="1.5" />
            
            {/* Titik prediksi */}
            {!p.isAnchor && (
              <circle cx={x} cy={yPred} r="4.5" fill="#0284c7" stroke="#ffffff" strokeWidth="1.5" />
            )}

            {/* Nilai numerik di atas/bawah titik (hanya untuk titik prediksi jika tidak tumpang tindih) */}
            {!p.isAnchor && (
              <text
                x={x}
                y={yPred - 10}
                textAnchor="middle"
                fill="#0284c7"
                fontSize="11"
                fontWeight="700"
                fontFamily="var(--font-outlier)"
              >
                {p.lstm_oni.toFixed(2).replace('.', ',')}
              </text>
            )}

            {/* Label bulan di sumbu X */}
            <text
              x={x}
              y={HEIGHT - 32}
              textAnchor="middle"
              fill={p.isAnchor ? '#64748b' : '#0f172a'}
              fontSize="11.5"
              fontWeight={p.isAnchor ? '500' : '700'}
              fontFamily="var(--font-outlier)"
            >
              {p.label}
            </text>
          </g>
        );
      })}

      {/* Legenda bawah */}
      <g transform={`translate(${PAD.left}, ${HEIGHT - 8})`}>
        <line x1="0" y1="-4" x2="18" y2="-4" stroke="#0f172a" strokeWidth="2.5" />
        <circle cx="9" cy="-4" r="3" fill="#0f172a" />
        <text x="24" y="0" fill="#334155" fontSize="11" fontWeight="600">Aktual Observasi</text>

        <line x1="140" y1="-4" x2="160" y2="-4" stroke="#0284c7" strokeWidth="2.5" strokeDasharray="4 2" />
        <circle cx="150" cy="-4" r="3" fill="#0284c7" />
        <text x="166" y="0" fill="#0284c7" fontSize="11" fontWeight="600">Prediksi Causal LSTM</text>

        <text x="320" y="0" fill="#94a3b8" fontSize="11">
          (Target proyeksi: {h} bulan ke depan dari batas observasi)
        </text>
      </g>
    </svg>
  );
}
