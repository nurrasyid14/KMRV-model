import React from 'react';
import { roniTimeSeries } from '../data/climateData';

/**
 * Deret waktu RONI dengan pita ketidakpastian 80%.
 * Compact menampilkan 14 bulan terakhir agar prakiraan tetap terbaca di ponsel.
 */
export default function RoniTraceChart({ compact = false }) {
  const data = compact ? roniTimeSeries.slice(16) : roniTimeSeries;
  const chartWidth = compact ? 380 : 880;
  const chartHeight = 300;
  const padLeft = compact ? 44 : 56;
  const padRight = compact ? 96 : 108;
  const padTop = 30;
  const padBottom = 40;
  const labelSize = compact ? 14 : 12;

  const innerW = chartWidth - padLeft - padRight;
  const innerH = chartHeight - padTop - padBottom;

  const yMin = -1.0;
  const yMax = 1.8;

  const getY = (val) => {
    const clamped = Math.max(yMin, Math.min(yMax, val));
    return padTop + innerH - ((clamped - yMin) / (yMax - yMin)) * innerH;
  };

  const getX = (idx) => padLeft + (idx / (data.length - 1)) * innerW;

  const firstForecast = data.findIndex((d) => d.isForecast);
  const forecastStartIndex = Math.max(0, firstForecast - 1);
  const lastPoint = data[data.length - 1];

  const historicalPoints = data
    .filter((d) => !d.isForecast)
    .map((d, i) => `${getX(i)},${getY(d.value)}`)
    .join(' L ');

  const forecastPoints = data
    .slice(forecastStartIndex)
    .map((d, i) => `${getX(forecastStartIndex + i)},${getY(d.value)}`)
    .join(' L ');

  const upperPoints = data
    .slice(forecastStartIndex)
    .map((d, i) => `${getX(forecastStartIndex + i)},${getY(d.upper || d.value)}`);

  const lowerPointsRev = data
    .slice(forecastStartIndex)
    .map((d, i) => `${getX(forecastStartIndex + i)},${getY(d.lower || d.value)}`)
    .reverse();

  const uncertaintyPolygon = `M ${upperPoints.join(' L ')} L ${lowerPointsRev.join(' L ')} Z`;

  const yElNinoLine = getY(0.5);
  const yLaNinaLine = getY(-0.5);
  const yZeroLine = getY(0.0);

  // Jangan biarkan label terakhir menabrak label sebelumnya di sumbu X.
  const xTickIndexes = [];
  for (let i = 0; i < data.length; i += 4) xTickIndexes.push(i);
  const lastIndex = data.length - 1;
  if (lastIndex - xTickIndexes[xTickIndexes.length - 1] < 3) {
    xTickIndexes[xTickIndexes.length - 1] = lastIndex;
  } else {
    xTickIndexes.push(lastIndex);
  }
  const xTicks = xTickIndexes.map((index) => ({ point: data[index], index }));

  const uid = compact ? 'roni-compact' : 'roni-wide';
  const thresholdLabels = compact
    ? ['El Niño +0,5', 'Normal 0,0', 'La Niña -0,5']
    : ['+0,5 °C El Niño', '0,0 °C Normal', '-0,5 °C La Niña'];

  return (
    <svg
      width="100%"
      height={chartHeight}
      viewBox={`0 0 ${chartWidth} ${chartHeight}`}
      className={`roni-svg-chart ${compact ? 'roni-svg-chart--compact' : 'roni-svg-chart--wide'}`}
      role="img"
      aria-labelledby={`${uid}-title ${uid}-desc`}
    >
      <title id={`${uid}-title`}>Indeks RONI: observasi dan prakiraan KMRV</title>
      <desc id={`${uid}-desc`}>
        {compact
          ? 'Deret observasi Maret 2026 sampai Oktober 2026, lalu proyeksi KMRV sampai April 2027.'
          : 'Deret observasi November 2024 sampai Oktober 2026, lalu proyeksi KMRV sampai April 2027.'}
        {' '}Pita arsir menunjukkan interval keyakinan 80 persen; nilai akhir proyeksi plus 1,20 derajat Celsius.
      </desc>

      {/* Zona Shading Lembut El Niño (> +0,5 °C) */}
      <rect
        x={padLeft}
        y={padTop}
        width={innerW}
        height={Math.max(0, yElNinoLine - padTop)}
        fill="var(--color-elnino-soft)"
        opacity="0.18"
      />
      {/* Zona Shading Lembut La Niña (< -0,5 °C) */}
      <rect
        x={padLeft}
        y={yLaNinaLine}
        width={innerW}
        height={Math.max(0, padTop + innerH - yLaNinaLine)}
        fill="var(--color-lanina-soft)"
        opacity="0.18"
      />

      {/* Garis Horizontal Ambang Batas */}
      <line
        x1={padLeft}
        y1={yElNinoLine}
        x2={padLeft + innerW}
        y2={yElNinoLine}
        stroke="var(--color-elnino)"
        strokeWidth="1.2"
        strokeDasharray="4 4"
      />
      <text
        x={padLeft + innerW + 8}
        y={yElNinoLine + 4}
        fill="var(--color-elnino)"
        fontSize={labelSize}
        fontFamily="var(--font-outlier)"
        fontWeight="600"
      >
        {thresholdLabels[0]}
      </text>

      <line
        x1={padLeft}
        y1={yZeroLine}
        x2={padLeft + innerW}
        y2={yZeroLine}
        stroke="var(--color-rule-2)"
        strokeWidth="1"
      />
      <text
        x={padLeft + innerW + 8}
        y={yZeroLine + 4}
        fill="var(--color-muted)"
        fontSize={labelSize}
        fontFamily="var(--font-outlier)"
      >
        {thresholdLabels[1]}
      </text>

      <line
        x1={padLeft}
        y1={yLaNinaLine}
        x2={padLeft + innerW}
        y2={yLaNinaLine}
        stroke="var(--color-lanina)"
        strokeWidth="1.2"
        strokeDasharray="4 4"
      />
      <text
        x={padLeft + innerW + 8}
        y={yLaNinaLine + 4}
        fill="var(--color-lanina)"
        fontSize={labelSize}
        fontFamily="var(--font-outlier)"
        fontWeight="600"
      >
        {thresholdLabels[2]}
      </text>

      {/* Garis Pembatas Vertikal: Observasi Historis vs Forecast */}
      <line
        x1={getX(forecastStartIndex)}
        y1={padTop}
        x2={getX(forecastStartIndex)}
        y2={padTop + innerH}
        stroke="var(--color-rule-2)"
        strokeWidth="1.2"
        strokeDasharray="3 3"
      />
      <text
        x={getX(forecastStartIndex) - 6}
        y={padTop + 14}
        textAnchor="end"
        fill="var(--color-muted)"
        fontSize={labelSize}
        fontFamily="var(--font-body)"
      >
        Observasi
      </text>
      <text
        x={getX(forecastStartIndex) + 6}
        y={padTop + 14}
        fill="var(--color-brand)"
        fontSize={labelSize}
        fontFamily="var(--font-body)"
        fontWeight="600"
      >
        Prakiraan KMRV
      </text>

      {/* Pita Ketidakpastian (Uncertainty Band) */}
      <path d={uncertaintyPolygon} fill="var(--color-band-fill)" opacity="0.9" />

      {/* Garis Historis */}
      <path
        d={`M ${historicalPoints}`}
        fill="none"
        stroke="var(--color-ink)"
        strokeWidth="2.2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Garis Proyeksi KMRV */}
      <path
        d={`M ${forecastPoints}`}
        fill="none"
        stroke="var(--color-brand)"
        strokeWidth="2.5"
        strokeDasharray="5 3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      {/* Titik Observasi Terakhir */}
      <circle
        cx={getX(forecastStartIndex)}
        cy={getY(data[forecastStartIndex].value)}
        r="4.5"
        fill="var(--color-ink)"
      />

      {/* Titik Akhir Proyeksi Lead 6 Bulan */}
      <circle cx={getX(lastIndex)} cy={getY(lastPoint.value)} r="4.5" fill="var(--color-brand)" />
      <text
        x={getX(lastIndex)}
        y={getY(lastPoint.value) - 8}
        textAnchor="middle"
        fill="var(--color-brand)"
        fontSize={labelSize}
        fontFamily="var(--font-outlier)"
        fontWeight="600"
      >
        +1,20 °C
      </text>

      {/* Label Sumbu X */}
      {xTicks.map(({ point, index }) => (
        <text
          key={point.date}
          x={getX(index)}
          y={padTop + innerH + 18}
          textAnchor="middle"
          fill="var(--color-muted)"
          fontSize={labelSize}
          fontFamily="var(--font-outlier)"
        >
          {point.date}
        </text>
      ))}
    </svg>
  );
}
