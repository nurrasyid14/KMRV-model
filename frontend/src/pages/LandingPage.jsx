import React from 'react';
import {
  currentClimateState,
  climateDatasetMeta,
  roniTimeSeries,
  regionalOceanData,
  regionalRainfallMatrix,
  dataProvenanceRecords
} from '../data/climateData';

const LEAD_KEY = '3 bulan';
const lead = currentClimateState.leadTimes[LEAD_KEY];

// Sparkline ringkas: bentuk data nyata dari tab yang dibuka, tanpa teks mikro.
function Vignette({ tab }) {
  if (tab === 'laut') {
    return (
      <svg width="160" height="34" viewBox="0 0 160 34" aria-hidden="true">
        {regionalOceanData.map((region, i) => (
          <rect
            key={region.id}
            x={i * 32}
            y="13"
            width={Math.max(4, (Math.abs(region.num) / 0.9) * 26)}
            height="8"
            rx="1"
            fill={region.num >= 0 ? 'var(--color-elnino)' : 'var(--color-lanina)'}
            opacity={1 - i * 0.14}
          />
        ))}
      </svg>
    );
  }

  if (tab === 'dampak') {
    const maxDeficit = Math.max(...regionalRainfallMatrix.map((row) => Math.abs(row.jja)));
    return (
      <svg width="160" height="34" viewBox="0 0 160 34" aria-hidden="true">
        {regionalRainfallMatrix.map((row, i) => {
          const barHeight = Math.max(4, (Math.abs(row.jja) / maxDeficit) * 22);
          return (
            <rect
              key={row.region}
              x={i * 32}
              y={30 - barHeight}
              width="24"
              height={barHeight}
              rx="1"
              fill="var(--color-elnino)"
              opacity={1 - i * 0.14}
            />
          );
        })}
      </svg>
    );
  }

  if (tab === 'prakiraan') {
    return (
      <svg width="160" height="34" viewBox="0 0 160" aria-hidden="true">
        <rect x="0" y="6" width={lead.kmrvMae * 100} height="5" rx="1" fill="var(--color-accent)" />
        <rect x="0" y="15" width={lead.persMae * 100} height="5" rx="1" fill="var(--color-rule-2)" />
        <rect x="0" y="24" width={lead.klimMae * 100} height="5" rx="1" fill="var(--color-rule-2)" />
      </svg>
    );
  }

  return (
    <svg width="160" height="34" viewBox="0 0 160 34" aria-hidden="true">
      {dataProvenanceRecords.slice(0, 3).map((source, i) => (
        <g key={source.source}>
          <rect
            x="0"
            y={6 + i * 9}
            width="4"
            height="4"
            rx="0.5"
            fill={i === 0 ? 'var(--color-accent)' : i === 1 ? 'var(--color-lanina)' : 'var(--color-neutral)'}
          />
          <line x1="10" y1={8 + i * 9} x2={150 - i * 18} y2={8 + i * 9} stroke="var(--color-rule-2)" strokeWidth="1" />
        </g>
      ))}
    </svg>
  );
}

function TraceChart({ compact = false }) {
  // Di layar sempit, tampilkan 14 bulan terakhir agar prakiraan tetap terlihat tanpa geser horizontal.
  const data = compact ? roniTimeSeries.slice(16) : roniTimeSeries;
  const width = compact ? 380 : 640;
  const height = compact ? 260 : 300;
  const padLeft = compact ? 46 : 52;
  const padRight = compact ? 64 : 108;
  const padTop = compact ? 26 : 28;
  const padBottom = compact ? 36 : 38;
  const innerW = width - padLeft - padRight;
  const innerH = height - padTop - padBottom;
  const labelSize = compact ? 15 : 12;
  const yMin = -1;
  const yMax = 1.8;
  const uid = compact ? 'trace-compact' : 'trace';

  const getX = (index) => padLeft + (index / (data.length - 1)) * innerW;
  const getY = (value) => {
    const clamped = Math.max(yMin, Math.min(yMax, value));
    return padTop + innerH - ((clamped - yMin) / (yMax - yMin)) * innerH;
  };

  const firstForecast = data.findIndex((point) => point.isForecast);
  const forecastStart = Math.max(0, firstForecast - 1);
  const targetIndex = data.findIndex((point) => point.date === 'Feb 27');
  const targetPoint = data[targetIndex];
  const lastPoint = data[data.length - 1];

  const historicalPath = data
    .map((point, index) => ({ point, index }))
    .filter(({ point }) => !point.isForecast)
    .map(({ point, index }) => `${getX(index)},${getY(point.value)}`)
    .join(' L ');

  const forecastPath = data
    .slice(forecastStart)
    .map((point, index) => `${getX(forecastStart + index)},${getY(point.value)}`)
    .join(' L ');

  const bandPoints = data.slice(forecastStart).map((point, index) => ({
    x: getX(forecastStart + index),
    upper: getY(point.upper ?? point.value),
    lower: getY(point.lower ?? point.value)
  }));
  const bandPath = `M ${bandPoints.map((point) => `${point.x},${point.upper}`).join(' L ')} L ${bandPoints
    .slice()
    .reverse()
    .map((point) => `${point.x},${point.lower}`)
    .join(' L ')} Z`;

  const yTicks = [
    { value: -0.5, label: '-0,5', color: 'var(--color-lanina-border)' },
    { value: 0, label: '0,0', color: 'var(--color-rule-2)' },
    { value: 0.5, label: '+0,5', color: 'var(--color-elnino-border)' },
    { value: 1.5, label: '+1,5', color: 'var(--color-rule)' }
  ];

  const tickIndexes = [];
  for (let i = 0; i < data.length; i += 4) tickIndexes.push(i);
  const lastIndex = data.length - 1;
  if (lastIndex - tickIndexes[tickIndexes.length - 1] < 3) {
    tickIndexes[tickIndexes.length - 1] = lastIndex;
  } else {
    tickIndexes.push(lastIndex);
  }
  const xTicks = tickIndexes.map((index) => ({ point: data[index], index }));

  return (
    <svg
      viewBox={`0 0 ${width} ${height}`}
      className={`trace-svg ${compact ? 'trace-svg--compact' : 'trace-svg--wide'}`}
      role="img"
      aria-labelledby={`${uid}-title ${uid}-desc`}
    >
      <title id={`${uid}-title`}>Lintasan indeks RONI observasi dan prakiraan KMRV</title>
      <desc id={`${uid}-desc`}>
        {compact
          ? 'Garis observasi dari Maret 2026 sampai Oktober 2026, lalu proyeksi KMRV sampai April 2027'
          : 'Garis observasi dari November 2024 sampai Oktober 2026, lalu proyeksi KMRV sampai April 2027'}
        {' '}dengan pita ketidakpastian 80 persen. Nilai pada Februari 2027 adalah plus 0,94 derajat Celsius.
      </desc>

      <rect
        x={padLeft}
        y={padTop}
        width={innerW}
        height={Math.max(0, getY(0.5) - padTop)}
        fill="var(--color-elnino-soft)"
        opacity="0.28"
      />
      <rect
        x={padLeft}
        y={getY(-0.5)}
        width={innerW}
        height={Math.max(0, padTop + innerH - getY(-0.5))}
        fill="var(--color-lanina-soft)"
        opacity="0.28"
      />

      {yTicks.map((tick) => (
        <g key={tick.value}>
          <line
            x1={padLeft}
            y1={getY(tick.value)}
            x2={padLeft + innerW}
            y2={getY(tick.value)}
            stroke={tick.color}
            strokeWidth="1"
            strokeDasharray={tick.value === 0 ? undefined : '4 4'}
          />
          <text
            x={padLeft - 9}
            y={getY(tick.value) + 4}
            textAnchor="end"
            fill="var(--color-muted)"
            fontSize={labelSize}
            fontFamily="var(--font-outlier)"
          >
            {tick.label}
          </text>
        </g>
      ))}

      <text x={padLeft + innerW + 8} y={getY(0.5) + 4} fill="var(--color-elnino)" fontSize={labelSize} fontFamily="var(--font-outlier)">
        El Niño
      </text>
      <text x={padLeft + innerW + 8} y={getY(0) + 4} fill="var(--color-muted)" fontSize={labelSize} fontFamily="var(--font-outlier)">
        Netral
      </text>
      <text x={padLeft + innerW + 8} y={getY(-0.5) + 4} fill="var(--color-lanina)" fontSize={labelSize} fontFamily="var(--font-outlier)">
        La Niña
      </text>

      <path d={bandPath} fill="var(--color-band-fill)" opacity="0.82" />
      <path
        d={`M ${historicalPath}`}
        fill="none"
        stroke="var(--color-ink-2)"
        strokeWidth="2"
        strokeLinecap="round"
        strokeLinejoin="round"
      />
      <path
        d={`M ${forecastPath}`}
        fill="none"
        stroke="var(--color-accent)"
        strokeWidth="2.2"
        strokeDasharray="5 3"
        strokeLinecap="round"
        strokeLinejoin="round"
      />

      <line
        x1={getX(forecastStart)}
        y1={padTop}
        x2={getX(forecastStart)}
        y2={padTop + innerH}
        stroke="var(--color-rule-2)"
        strokeWidth="1"
        strokeDasharray="3 3"
      />
      <text
        x={getX(forecastStart) - 7}
        y={padTop + 13}
        textAnchor="end"
        fill="var(--color-muted)"
        fontSize={labelSize}
        fontFamily="var(--font-outlier)"
      >
        Observasi
      </text>
      <text
        x={getX(forecastStart) + 7}
        y={padTop + 13}
        fill="var(--color-accent)"
        fontSize={labelSize}
        fontFamily="var(--font-outlier)"
      >
        Prakiraan
      </text>

      <circle cx={getX(forecastStart)} cy={getY(data[forecastStart].value)} r="4" fill="var(--color-ink)" />

      <circle cx={getX(targetIndex)} cy={getY(targetPoint.value)} r="9" fill="none" stroke="var(--color-accent)" opacity="0.45" />
      <circle cx={getX(targetIndex)} cy={getY(targetPoint.value)} r="4.5" fill="var(--color-accent)" />
      <text
        x={getX(targetIndex)}
        y={getY(targetPoint.value) - 13}
        textAnchor="middle"
        fill="var(--color-accent)"
        fontSize={labelSize}
        fontWeight="600"
        fontFamily="var(--font-outlier)"
      >
        +0,94 °C
      </text>

      <circle
        cx={getX(data.length - 1)}
        cy={getY(lastPoint.value)}
        r="3.5"
        fill="var(--color-accent)"
      />

      {xTicks.map(({ point, index }) => (
        <text
          key={point.date}
          x={getX(index)}
          y={padTop + innerH + 20}
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

const dashboardSections = [
  { tab: 'laut', title: 'Peta suhu permukaan laut' },
  { tab: 'dampak', title: 'Anomali curah hujan Indonesia' },
  { tab: 'prakiraan', title: 'Evaluasi model terbuka' },
  { tab: 'metode', title: 'Metodologi dan batasan' }
];

export default function LandingPage({ onOpenDashboard }) {
  return (
    <div className="landing-page-root">
      <header className="landing-nav">
        <div className="landing-nav-inner container">
          <div className="brand-lockup">
            <div className="brand-symbol" aria-hidden="true">
              <svg width="22" height="22" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="16.5" x2="21" y2="16.5" strokeDasharray="2 2" opacity="0.55" />
                <path d="M3.5 18 C 5.5 15.8 7.1 17.4 8.9 15.6 C 11.1 13.4 11.9 11 13.9 9 C 15.5 7.4 16.7 6.4 18.3 4.9" />
                <circle cx="19.2" cy="4.2" r="1.8" fill="currentColor" stroke="none" />
              </svg>
            </div>
            <div className="brand-text">
              <span className="brand-name">KMRV</span>
              <span className="brand-tagline">Proyeksi ENSO Maritim Indonesia</span>
            </div>
          </div>

          <span className="landing-status">Data per {climateDatasetMeta.lastUpdated}</span>

          <button type="button" className="btn btn--primary" onClick={() => onOpenDashboard()}>
            Buka dashboard
          </button>
        </div>
      </header>

      <main>
        <section className="landing-hero container" aria-labelledby="heroTitle">
          <div className="hero-content">
            <h1 id="heroTitle" className="hero-headline">
              Peluang El Niño {lead.elNinoProb}% terbentuk dalam tiga bulan ke depan
            </h1>
            <p className="hero-caption">
              SST harian NOAA OISST v2.1, horizon 1, 3, 6 bulan
            </p>

            <div className="hero-actions">
              <button
                type="button"
                className="btn btn--primary btn--lg"
                onClick={() => onOpenDashboard()}
              >
                Buka dashboard
              </button>
            </div>
          </div>

          <article className="data-card" aria-label="Ringkasan proyeksi terbaru">
            <div className="data-card-head">
              <div>
                <span className="data-kicker">Fase terproyeksi (3 bulan)</span>
                <strong>El Niño lemah hingga moderat</strong>
              </div>
              <span className="dataset-label">{lead.targetMonth}</span>
            </div>

            <div className="trace-frame">
              <TraceChart />
              <TraceChart compact />
            </div>

            <div className="trace-legend" aria-hidden="true">
              <span className="trace-legend-item"><span className="trace-swatch trace-swatch--hist" />Observasi</span>
              <span className="trace-legend-item"><span className="trace-swatch trace-swatch--forecast" />Prakiraan KMRV</span>
              <span className="trace-legend-item"><span className="trace-swatch trace-swatch--band" />Interval 80%</span>
            </div>

            <div className="data-card-readout">
              <div>
                <span className="readout-label">RONI diproyeksikan</span>
                <strong className="readout-value">{lead.roniForecast}</strong>
                <span className="readout-band">{lead.uncertaintyBand} (80% CI)</span>
              </div>
              <span className="readout-meta">Ambang El Niño +0,5 °C</span>
            </div>

            <div className="prob-meter" aria-label="Peluang fase dalam persen">
              <div className="prob-row">
                <span className="prob-label">El Niño</span>
                <div className="prob-track">
                  <div className="prob-fill elnino" style={{ width: `${lead.elNinoProb}%` }} />
                </div>
                <span className="prob-value elnino-high">{lead.elNinoProb}%</span>
              </div>
              <div className="prob-row">
                <span className="prob-label">Netral</span>
                <div className="prob-track">
                  <div className="prob-fill neutral" style={{ width: `${lead.neutralProb}%` }} />
                </div>
                <span className="prob-value">{lead.neutralProb}%</span>
              </div>
              <div className="prob-row">
                <span className="prob-label">La Niña</span>
                <div className="prob-track">
                  <div className="prob-fill lanina" style={{ width: `${lead.laNinaProb}%` }} />
                </div>
                <span className="prob-value">{lead.laNinaProb}%</span>
              </div>
            </div>

            <div className="benchmark-list" aria-label="Perbandingan akurasi">
              <div className="benchmark-row">
                <span className="benchmark-name is-kmrv">KMRV</span>
                <div className="benchmark-track">
                  <div className="benchmark-fill kmrv" style={{ width: `${lead.kmrvMae * 100}%` }} />
                </div>
                <span className="benchmark-score">{lead.kmrvMae.toFixed(2).replace('.', ',')}</span>
              </div>
              <div className="benchmark-row">
                <span className="benchmark-name">Persistensi</span>
                <div className="benchmark-track">
                  <div className="benchmark-fill baseline" style={{ width: `${lead.persMae * 100}%` }} />
                </div>
                <span className="benchmark-score">{lead.persMae.toFixed(2).replace('.', ',')}</span>
              </div>
            </div>
            <p className="card-meta">
              MAE validasi horizon 3 bulan (°C), makin kecil makin akurat.
            </p>
          </article>
        </section>

        <section className="landing-section container" aria-labelledby="featuresTitle">
          <h2 id="featuresTitle" className="section-title">Isi dashboard</h2>

          <div className="feature-list">
            {dashboardSections.map((item) => (
              <button
                key={item.tab}
                type="button"
                className="feature-row"
                onClick={() => onOpenDashboard(item.tab)}
              >
                <span className="feature-row-title">{item.title}</span>
                <span className="feature-row-viz">
                  <Vignette tab={item.tab} />
                </span>
              </button>
            ))}
          </div>
        </section>
      </main>

      <footer className="landing-footer container">
        <div className="footer-inner">
          <div className="footer-col">
            <div className="brand-lockup">
              <div className="brand-symbol" aria-hidden="true">
                <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                  <line x1="3" y1="16.5" x2="21" y2="16.5" strokeDasharray="2 2" opacity="0.55" />
                  <path d="M3.5 18 C 5.5 15.8 7.1 17.4 8.9 15.6 C 11.1 13.4 11.9 11 13.9 9 C 15.5 7.4 16.7 6.4 18.3 4.9" />
                  <circle cx="19.2" cy="4.2" r="1.8" fill="currentColor" stroke="none" />
                </svg>
              </div>
              <span className="brand-name">KMRV</span>
            </div>
            <p className="card-meta">
              Tugas Proyek Mata Kuliah <strong>Sistem Cerdas</strong>, Semester 5,
              Program Studi Sains Data Terapan.
            </p>
          </div>

          <div className="footer-col">
            <span className="footer-col-title">Sumber data</span>
            <p className="card-meta">
              NOAA Daily OISST v2.1, CPC NOAA (RONI, ONI, SOI), BOM Australia (SOI, DMI)
            </p>
          </div>
        </div>
      </footer>
    </div>
  );
}

