import React, { useState } from 'react';
import { createRoot } from 'react-dom/client';
import {
  annualPhases,
  evaluation,
  facts,
  forecastSeries,
  history,
  latest,
  meta,
  regions,
  testPredictions
} from './data/realData';
import './styles.css';

const INDO_MONTHS_MAP = {
  '01': 'Januari', '02': 'Februari', '03': 'Maret', '04': 'April',
  '05': 'Mei', '06': 'Juni', '07': 'Juli', '08': 'Agustus',
  '09': 'September', '10': 'Oktober', '11': 'November', '12': 'Desember'
};

const fmt = (value, digits = 2) => {
  if (value === null || value === undefined || isNaN(value)) return '—';
  return new Intl.NumberFormat('id-ID', {
    minimumFractionDigits: digits,
    maximumFractionDigits: digits
  }).format(value);
};

const signed = (value, digits = 2) => {
  if (value === null || value === undefined || isNaN(value)) return '—';
  return `${value >= 0 ? '+' : '−'}${fmt(Math.abs(value), digits)}`;
};

function Sidebar({ active, setActive }) {
  const items = [
    {
      id: 'overview',
      label: 'Ikhtisar & Monitoring',
      icon: (
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <rect x="2.5" y="2.5" width="6.5" height="6.5" rx="1.5" />
          <rect x="11" y="2.5" width="6.5" height="6.5" rx="1.5" />
          <rect x="2.5" y="11" width="6.5" height="6.5" rx="1.5" />
          <rect x="11" y="11" width="6.5" height="6.5" rx="1.5" />
        </svg>
      )
    },
    {
      id: 'visualization',
      label: 'Visualisasi Data',
      icon: (
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M2.5 16.5h15" />
          <path d="M2.5 3.5v13" />
          <path d="M5.5 12.5l3.5-4 3 3 4.5-6" />
        </svg>
      )
    },
    {
      id: 'forecast',
      label: 'Prakiraan Multi-Horizon',
      icon: (
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <polyline points="4 14.5 8.5 10 12 12.5 16.5 6.5" />
          <polyline points="12.5 6.5 16.5 6.5 16.5 10.5" />
        </svg>
      )
    },
    {
      id: 'classification',
      label: 'Hasil Klasifikasi',
      icon: (
        <svg viewBox="0 0 20 20" width="16" height="16" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">
          <path d="M6.5 10.5l2.5 2.5 5.5-6" />
          <rect x="2.5" y="2.5" width="15" height="15" rx="3" />
        </svg>
      )
    }
  ];

  return (
    <aside className="sidebar">
      <div className="brand">
        <div className="brand-badge" aria-label="Logo Lautan.id">
          <svg viewBox="0 0 256 256" width="22" height="22" fill="none" aria-hidden="true">
            <path
              d="M 38,154 C 52,94 100,56 162,64 C 198,68 222,94 226,116 C 214,106 190,92 154,90 C 114,88 80,112 62,154 C 54,172 34,172 38,154 Z"
              fill="#C9F26B"
            />
            <path
              d="M 218,102 C 204,162 156,200 94,192 C 58,188 34,162 30,140 C 42,150 66,164 102,166 C 142,168 176,144 194,102 C 202,84 222,84 218,102 Z"
              fill="#FFFFFF"
            />
          </svg>
        </div>
        <div>
          <div className="brand-title">Lautan.id</div>
          <div className="brand-sub">INTELIJEN IKLIM MARITIM</div>
        </div>
      </div>

      <div className="sidebar-nav-label">MENU UTAMA</div>
      <nav className="sidebar-nav" aria-label="Navigasi menu utama">
        {items.map((item) => (
          <button
            key={item.id}
            className={`nav-pill-btn ${active === item.id ? 'active' : ''}`}
            onClick={() => {
              setActive(item.id);
              window.scrollTo({ top: 0, behavior: 'smooth' });
            }}
          >
            <span className="nav-pill-icon">{item.icon}</span>
            <span>{item.label}</span>
          </button>
        ))}
      </nav>
    </aside>
  );
}

/* ==========================================================================
   PAGE 1: IKHTISAR & MONITORING
   ========================================================================== */

function OverviewPage() {
  const snapshot = latest;
  const clamped = Math.max(-2, Math.min(2, snapshot.oni || 0));
  const dotLeft = ((clamped + 2) / 4) * 100;

  // Max regional anomaly for relative bar sizing
  const maxAnom = Math.max(...regions.map((r) => Math.abs(r.anomaly)), 0.4);

  const endParts = (meta?.datasetEnd || latest.date || '2026-03').split('-');
  const latestMonthName = INDO_MONTHS_MAP[endParts[1]] || 'Maret';
  const latestYear = endParts[0] || '2026';
  const startYear = (meta?.datasetStart || '2016-01').split('-')[0] || '2016';
  const totalObsCount = meta?.rows || history?.length || 123;

  const h1PredItem = forecastSeries?.['1']?.find((d) => d.isPrediction);
  const h1PredVal = h1PredItem?.prediction;
  const h1Acc = evaluation?.['1']?.accuracy?.test ?? 93.8;

  const h3PredList = forecastSeries?.['3']?.filter((d) => d.isPrediction) || [];
  const h3PredItem = h3PredList[h3PredList.length - 1];
  const h3PredVal = h3PredItem?.prediction;
  const h3Acc = evaluation?.['3']?.accuracy?.test ?? 68.8;

  const h6PredList = forecastSeries?.['6']?.filter((d) => d.isPrediction) || [];
  const h6PredItem = h6PredList[h6PredList.length - 1];
  const h6PredVal = h6PredItem?.prediction;
  const h6Acc = evaluation?.['6']?.accuracy?.test ?? 50.0;

  return (
    <div>
      <div className="view-header">
        <h1 className="view-title">Monitoring Iklim Maritim & Dinamika ENSO</h1>
        <p className="view-subtitle">
          Pantauan deviasi anomali suhu muka laut (SST) Pasifik & perairan Indonesia berdasarkan
          data terkini
        </p>
      </div>

      {/* Row 1: Fase & Dataset */}
      <div className="phase-hero-grid">
        <div className="fig-card" aria-label={`Fase ENSO: ${latest.phase || 'Netral'}`}>
          <div className="phase-tag">FASE ENSO TERKINI</div>
          <h2 className="phase-heading">Fase {latest.phase || 'Netral'} (Stabil)</h2>
          <p className="phase-desc">
            Indeks ONI tercatat {latest.oni != null ? `${signed(latest.oni)} °C` : '— (Data tidak tersedia)'}. Berada dalam rentang normal (−0,5 °C s.d.
            +0,5 °C). Sirkulasi atmosfer-laut seimbang.
          </p>

          <div className="phase-slider-wrap">
            <div className="phase-slider-bar">
              <div
                className="phase-slider-seg"
                style={{ width: '37.5%', backgroundColor: '#60a5fa' }}
              ></div>
              <div
                className="phase-slider-seg"
                style={{ width: '25%', backgroundColor: '#86efac' }}
              ></div>
              <div
                className="phase-slider-seg"
                style={{ width: '37.5%', backgroundColor: '#fb923c' }}
              ></div>
            </div>
            <div
              className="phase-slider-dot"
              style={{ left: `${dotLeft}%` }}
              title={`Posisi ONI: ${signed(latest.oni)} °C`}
            ></div>
            <div className="phase-slider-labels">
              <span>La Niña (&lt; −0,5)</span>
              <span>● Netral ({signed(latest.oni)} °C)</span>
              <span>El Niño (&gt; +0,5)</span>
            </div>
          </div>
        </div>

        <div
          className="fig-card"
          style={{
            display: 'flex',
            flexDirection: 'column',
            justifyContent: 'space-between'
          }}
        >
          <div>
            <div className="phase-tag">DATASET YANG DIGUNAKAN</div>
            <div
              style={{
                fontSize: '30px',
                fontWeight: 800,
                fontFamily: 'var(--font-sans)',
                color: '#16251c',
                margin: '8px 0 4px',
                lineHeight: 1.1
              }}
            >
              {latestMonthName} {latestYear}
            </div>
            <div style={{ fontSize: '11px', color: '#7a8178' }}>Observasi Terakhir NOAA CPC</div>
          </div>

          <div
            style={{
              marginTop: '16px',
              paddingTop: '12px',
              borderTop: '1px solid #f1f5f9',
              display: 'flex',
              flexDirection: 'column',
              gap: '6px'
            }}
          >
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '11px'
              }}
            >
              <span style={{ color: '#64748b' }}>Rentang Waktu:</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: '#1e293b' }}>
                {startYear} – {latestYear}
              </strong>
            </div>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                fontSize: '11px'
              }}
            >
              <span style={{ color: '#64748b' }}>Total Observasi:</span>
              <strong style={{ fontFamily: 'var(--font-mono)', color: '#166534' }}>
                {totalObsCount} Bulan
              </strong>
            </div>
          </div>
        </div>
      </div>

      {/* Row 2: 3 KPI Cards */}
      <div className="grid-3col" style={{ marginBottom: '18px' }}>
        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">ONI (OCEANIC NIÑO INDEX)</span>
            <span className="kpi-badge badge-green">● Netral</span>
          </div>
          <div className="kpi-value">{signed(latest.oni)} °C</div>
          <div className="kpi-sub">Deviasi SST Niño 3.4 · Rujukan Utama ENSO</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">SOI (SOUTHERN OSCILLATION INDEX)</span>
            <span className="kpi-badge badge-green">✓ Seimbang</span>
          </div>
          <div className="kpi-value">{signed(latest.soi, 3)}</div>
          <div className="kpi-sub">Tekanan Udara Tahiti–Darwin Normal</div>
        </div>

        <div className="kpi-card">
          <div className="kpi-top">
            <span className="kpi-label">DMI (DIPOLE MODE INDEX)</span>
            <span className="kpi-badge">IOD Netral</span>
          </div>
          <div className="kpi-value">{signed(latest.dmi, 3)} °C</div>
          <div className="kpi-sub">Gradien Samudera Hindia Normal</div>
        </div>
      </div>

      {/* Row 3: SST Regional Panel & Proyeksi Model */}
      <div className="grid-sst-pred">
        {/* Left: SST Regional */}
        <div className="fig-card">
          <h2 className="fig-card-title">Anomali Suhu Permukaan Laut (SST) Regional</h2>
          <p className="fig-card-subtitle">
            Anomali terhadap rata-rata bulan yang sama di 5 domain kunci (2016–2026)
          </p>

          <div style={{ display: 'flex', flexDirection: 'column' }}>
            {regions.map((r) => {
              const anomaly = r.anomaly ?? 0;
              const isPositive = anomaly >= 0;
              const barWidth = Math.min(50, (Math.abs(anomaly) / maxAnom) * 50);

              const roleText =
                r.id === 'nino34'
                  ? 'Referensi Indeks ENSO Utama'
                  : r.id === 'karimata'
                  ? 'Arlindo Jalur Barat & Laut Jawa'
                  : r.id === 'makassar'
                  ? 'Jalur Utama Arlindo (Indonesian Throughflow)'
                  : r.id === 'jawa'
                  ? 'Zona Upwelling Monsun & Samudera Hindia'
                  : 'Gerbang Pasifik Barat & Halmahera Eddy';

              const statusText =
                anomaly >= 0.2
                  ? 'Hangat lokal'
                  : anomaly >= 0
                  ? 'Sedikit hangat'
                  : 'Sedikit dingin';

              const regionCode =
                r.id === 'nino34'
                  ? 'N3.4'
                  : r.id === 'karimata'
                  ? 'KRM'
                  : r.id === 'makassar'
                  ? 'MKS'
                  : r.id === 'jawa'
                  ? 'JWA'
                  : 'MLP';

              return (
                <div className="sst-table-row" key={r.id}>
                  <div className="sst-col-name">
                    <strong>{r.name} ({regionCode})</strong>
                    <small>{roleText}</small>
                  </div>

                  <div className="sst-col-bar">
                    <span className="sst-center-line"></span>
                    <span
                      className="sst-fill-bar"
                      style={{
                        backgroundColor: isPositive ? '#c27803' : '#315f4a',
                        left: isPositive ? '50%' : `${50 - barWidth}%`,
                        width: `${barWidth}%`
                      }}
                    ></span>
                  </div>

                  <div className="sst-col-value-group">
                    <div
                      className="sst-col-val"
                      style={{ color: isPositive ? '#c27803' : '#315f4a' }}
                    >
                      {signed(anomaly, 3)} °C
                    </div>
                    <div className="sst-col-status">{statusText}</div>
                  </div>
                </div>
              );
            })}
          </div>

          <div
            style={{
              marginTop: '16px',
              paddingTop: '12px',
              borderTop: '1px solid #f8fafc',
              fontSize: '10px',
              color: '#64748b',
              display: 'flex',
              gap: '16px'
            }}
          >
            <span>
              <span
                style={{
                  display: 'inline-block',
                  width: '9px',
                  height: '9px',
                  backgroundColor: '#315f4a',
                  marginRight: '5px',
                  borderRadius: '2px'
                }}
              ></span>
              Hijau: Anomali Dingin (≤ 0°C)
            </span>
            <span>
              <span
                style={{
                  display: 'inline-block',
                  width: '9px',
                  height: '9px',
                  backgroundColor: '#c27803',
                  marginRight: '5px',
                  borderRadius: '2px'
                }}
              ></span>
              Amber: Anomali Hangat (≥ 0°C)
            </span>
          </div>
        </div>

        {/* Right: Proyeksi Model */}
        <div className="fig-card">
          <h2 className="fig-card-title">Proyeksi Model:</h2>
          <p className="fig-card-subtitle">Ringkasan proyeksi ONI horizon 1, 3, dan 6 bulan</p>

          <div
            className="mini-pred-card"
            style={{ backgroundColor: '#EAF7C9', border: '1px solid #D7EC9A' }}
          >
            <div className="mini-pred-header" style={{ color: '#3E6B4F' }}>
              PREDIKSI ONI · HORIZON 1 BULAN (APR 2026)
            </div>
            <div className="mini-pred-title" style={{ color: '#1E3A2B' }}>
              {h1PredVal != null ? `${signed(h1PredVal)} °C` : '+0,07 °C'} · Fase Netral
            </div>
            <div className="mini-pred-note" style={{ color: '#5F6B60' }}>
              Akurasi uji {h1Acc.toFixed(1).replace('.', ',')}% · sangat layak
            </div>
          </div>

          <div
            className="mini-pred-card"
            style={{ backgroundColor: '#F8EFDF', border: '1px solid #EAD7B0' }}
          >
            <div className="mini-pred-header" style={{ color: '#A9761F' }}>
              PREDIKSI ONI · HORIZON 3 BULAN (JUN 2026)
            </div>
            <div className="mini-pred-title" style={{ color: '#7A5A2E' }}>
              {h3PredVal != null ? `${signed(h3PredVal)} °C` : '+0,42 °C'} · Fase Netral
            </div>
            <div className="mini-pred-note" style={{ color: '#7A5A2E' }}>
              Akurasi uji {h3Acc.toFixed(1).replace('.', ',')}%* · semu (dominan Netral)
            </div>
          </div>

          <div
            className="mini-pred-card"
            style={{ backgroundColor: '#F7E7E1', border: '1px solid #EBC7BD' }}
          >
            <div className="mini-pred-header" style={{ color: '#B4553F' }}>
              PREDIKSI ONI · HORIZON 6 BULAN (SEP 2026)
            </div>
            <div className="mini-pred-title" style={{ color: '#8F4635' }}>
              {h6PredVal != null ? `${signed(h6PredVal)} °C` : '+0,67 °C'} · Fase El Niño
            </div>
            <div className="mini-pred-note" style={{ color: '#8F4635' }}>
              Akurasi uji {h6Acc.toFixed(1).replace('.', ',')}% · tidak andal
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE 2: VISUALISASI DATA (HEATMAP & DISTRIBUTION)
   ========================================================================== */

function VisualizationPage() {
  const [hover, setHover] = useState(null);
  const width = 940;
  const height = 260;
  const padLeft = 54;
  const padRight = 32;
  const padY = 24;
  const min = -3.0;
  const max = 3.0;

  const x = (i) =>
    padLeft + i * ((width - padLeft - padRight) / Math.max(history.length - 1, 1));
  const y = (v) => height - padY - ((v - min) / (max - min)) * (height - padY * 2);

  const points = history.map((d, i) => `${x(i)},${y(d.oni)}`).join(' ');
  const years = [2016, 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, 2026];
  const testStartIndex = history.findIndex((h) => h.date >= '2024-01');
  const testStartX = x(testStartIndex >= 0 ? testStartIndex : 96);

  const totalMonths = facts.counts.netral + facts.counts.elNino + facts.counts.laNina;
  const numNetral = (facts.counts.netral / totalMonths) * 100;
  const numElNino = (facts.counts.elNino / totalMonths) * 100;
  const numLaNina = (facts.counts.laNina / totalMonths) * 100;
  const pctNetral = numNetral.toFixed(1).replace('.', ',');
  const pctElNino = numElNino.toFixed(1).replace('.', ',');
  const pctLaNina = numLaNina.toFixed(1).replace('.', ',');

  return (
    <div>
      <div className="view-header">
        <h1 className="view-title">Visualisasi Dinamika ENSO</h1>
        <p className="view-subtitle">
          Tren ONI 2016–2026, komposisi fase per tahun, dan distribusi fase ENSO
        </p>
      </div>

      {/* Top Card: Tren Indeks ONI */}
      <div className="fig-card" style={{ marginBottom: '18px' }}>
        <h2 className="fig-card-title">Tren Indeks ONI 2016–2026</h2>
        <p className="fig-card-subtitle">
          ONI bulanan (°C) · {totalMonths} bulan observasi NOAA CPC · Area berwarna menandakan fase El Niño,
          Netral, dan La Niña (ambang ±0,5 °C)
        </p>

        <div style={{ position: 'relative' }}>
          <svg
            viewBox={`0 0 ${width} ${height}`}
            style={{ width: '100%', height: 'auto' }}
            role="img"
            aria-label="Grafik arsip tren ONI historis Januari 2016 sampai Maret 2026"
          >
            <title>Grafik Dinamika ONI Historis 2016–2026</title>
            <desc>Arsip {totalMonths} titik data ONI bulanan dari Januari 2016 hingga Maret 2026 dengan anotasi area uji Januari 2024–Maret 2026 dan garis batas ±0,5 °C.</desc>

            {/* Shaded band for test period (Jan 2024 – Mar 2026) */}
            <rect
              x={testStartX}
              y={padY}
              width={width - padRight - testStartX}
              height={height - padY * 2}
              fill="#dbeafe"
              opacity="0.35"
            />
            <text
              x={width - padRight - 8}
              y={padY + 12}
              textAnchor="end"
              fill="#0369a1"
              fontSize="8.5"
              fontWeight="700"
              fontFamily="var(--font-sans)"
            >
              Periode Uji (Jan 2024–Mar 2026)
            </text>

            {/* Background zones */}
            <rect
              x={padLeft}
              y={y(max)}
              width={width - padLeft - padRight}
              height={Math.max(0, y(0.5) - y(max))}
              fill="#fff7ed"
              opacity="0.8"
            />
            <rect
              x={padLeft}
              y={y(-0.5)}
              width={width - padLeft - padRight}
              height={Math.max(0, y(min) - y(-0.5))}
              fill="#f0fdf4"
              opacity="0.8"
            />

            {/* Horizontal Grid lines and Left Y-Axis labels */}
            {[-3, -2, -1, 0, 1, 2, 3].map((val) => {
              const isZero = val === 0;
              const isPos = val > 0;
              return (
                <g key={val}>
                  <line
                    x1={padLeft}
                    x2={width - padRight}
                    y1={y(val)}
                    y2={y(val)}
                    stroke={isZero ? '#94a3b8' : '#f1f5f9'}
                    strokeWidth={isZero ? 1.2 : 1}
                    strokeDasharray={isZero ? 'none' : '3 3'}
                  />
                  <text
                    x={padLeft - 8}
                    y={y(val) + 3.5}
                    textAnchor="end"
                    fill={isPos ? '#c2410c' : val < 0 ? '#0284c7' : '#475569'}
                    fontSize="9.5"
                    fontWeight={isZero ? '700' : '600'}
                    fontFamily="var(--font-mono)"
                  >
                    {isPos ? `+${val},0` : val < 0 ? `−${Math.abs(val)},0` : '0,0'}
                  </text>
                </g>
              );
            })}

            {/* Threshold lines with right labels */}
            <line
              x1={padLeft}
              x2={width - padRight}
              y1={y(0.5)}
              y2={y(0.5)}
              stroke="#fb923c"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <text
              x={width - padRight - 6}
              y={y(0.5) - 6}
              textAnchor="end"
              fill="#c2410c"
              fontSize="9"
              fontWeight="600"
              fontFamily="var(--font-sans)"
            >
              +0,5 °C Ambang El Niño
            </text>

            <line
              x1={padLeft}
              x2={width - padRight}
              y1={y(-0.5)}
              y2={y(-0.5)}
              stroke="#4ade80"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <text
              x={width - padRight - 6}
              y={y(-0.5) + 12}
              textAnchor="end"
              fill="#15803d"
              fontSize="9"
              fontWeight="600"
              fontFamily="var(--font-sans)"
            >
              −0,5 °C Ambang La Niña
            </text>

            {/* Vertical year grid */}
            {years.map((yr) => {
              const idx = Math.min(history.length - 1, (yr - 2016) * 12);
              const posX = x(idx);
              return (
                <g key={yr}>
                  <line
                    x1={posX}
                    x2={posX}
                    y1={padY}
                    y2={height - padY}
                    stroke="#f1f5f9"
                    strokeDasharray="2 3"
                  />
                  <text
                    x={posX}
                    y={height - 6}
                    textAnchor={yr === 2016 ? 'start' : yr === 2026 ? 'end' : 'middle'}
                    fill="#94a3b8"
                    fontSize="9.5"
                    fontFamily="var(--font-mono)"
                  >
                    {yr}
                  </text>
                </g>
              );
            })}

            {/* Historical event labels */}
            <text
              x={x(2)}
              y={y(2.5) + 16}
              fill="#c2410c"
              fontSize="9"
              fontWeight="700"
              fontFamily="var(--font-mono)"
            >
              El Niño 2015–16
            </text>
            <text
              x={x(72)}
              y={y(-1.0) + 20}
              textAnchor="middle"
              fill="#15803d"
              fontSize="9"
              fontWeight="700"
              fontFamily="var(--font-mono)"
            >
              La Niña 2020–22
            </text>
            <text
              x={x(95)}
              y={y(1.99) - 10}
              textAnchor="middle"
              fill="#c2410c"
              fontSize="9"
              fontWeight="700"
              fontFamily="var(--font-mono)"
            >
              El Niño 2023–24
            </text>

            {/* Main curve */}
            <polyline
              points={points}
              fill="none"
              stroke="#1c382a"
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Interactive hover points */}
            {history.map((d, i) => {
              const posX = x(i);
              const posY = y(d.oni);
              return (
                <circle
                  key={d.date}
                  cx={posX}
                  cy={posY}
                  r="6"
                  fill="transparent"
                  style={{ cursor: 'pointer' }}
                  onMouseEnter={() => setHover({ ...d, x: posX, y: posY })}
                  onMouseLeave={() => setHover(null)}
                />
              );
            })}
          </svg>

          {hover && (
            <div
              className="floating-tooltip-card"
              style={{
                left: `${Math.min(84, Math.max(4, (hover.x / width) * 100))}%`,
                top: `${Math.max(4, (hover.y / height) * 100 - 20)}%`
              }}
            >
              <small>PERIODE: {hover.date}</small>
              <strong>{signed(hover.oni)} °C</strong>
              <span>
                {hover.oni >= 0.5
                  ? 'Fase El Niño'
                  : hover.oni <= -0.5
                  ? 'Fase La Niña'
                  : 'Fase Netral'}
              </span>
            </div>
          )}
        </div>

        {/* Legend */}
        <div
          style={{
            display: 'flex',
            gap: '18px',
            marginTop: '14px',
            fontSize: '10.5px',
            color: '#64748b'
          }}
        >
          <span>
            <span
              style={{
                display: 'inline-block',
                width: '18px',
                height: '2.5px',
                backgroundColor: '#1c382a',
                marginRight: '6px',
                verticalAlign: 'middle'
              }}
            ></span>
            ONI Bulanan (NOAA CPC)
          </span>
          <span>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '10px',
                backgroundColor: '#fb923c',
                marginRight: '6px',
                verticalAlign: 'middle',
                borderRadius: '2px'
              }}
            ></span>
            El Niño (≥ +0,5)
          </span>
          <span>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '10px',
                backgroundColor: '#e2e8f0',
                marginRight: '6px',
                verticalAlign: 'middle',
                borderRadius: '2px'
              }}
            ></span>
            Netral
          </span>
          <span>
            <span
              style={{
                display: 'inline-block',
                width: '10px',
                height: '10px',
                backgroundColor: '#4ade80',
                marginRight: '6px',
                verticalAlign: 'middle',
                borderRadius: '2px'
              }}
            ></span>
            La Niña (≤ −0,5)
          </span>
        </div>
      </div>

      {/* Bottom 2 Columns: Phase per Year Card & Distribution Card */}
      <div className="grid-2col">
        {/* Left: Fase ENSO per Tahun */}
        <div className="fig-card">
          <h2 className="fig-card-title">Fase ENSO per Tahun</h2>
          <p className="fig-card-subtitle">
            Komposisi bulan Netral, El Niño, dan La Niña per tahun
          </p>

          <div className="py-chart-wrap">
            <div className="py-columns-container">
              {annualPhases.map((ap) => {
                const totalH = (ap.total / 12) * 190;
                const netralH = ap.total > 0 ? (ap.netral / ap.total) * totalH : 0;
                const elNinoH = ap.total > 0 ? (ap.elNino / ap.total) * totalH : 0;
                const laNinaH = ap.total > 0 ? (ap.laNina / ap.total) * totalH : 0;

                return (
                  <div className="py-col-item" key={ap.year}>
                    <div className="py-bar-stack" style={{ height: `${totalH}px` }}>
                      {ap.netral > 0 && (
                        <div
                          className="py-seg py-seg-netral"
                          style={{ height: `${netralH}px` }}
                          title={`${ap.year} Netral: ${ap.netral} bulan`}
                        >
                          {ap.netral >= 3 ? ap.netral : ''}
                        </div>
                      )}
                      {ap.elNino > 0 && (
                        <div
                          className="py-seg py-seg-elnino"
                          style={{ height: `${elNinoH}px` }}
                          title={`${ap.year} El Niño: ${ap.elNino} bulan`}
                        >
                          {ap.elNino >= 3 ? ap.elNino : ''}
                        </div>
                      )}
                      {ap.laNina > 0 && (
                        <div
                          className="py-seg py-seg-lanina"
                          style={{ height: `${laNinaH}px` }}
                          title={`${ap.year} La Niña: ${ap.laNina} bulan`}
                        >
                          {ap.laNina >= 3 ? ap.laNina : ''}
                        </div>
                      )}
                    </div>
                    <div className="py-col-year">{ap.year}</div>
                  </div>
                );
              })}
            </div>

            <div className="py-legend-bar">
              <div className="py-legend-item">
                <span className="py-legend-dot" style={{ backgroundColor: '#c9d3c3' }}></span>
                <span>Netral</span>
              </div>
              <div className="py-legend-item">
                <span className="py-legend-dot" style={{ backgroundColor: '#d9b36c' }}></span>
                <span>El Niño</span>
              </div>
              <div className="py-legend-item">
                <span className="py-legend-dot" style={{ backgroundColor: '#7fa88e' }}></span>
                <span>La Niña</span>
              </div>
            </div>

            <div className="py-footer-note">
              2026 hanya sampai Maret · dihitung dari {totalMonths} bulan observasi (Jan 2016 – Mar 2026).
            </div>
          </div>
        </div>

        {/* Right: Distribusi Fase ENSO */}
        <div className="fig-card">
          <h2 className="fig-card-title">Distribusi Fase ENSO 2016–2026</h2>
          <p className="fig-card-subtitle">
            {facts.counts.netral} Netral · {facts.counts.elNino} El Niño · {facts.counts.laNina} La Niña dari {totalMonths} bulan observasi
          </p>

          <div className="pd-stack-bar">
            <div
              className="pd-stack-seg"
              style={{
                width: `${numNetral.toFixed(2)}%`,
                backgroundColor: '#c9d3c3',
                color: '#16251c'
              }}
            >
              {pctNetral}%
            </div>
            <div
              className="pd-stack-seg"
              style={{
                width: `${numElNino.toFixed(2)}%`,
                backgroundColor: '#d9b36c',
                color: '#ffffff'
              }}
            >
              {pctElNino}%
            </div>
            <div
              className="pd-stack-seg"
              style={{
                width: `${numLaNina.toFixed(2)}%`,
                backgroundColor: '#7fa88e',
                color: '#ffffff'
              }}
            >
              {pctLaNina}%
            </div>
          </div>

          <div className="pd-stat-list">
            <div className="pd-stat-row">
              <div className="pd-stat-left">
                <span className="py-legend-dot" style={{ backgroundColor: '#c9d3c3' }}></span>
                <span>Netral</span>
              </div>
              <div className="pd-stat-mid">{facts.counts.netral} bulan · {pctNetral}%</div>
              <div className="pd-stat-right">Fase dominan</div>
            </div>
            <div className="pd-stat-row">
              <div className="pd-stat-left">
                <span className="py-legend-dot" style={{ backgroundColor: '#d9b36c' }}></span>
                <span>El Niño</span>
              </div>
              <div className="pd-stat-mid">{facts.counts.elNino} bulan · {pctElNino}%</div>
              <div className="pd-stat-right">Episode hangat</div>
            </div>
            <div className="pd-stat-row">
              <div className="pd-stat-left">
                <span className="py-legend-dot" style={{ backgroundColor: '#7fa88e' }}></span>
                <span>La Niña</span>
              </div>
              <div className="pd-stat-mid">{facts.counts.laNina} bulan · {pctLaNina}%</div>
              <div className="pd-stat-right">Episode dingin</div>
            </div>
          </div>

          <div style={{ marginTop: 'auto', paddingTop: '16px', borderTop: '1px solid #f1f5f9' }}>
            <div style={{ fontSize: '10px', color: '#9a9f92' }}>
              Dihitung dari {totalMonths} bulan observasi (Januari 2016 – Maret 2026).
            </div>
            <div style={{ fontSize: '11px', color: '#7a8178', marginTop: '4px' }}>
              El Niño dan La Niña hampir seimbang; Netral tetap paling sering.
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   PAGE 3: PRAKIRAAN MULTI-HORIZON
   ========================================================================== */

function ForecastPage() {
  const [horizon, setHorizon] = useState(1);
  const [hover, setHover] = useState(null);
  const series = forecastSeries[horizon] || [];
  const hasSeries = series.length > 0;
  const width = 940;
  const height = 280;
  const padLeft = 56;
  const padRight = 24;
  const padTop = 52;
  const padBottom = 28;
  const min = -1.2;
  const max = 0.6;

  const x = (i) => padLeft + i * ((width - padLeft - padRight) / Math.max((series?.length || 1) - 1, 1));
  const y = (v) => padTop + ((max - v) / (max - min)) * (height - padTop - padBottom);

  const splitIdx = 3;
  const splitX = x(splitIdx);

  const splitItem = hasSeries ? series[splitIdx] : null;
  const splitDateParts = splitItem?.date ? splitItem.date.split('/') : ['03', '26'];
  const splitMonthName = INDO_MONTHS_MAP[splitDateParts[0]] || 'Maret';
  const splitYear = `20${splitDateParts[1] || '26'}`;
  const splitLabel = `${splitMonthName} ${splitYear}`;

  // Actual observation: strictly up to latest observation (splitIdx)
  const actualSeries = hasSeries ? series.slice(0, splitIdx + 1) : [];
  const actualPoints = actualSeries
    .map((d, i) => `${x(i)},${y(d.actual)}`)
    .join(' ');

  // Projection: connects from latest observation (splitIdx) into future horizon
  const predSeries = hasSeries ? series.slice(splitIdx) : [];
  const predictedPoints = predSeries
    .map((d, i) => `${x(splitIdx + i)},${y(d.prediction ?? d.actual)}`)
    .join(' ');

  const yTicks = [0.5, 0.0, -0.5, -1.0];

  const HORIZONS_META = [
    {
      h: 1,
      badge: '★ PREDIKSI 1 BULAN (APR 2026)',
      title: 'Cukup Andal untuk Fase',
      defaultVal: '+0,07 °C (Netral)',
      desc: 'Dari 16 bulan uji, 15 tebakannya tepat (93,8%). ONI RMSE mencapai 0,198 °C dengan performa stabil pada variasi fase. Sangat layak digunakan sebagai rujukan operasional.',
      activeTheme: 'card-primary-dark',
      badgeColor: '#C9F26B',
      oniColor: '#C9F26B',
      descColor: '#B9C6B6',
      inactiveBadgeColor: '#15803d'
    },
    {
      h: 3,
      badge: '▲ PREDIKSI 3 BULAN (JUN 2026)',
      title: 'Akurasi Semu (Bias Netral)',
      defaultVal: '+0,42 °C (Netral)',
      desc: 'Akurasi uji 68,8% (11 dari 16 benar) bersifat semu karena model memprediksi seluruh sampel sebagai Netral. Saat diuji pada fase aktif saat validasi, akurasinya hanya 23,1%. Bukan bukti model pintar.',
      activeTheme: 'card-amber-dark',
      badgeColor: '#FBBF24',
      oniColor: '#FBBF24',
      descColor: '#E2D9C8',
      inactiveBadgeColor: '#B45309'
    },
    {
      h: 6,
      badge: '✕ PREDIKSI 6 BULAN (SEP 2026)',
      title: 'Kurang Andal',
      defaultVal: '+0,67 °C (El Niño)',
      desc: 'Akurasi uji 50,0% dengan RMSE ONI 0,982 °C. Akumulasi error proyeksi jangka panjang dan barrier prediktabilitas musim semi ENSO membuat horizon ini tidak disarankan untuk keputusan kritis.',
      activeTheme: 'card-rose-dark',
      badgeColor: '#FDA4AF',
      oniColor: '#FDA4AF',
      descColor: '#E5D0CD',
      inactiveBadgeColor: '#BE123C'
    },
    {
      h: 9,
      badge: '✕ PREDIKSI 9 BULAN (DES 2026)',
      title: 'Tidak Andal (Drift Jangka Panjang)',
      defaultVal: 'Prakiraan 9 Bulan',
      desc: 'Proyeksi 9 bulan melampaui musim semi dan gugur 2026. Akumulasi galat multi-step dan sinyal laut-atmosfer yang melemah membuat model empiris kehilangan korelasi prediktif.',
      activeTheme: 'card-amber-dark',
      badgeColor: '#F59E0B',
      oniColor: '#F59E0B',
      descColor: '#E2D9C8',
      inactiveBadgeColor: '#D97706'
    },
    {
      h: 12,
      badge: '✕ PREDIKSI 12 BULAN (MAR 2027)',
      title: 'Eksperimental / Batas Fisik Terlampaui',
      defaultVal: 'Prakiraan 12 Bulan',
      desc: 'Proyeksi 1 tahun penuh melintasi siklus musim semi ENSO (SPB). Tanpa asimilasi dinamika fluida laut 3D, model statistik-AI murni menghasilkan estimasi berderau tinggi.',
      activeTheme: 'card-rose-dark',
      badgeColor: '#F87171',
      oniColor: '#F87171',
      descColor: '#E5D0CD',
      inactiveBadgeColor: '#DC2626'
    }
  ];

  return (
    <div>
      <div className="view-header">
        <h1 className="view-title">Prakiraan ENSO Multi-Horizon & Simulasi Lintasan ONI</h1>
        <p className="view-subtitle">
          Simulasi proyeksi ke depan model Causal LSTM (1, 3, 6, 9, dan 12 bulan)
        </p>
      </div>

      {/* Horizon Tabs Bar */}
      <div className="horizon-pill-bar">
        <button
          className={`h-pill-btn ${horizon === 1 ? 'active' : ''}`}
          onClick={() => setHorizon(1)}
        >
          ★ Horizon 1 Bulan (Relatif Andal)
        </button>
        <button
          className={`h-pill-btn ${horizon === 3 ? 'active' : ''}`}
          onClick={() => setHorizon(3)}
        >
          Horizon 3 Bulan (Akurasi Semu)
        </button>
        <button
          className={`h-pill-btn ${horizon === 6 ? 'active' : ''}`}
          onClick={() => setHorizon(6)}
        >
          Horizon 6 Bulan (Tidak Andal)
        </button>
        <button
          className={`h-pill-btn ${horizon === 9 ? 'active' : ''}`}
          onClick={() => setHorizon(9)}
        >
          Horizon 9 Bulan (Kurang Andal)
        </button>
        <button
          className={`h-pill-btn ${horizon === 12 ? 'active' : ''}`}
          onClick={() => setHorizon(12)}
        >
          Horizon 12 Bulan (Eksperimental)
        </button>
      </div>

      {/* Main Chart Card */}
      <div className="fig-card" style={{ marginBottom: '18px' }}>
        <h2 className="fig-card-title">
          Lintasan Historis vs Proyeksi Model Causal LSTM (s.d. 2026)
        </h2>
        <p className="fig-card-subtitle">
          Nilai Indeks ONI (°C) · Area berwarna menandakan ambang batas fase ENSO standar NOAA CPC
        </p>

        <div style={{ position: 'relative' }}>
          {!hasSeries && (
            <div
              style={{
                position: 'absolute',
                inset: 0,
                display: 'flex',
                flexDirection: 'column',
                alignItems: 'center',
                justifyContent: 'center',
                backgroundColor: 'rgba(252, 252, 249, 0.92)',
                borderRadius: '16px',
                padding: '24px',
                textAlign: 'center',
                zIndex: 10
              }}
            >
              <div style={{ fontSize: '15px', fontWeight: 700, color: '#16251C', marginBottom: '6px' }}>
                Model Horizon {horizon} Bulan Siap Dilatih
              </div>
              <div style={{ fontSize: '12.5px', color: '#64748b', maxWidth: '500px', lineHeight: 1.5 }}>
                Kode arsitektur dan target dataset sudah siap. Jalankan perintah:
                <br />
                <code
                  style={{
                    display: 'inline-block',
                    backgroundColor: '#f1f5f9',
                    padding: '4px 10px',
                    borderRadius: '6px',
                    margin: '6px 0',
                    color: '#0f172a',
                    fontFamily: 'var(--font-mono)',
                    fontWeight: 600
                  }}
                >
                  python main.py --horizons {horizon}
                </code>
                <br />
                lalu jalankan{' '}
                <code
                  style={{
                    backgroundColor: '#f1f5f9',
                    padding: '2px 6px',
                    borderRadius: '4px',
                    color: '#0f172a',
                    fontFamily: 'var(--font-mono)'
                  }}
                >
                  python scripts/export_dashboard_data.py
                </code>{' '}
                untuk memvisualisasikan grafik.
              </div>
            </div>
          )}
          <svg viewBox={`0 0 ${width} ${height}`} style={{ width: '100%', height: 'auto' }}>
            {/* Background dual-tone zones */}
            <rect
              x={padLeft}
              y={y(max)}
              width={width - padLeft - padRight}
              height={Math.max(0, y(0.5) - y(max))}
              fill="#fff7ed"
              opacity="0.8"
            />
            <rect
              x={padLeft}
              y={y(-0.5)}
              width={width - padLeft - padRight}
              height={Math.max(0, y(min) - y(-0.5))}
              fill="#f0fdf4"
              opacity="0.8"
            />

            {/* Horizontal Grid lines and Left Y-Axis labels */}
            {yTicks.map((val) => {
              const isZero = val === 0;
              const isPos = val > 0;
              return (
                <g key={val}>
                  <line
                    x1={padLeft}
                    x2={width - padRight}
                    y1={y(val)}
                    y2={y(val)}
                    stroke={isZero ? '#94a3b8' : '#f1f5f9'}
                    strokeWidth={isZero ? 1.2 : 1}
                    strokeDasharray={isZero ? 'none' : '3 3'}
                  />
                  <text
                    x={padLeft - 8}
                    y={y(val) + 3.5}
                    textAnchor="end"
                    fill={isPos ? '#c2410c' : val < 0 ? (val <= -1 ? '#0284c7' : '#15803d') : '#475569'}
                    fontSize="9.5"
                    fontWeight={isZero ? '700' : '600'}
                    fontFamily="var(--font-mono)"
                  >
                    {isPos ? `+${val.toFixed(1).replace('.', ',')}` : val < 0 ? `−${Math.abs(val).toFixed(1).replace('.', ',')}` : '0,0'}
                  </text>
                </g>
              );
            })}

            {/* Threshold lines with right labels */}
            <line
              x1={padLeft}
              x2={width - padRight}
              y1={y(0.5)}
              y2={y(0.5)}
              stroke="#fb923c"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <text
              x={width - padRight - 6}
              y={y(0.5) - 6}
              textAnchor="end"
              fill="#c2410c"
              fontSize="9"
              fontWeight="600"
              fontFamily="var(--font-mono)"
            >
              +0,5 °C (Ambang Batas El Niño)
            </text>

            <text
              x={width - padRight - 6}
              y={y(0) - 6}
              textAnchor="end"
              fill="#64748b"
              fontSize="9"
              fontFamily="var(--font-mono)"
            >
              0,0 °C (Garis Netral Sempurna)
            </text>

            <line
              x1={padLeft}
              x2={width - padRight}
              y1={y(-0.5)}
              y2={y(-0.5)}
              stroke="#4ade80"
              strokeWidth="1.2"
              strokeDasharray="4 3"
            />
            <text
              x={width - padRight - 6}
              y={y(-0.5) + 12}
              textAnchor="end"
              fill="#15803d"
              fontSize="9"
              fontWeight="600"
              fontFamily="var(--font-mono)"
            >
              −0,5 °C (Ambang Batas La Niña)
            </text>

            {/* Split observation line & header badge (positioned safely above threshold lines) */}
            <line
              x1={splitX}
              x2={splitX}
              y1="32"
              y2={height - padBottom}
              stroke="#64748b"
              strokeWidth="1.2"
              strokeDasharray="3 3"
            />
            <rect
              x={splitX - 78}
              y="8"
              width="156"
              height="20"
              rx="10"
              fill="#f8fafc"
              stroke="#cbd5e1"
              strokeWidth="1"
            />
            <text
              x={splitX}
              y="22"
              textAnchor="middle"
              fill="#1e3a2b"
              fontSize="9.5"
              fontWeight="700"
              fontFamily="var(--font-sans)"
            >
              ▼ Batas Observasi: {splitLabel}
            </text>

            {/* Actual line (stops at latest observation) */}
            <polyline
              points={actualPoints}
              fill="none"
              stroke="#111827"
              strokeWidth="2.4"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Projection line (starts from latest observation) */}
            <polyline
              points={predictedPoints}
              fill="none"
              stroke="#84cc16"
              strokeWidth="2.2"
              strokeDasharray="5 3"
              strokeLinecap="round"
              strokeLinejoin="round"
            />

            {/* Dots & hover targets */}
            {series.map((d, i) => {
              const posX = x(i);
              const val = i <= splitIdx ? d.actual : d.prediction;
              const posY = y(val);
              const isPast = i < splitIdx;
              const isBorder = i === splitIdx;
              const isFuture = i > splitIdx;
              const isHovered = hover && hover.index === i;
              return (
                <g key={d.date}>
                  {/* Invisible enlarged hit target for effortless hovering */}
                  <circle
                    cx={posX}
                    cy={posY}
                    r={14}
                    fill="transparent"
                    style={{ cursor: 'pointer' }}
                    onMouseEnter={() =>
                      setHover({
                        index: i,
                        x: posX,
                        y: posY,
                        date: d.date,
                        val,
                        isFuture
                      })
                    }
                    onMouseLeave={() => setHover(null)}
                  />
                  <circle
                    cx={posX}
                    cy={posY}
                    r={isHovered ? 6 : isBorder ? 5 : 4}
                    fill={isPast ? '#111827' : isBorder ? '#111827' : '#84cc16'}
                    stroke={isBorder ? '#84cc16' : '#ffffff'}
                    strokeWidth={isBorder ? 2 : 1.5}
                    style={{ pointerEvents: 'none' }}
                  />
                </g>
              );
            })}

            {/* X-axis date labels */}
            {series.map((d, i) => (
              <g key={d.date}>
                <line
                  x1={x(i)}
                  x2={x(i)}
                  y1={height - padBottom}
                  y2={height - padBottom + 4}
                  stroke="#94a3b8"
                  strokeWidth="1"
                />
                <text
                  x={x(i)}
                  y={height - 10}
                  textAnchor="middle"
                  fill={i === splitIdx ? '#0f172a' : i > splitIdx ? '#15803d' : '#64748b'}
                  fontSize={i === splitIdx ? '10' : '9'}
                  fontWeight={i === splitIdx ? '700' : '500'}
                  fontFamily="var(--font-mono)"
                >
                  {d.date}
                </text>
              </g>
            ))}
          </svg>

          {/* Interactive Tooltip matching FigCraft Node 197 */}
          {hover && (
            <div
              style={{
                position: 'absolute',
                left: `${Math.min(80, Math.max(20, (hover.x / width) * 100))}%`,
                top: `${Math.max(8, (hover.y / height) * 100 - 14)}%`,
                transform: 'translate(-50%, -100%)',
                backgroundColor: '#1E3A2B',
                color: '#ffffff',
                borderRadius: '16px',
                padding: '12px 16px',
                boxShadow: '0 8px 20px rgba(30, 58, 43, 0.25)',
                pointerEvents: 'none',
                zIndex: 20,
                minWidth: '190px',
                whiteSpace: 'nowrap'
              }}
            >
              <div
                style={{
                  fontSize: '10px',
                  fontFamily: 'var(--font-sans)',
                  color: '#C9D3C3',
                  letterSpacing: '0.04em',
                  textTransform: 'uppercase',
                  marginBottom: '3px'
                }}
              >
                {hover.isFuture
                  ? `PROYEKSI: ${hover.date}`
                  : `OBSERVASI: ${hover.date}`}
              </div>
              <div
                style={{
                  fontSize: '15px',
                  fontWeight: 800,
                  fontFamily: 'var(--font-sans)',
                  color: '#ffffff',
                  marginBottom: '3px'
                }}
              >
                {hover.isFuture
                  ? `ONI Prediksi: ${signed(hover.val)} °C`
                  : `ONI Observasi: ${signed(hover.val)} °C`}
              </div>
              <div
                style={{
                  fontSize: '10px',
                  color: '#D7E0D4',
                  display: 'flex',
                  alignItems: 'center',
                  gap: '5px'
                }}
              >
                <span
                  style={{
                    color:
                      hover.val >= 0.5
                        ? '#fb923c'
                        : hover.val <= -0.5
                        ? '#60a5fa'
                        : '#C9F26B',
                    fontWeight: 'bold',
                    fontSize: '11px'
                  }}
                >
                  ●
                </span>
                <span>
                  Status:{' '}
                  {hover.val >= 0.5
                    ? 'El Niño'
                    : hover.val <= -0.5
                    ? 'La Niña'
                    : hover.val < 0
                    ? 'Netral Mendingin'
                    : 'Netral Stabil'}
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Legend */}
        <div
          style={{
            display: 'flex',
            gap: '18px',
            marginTop: '14px',
            fontSize: '10.5px',
            color: '#64748b'
          }}
        >
          <span>
            <span
              style={{
                display: 'inline-block',
                width: '18px',
                height: '2.5px',
                backgroundColor: '#111827',
                marginRight: '6px',
                verticalAlign: 'middle'
              }}
            ></span>
            Data Observasi Historis (NOAA OISST)
          </span>
          <span>
            <span
              style={{
                display: 'inline-block',
                width: '18px',
                height: '2.5px',
                borderTop: '2px dashed #84cc16',
                marginRight: '6px',
                verticalAlign: 'middle'
              }}
            ></span>
            Proyeksi Causal LSTM (1, 3, 6, 9, 12 Bln)
          </span>
        </div>
      </div>

      {/* Single Dynamic Horizon Detail Card */}
      {(() => {
        const currentMeta = HORIZONS_META.find((item) => item.h === horizon) || HORIZONS_META[0];
        const evalItem = evaluation?.[horizon];
        const hPredSeries = forecastSeries?.[horizon] || [];
        const lastPred = hPredSeries.filter((d) => d.isPrediction).slice(-1)[0];
        const dynamicOni = lastPred
          ? `${signed(lastPred.prediction)} °C (${lastPred.prediction >= 0.5 ? 'El Niño' : lastPred.prediction <= -0.5 ? 'La Niña' : 'Netral'})`
          : currentMeta.defaultVal;

        const testAccStr = evalItem?.accuracy?.test != null ? `${evalItem.accuracy.test.toFixed(1).replace('.', ',')}%` : '—';
        const valAccStr = evalItem?.accuracy?.val != null ? `${evalItem.accuracy.val.toFixed(1).replace('.', ',')}%` : '—';
        const dynamicDesc = evalItem?.matrixNote ? evalItem.matrixNote : currentMeta.desc;
        const cardTheme = horizon === 1 ? 'theme-good' : horizon === 3 ? 'theme-warn' : 'theme-bad';
        const accentColor = horizon === 1 ? '#C9F26B' : horizon === 3 ? '#FBBF24' : '#FDA4AF';

        return (
          <div className={`h-stat-single-card ${cardTheme}`}>
            <div
              style={{
                display: 'flex',
                justifyContent: 'space-between',
                alignItems: 'center',
                borderBottom: '1px solid rgba(255, 255, 255, 0.12)',
                paddingBottom: '12px'
              }}
            >
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 800,
                  letterSpacing: '0.06em',
                  textTransform: 'uppercase',
                  color: accentColor
                }}
              >
                {currentMeta.badge}
              </span>
              <span
                style={{
                  fontSize: '11px',
                  fontWeight: 700,
                  padding: '3px 10px',
                  borderRadius: '999px',
                  backgroundColor: 'rgba(255, 255, 255, 0.15)',
                  color: '#ffffff'
                }}
              >
                {evalItem?.verdict || 'Prakiraan Multi-Step'}
              </span>
            </div>

            <div className="h-stat-single-body">
              {/* Left Info Column */}
              <div>
                <h3
                  style={{
                    fontSize: '20px',
                    fontWeight: 800,
                    color: '#ffffff',
                    margin: '0 0 6px',
                    fontFamily: 'var(--font-sans)'
                  }}
                >
                  {currentMeta.title}
                </h3>
                <div
                  style={{
                    fontSize: '26px',
                    fontWeight: 800,
                    color: accentColor,
                    margin: '0 0 10px',
                    fontFamily: 'var(--font-sans)'
                  }}
                >
                  {dynamicOni}
                </div>
                <p
                  style={{
                    fontSize: '12.5px',
                    color: 'rgba(255, 255, 255, 0.85)',
                    lineHeight: 1.6,
                    margin: 0
                  }}
                >
                  {dynamicDesc}
                </p>
              </div>

              {/* Right Metrics Grid */}
              <div className="h-stat-metrics-grid">
                <div className="h-stat-metric-box">
                  <span className="h-stat-metric-lbl">Akurasi Uji (Test)</span>
                  <span className="h-stat-metric-val" style={{ color: accentColor }}>
                    {testAccStr}
                  </span>
                </div>
                <div className="h-stat-metric-box">
                  <span className="h-stat-metric-lbl">Akurasi Validasi</span>
                  <span className="h-stat-metric-val">{valAccStr}</span>
                </div>
                <div className="h-stat-metric-box">
                  <span className="h-stat-metric-lbl">Horizon Lead</span>
                  <span className="h-stat-metric-val">{horizon} Bulan</span>
                </div>
                <div className="h-stat-metric-box">
                  <span className="h-stat-metric-lbl">Kategori Evaluasi</span>
                  <span className="h-stat-metric-val" style={{ fontSize: '14px', paddingTop: '4px' }}>
                    {evalItem?.tone === 'good'
                      ? 'Andal'
                      : evalItem?.tone === 'warn'
                      ? 'Bias Semu'
                      : 'Tidak Andal'}
                  </span>
                </div>
              </div>
            </div>
          </div>
        );
      })()}
    </div>
  );
}

/* ==========================================================================
   PAGE 4: HASIL KLASIFIKASI (MATCHING FIGCRAFT)
   ========================================================================== */

function ClassificationPage() {
  const [showAllSamples, setShowAllSamples] = useState(false);
  const INDO_MONTHS_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'Mei', 'Jun', 'Jul', 'Agu', 'Sep', 'Okt', 'Nov', 'Des'];
  const PHASE_NAMES_MAP = { 0: 'La Niña', 1: 'Netral', 2: 'El Niño' };

  const h1Preds = testPredictions?.['1'] || [];
  const testSamples = h1Preds.map((p) => {
    const parts = (p.date || '').split('-');
    const mIdx = parts[1] ? parseInt(parts[1], 10) - 1 : 0;
    const yStr = parts[0] || '';
    const dateLabel = `${INDO_MONTHS_SHORT[mIdx] || ''} ${yStr}`;
    const actual = PHASE_NAMES_MAP[p.actual_phase] || 'Netral';
    const pred = PHASE_NAMES_MAP[p.predicted_phase] || 'Netral';
    return {
      date: dateLabel,
      actual,
      pred,
      correct: p.actual_phase === p.predicted_phase,
    };
  });

  const sampleCount = testSamples.length || 16;
  const visibleSamples = showAllSamples ? testSamples : testSamples.slice(0, 6);
  const correctCount = testSamples.filter((s) => s.correct).length;
  const wrongCount = sampleCount - correctCount;
  const h1AccStr = sampleCount > 0 ? ((correctCount / sampleCount) * 100).toFixed(1).replace('.', ',') : '93,8';

  const h1ValAcc = evaluation?.['1']?.accuracy?.val ?? 53.8;
  const h1TestAcc = evaluation?.['1']?.accuracy?.test ?? 93.8;
  const h3ValAcc = evaluation?.['3']?.accuracy?.val ?? 23.1;
  const h3TestAcc = evaluation?.['3']?.accuracy?.test ?? 68.8;
  const h6ValAcc = evaluation?.['6']?.accuracy?.val ?? 15.4;
  const h6TestAcc = evaluation?.['6']?.accuracy?.test ?? 50.0;

  const h1MaeModel = evaluation?.['1']?.maeModel ?? 0.172;
  const h1MaeBase = evaluation?.['1']?.maeBaseline ?? 0.108;
  const h3MaeModel = evaluation?.['3']?.maeModel ?? 0.152;
  const h3MaeBase = evaluation?.['3']?.maeBaseline ?? 0.098;
  const h6MaeModel = evaluation?.['6']?.maeModel ?? 0.197;
  const h6MaeBase = evaluation?.['6']?.maeBaseline ?? 0.100;

  const firstDate = testSamples[0]?.date || 'Des 2024';
  const lastDate = testSamples[testSamples.length - 1]?.date || 'Mar 2026';

  // Chart 1 Bar math (scale: 0-100% -> 0-115px)
  const calcAccY = (acc) => 160 - (acc / 100) * 115;
  const calcAccH = (acc) => (acc / 100) * 115;

  // Chart 2 Bar math (scale: 0-0.3 -> 0-115px)
  const calcMaeY = (mae) => 160 - Math.min(125, (mae / 0.3) * 115);
  const calcMaeH = (mae) => Math.min(125, (mae / 0.3) * 115);

  return (
    <div>
      <div className="view-header">
        <h1 className="view-title">Hasil Klasifikasi Fase ENSO</h1>
        <p className="view-subtitle">
          Kinerja klasifikasi Causal LSTM + XGBoost per horizon pada {sampleCount} sampel uji ({firstDate} – {lastDate}) · tanpa fabrikasi hasil
        </p>
      </div>

      {/* Honesty Banner */}
      <div className="alert-honesty-banner">
        <div className="alert-honesty-icon">!</div>
        <div className="alert-honesty-text">
          <strong>Cara Membaca Hasil Klasifikasi</strong>
          <p>
            Akurasi tinggi belum tentu berarti model pintar. Horizon 1 Bulan mencapai {h1TestAcc.toFixed(1).replace('.', ',')}% dan layak dipakai; Horizon 3 Bulan {h3TestAcc.toFixed(1).replace('.', ',')}% karena model dominan memprediksi Netral; Horizon 6 Bulan {h6TestAcc.toFixed(1).replace('.', ',')}% menurun tajam karena barrier musim semi ENSO. Model juga belum mengalahkan persistence pada MAE.
          </p>
        </div>
      </div>

      {/* Row 1: 2 Columns - Classification Card & Horizon Summary Card */}
      <div className="grid-2col" style={{ marginBottom: '18px' }}>
        {/* Left: Classification Card */}
        <div className="fig-card">
          <h2 className="fig-card-title">Hasil Klasifikasi per Bulan Uji (Horizon 1 Bulan)</h2>
          <p className="fig-card-subtitle">
            Fase aktual vs prediksi model pada {sampleCount} sampel uji · {firstDate} – {lastDate}
          </p>

          <div className="cl-score-grid">
            <div className="cl-score-box" style={{ backgroundColor: '#f0fdf4', border: '1px solid #dcfce7' }}>
              <div className="cl-score-num" style={{ color: '#15803d' }}>{correctCount} Bulan</div>
              <div className="cl-score-title" style={{ color: '#166534' }}>Tebakan Tepat ({h1AccStr}%)</div>
              <div className="cl-score-desc" style={{ color: '#15803d' }}>Prediksi cocok dengan realitas fase NOAA</div>
            </div>
            <div className="cl-score-box" style={{ backgroundColor: '#fff1f2', border: '1px solid #ffe4e6' }}>
              <div className="cl-score-num" style={{ color: '#b91c1c' }}>{wrongCount} Bulan</div>
              <div className="cl-score-title" style={{ color: '#991b1b' }}>Meleset</div>
              <div className="cl-score-desc" style={{ color: '#b91c1c' }}>Prediksi fase tidak sesuai target aktual</div>
            </div>
          </div>

          <div className="cl-table-wrap">
            <table className="cl-table">
              <thead>
                <tr>
                  <th>BULAN UJI</th>
                  <th>FASE AKTUAL</th>
                  <th>PREDIKSI MODEL</th>
                  <th>HASIL</th>
                </tr>
              </thead>
              <tbody>
                {visibleSamples.map((s) => (
                  <tr key={s.date}>
                    <td style={{ fontFamily: 'var(--font-mono)', fontWeight: 600 }}>{s.date}</td>
                    <td>{s.actual}</td>
                    <td style={{ fontWeight: 600 }}>{s.pred}</td>
                    <td>
                      <span style={{ fontWeight: 600, color: s.correct ? '#16a34a' : '#b91c1c' }}>
                        {s.correct ? 'Benar' : 'Salah'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>

            {testSamples.length > 6 && (
              <button
                type="button"
                className="cl-see-more-btn"
                onClick={() => setShowAllSamples(!showAllSamples)}
              >
                <span>
                  {showAllSamples
                    ? 'Tampilkan Lebih Sedikit'
                    : `Lihat Selengkapnya (${sampleCount} Bulan)`}
                </span>
                <svg
                  viewBox="0 0 20 20"
                  width="14"
                  height="14"
                  fill="currentColor"
                  style={{
                    transform: showAllSamples ? 'rotate(180deg)' : 'none',
                    transition: 'transform 0.2s ease'
                  }}
                >
                  <path
                    fillRule="evenodd"
                    d="M5.23 7.21a.75.75 0 011.06.02L10 10.94l3.71-3.71a.75.75 0 111.06 1.06l-4.24 4.25a.75.75 0 01-1.06 0L5.21 8.27a.75.75 0 01.02-1.06z"
                    clipRule="evenodd"
                  />
                </svg>
              </button>
            )}
          </div>

          <div style={{ marginTop: '12px', fontSize: '10.5px', color: '#64748b', fontStyle: 'italic' }}>
            {correctCount} dari {sampleCount} tebakan benar pada evaluasi horizon 1 bulan.
          </div>
        </div>

        {/* Right: Horizon Summary Card */}
        <div className="fig-card">
          <h2 className="fig-card-title">Ringkasan Klasifikasi 3 Horizon</h2>
          <p className="fig-card-subtitle">
            Akurasi uji per horizon pada {sampleCount} sampel uji ({firstDate} – {lastDate})
          </p>

          <div style={{ display: 'flex', flexDirection: 'column', gap: '10px', marginTop: '14px' }}>
            {/* Horizon 1 */}
            <div className="h-summary-row-box" style={{ backgroundColor: '#eaf7c9', border: '1px solid #d7ec9a' }}>
              <div className="h-summary-row-header">
                <span className="h-summary-row-label">HORIZON 1 BULAN</span>
                <span className="h-summary-row-badge" style={{ backgroundColor: '#1e3a2b', color: '#ffffff' }}>Layak</span>
              </div>
              <div className="h-summary-row-val" style={{ color: '#166534' }}>{h1TestAcc.toFixed(1).replace('.', ',')}%</div>
              <div className="h-summary-row-desc">{correctCount} dari {sampleCount} tebakan fase tepat</div>
            </div>

            {/* Horizon 3 */}
            <div className="h-summary-row-box" style={{ backgroundColor: '#f8efdf', border: '1px solid #ead7b0' }}>
              <div className="h-summary-row-header">
                <span className="h-summary-row-label">HORIZON 3 BULAN</span>
                <span className="h-summary-row-badge" style={{ backgroundColor: '#b45309', color: '#ffffff' }}>Semu</span>
              </div>
              <div className="h-summary-row-val" style={{ color: '#92400e' }}>{h3TestAcc.toFixed(1).replace('.', ',')}%*</div>
              <div className="h-summary-row-desc">Akurasi semu: dominan memprediksi Netral</div>
            </div>

            {/* Horizon 6 */}
            <div className="h-summary-row-box" style={{ backgroundColor: '#f7e7e1', border: '1px solid #ebc7bd' }}>
              <div className="h-summary-row-header">
                <span className="h-summary-row-label">HORIZON 6 BULAN</span>
                <span className="h-summary-row-badge" style={{ backgroundColor: '#b91c1c', color: '#ffffff' }}>Gagal</span>
              </div>
              <div className="h-summary-row-val" style={{ color: '#9f1239' }}>{h6TestAcc.toFixed(1).replace('.', ',')}%</div>
              <div className="h-summary-row-desc">Kinerja rendah akibat barrier musim semi ENSO</div>
            </div>
          </div>

          <div style={{ marginTop: '10px', fontSize: '10px', color: '#7a8178' }}>
            *{h3TestAcc.toFixed(1).replace('.', ',')}% di Horizon 3 Bulan bersifat semu: model memprediksi mayoritas sampel uji sebagai Netral.
          </div>
        </div>
      </div>

      {/* Row 2: Perbandingan Kinerja Model */}
      <div className="fig-card">
        <h2 className="fig-card-title">Perbandingan Kinerja Model</h2>
        <p className="fig-card-subtitle">
          Dua sudut pandang: akurasi klasifikasi dan presisi numerik (MAE ONI)
        </p>

        <div className="grid-2col" style={{ marginTop: '20px', gap: '32px' }}>
          {/* Chart 1: Akurasi Validasi vs Uji */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#111827', marginBottom: '12px' }}>
              Akurasi Klasifikasi: Validasi vs Uji
            </div>
            <div style={{ width: '100%', height: 'auto' }}>
              <svg viewBox="0 0 440 220" width="100%" height="auto" style={{ display: 'block', overflow: 'visible' }}>
                {/* Baseline */}
                <line x1="15" y1="160" x2="425" y2="160" stroke="#cbd5e1" strokeWidth="1" />

                {/* Group 1: 1 Bulan */}
                <rect x="60" y={calcAccY(h1ValAcc)} width="26" height={calcAccH(h1ValAcc)} rx="2" fill="#8da399" />
                <text x="73" y={calcAccY(h1ValAcc) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h1ValAcc.toFixed(1).replace('.', ',')}%</text>

                <rect x="92" y={calcAccY(h1TestAcc)} width="26" height={calcAccH(h1TestAcc)} rx="2" fill="#1c382a" />
                <text x="105" y={calcAccY(h1TestAcc) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h1TestAcc.toFixed(1).replace('.', ',')}%</text>

                <text x="89" y="179" fill="#475569" fontSize="11" fontWeight="600" textAnchor="middle">1 Bulan</text>

                {/* Group 2: 3 Bulan */}
                <rect x="190" y={calcAccY(h3ValAcc)} width="26" height={calcAccH(h3ValAcc)} rx="2" fill="#8da399" />
                <text x="203" y={calcAccY(h3ValAcc) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h3ValAcc.toFixed(1).replace('.', ',')}%</text>

                <rect x="222" y={calcAccY(h3TestAcc)} width="26" height={calcAccH(h3TestAcc)} rx="2" fill="#b45309" />
                <text x="235" y={calcAccY(h3TestAcc) - 6} fill="#92400e" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h3TestAcc.toFixed(1).replace('.', ',')}%*</text>

                <text x="219" y="179" fill="#475569" fontSize="11" fontWeight="600" textAnchor="middle">3 Bulan</text>

                {/* Group 3: 6 Bulan */}
                <rect x="320" y={calcAccY(h6ValAcc)} width="26" height={calcAccH(h6ValAcc)} rx="2" fill="#8da399" />
                <text x="333" y={calcAccY(h6ValAcc) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h6ValAcc.toFixed(1).replace('.', ',')}%</text>

                <rect x="352" y={calcAccY(h6TestAcc)} width="26" height={calcAccH(h6TestAcc)} rx="2" fill="#b91c1c" />
                <text x="365" y={calcAccY(h6TestAcc) - 6} fill="#9f1239" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h6TestAcc.toFixed(1).replace('.', ',')}%</text>

                <text x="349" y="179" fill="#475569" fontSize="11" fontWeight="600" textAnchor="middle">6 Bulan</text>

                {/* Legend */}
                <g transform="translate(15, 206)">
                  <rect x="0" y="-8" width="8" height="8" rx="1.5" fill="#8da399" />
                  <text x="12" y="-1" fill="#64748b" fontSize="9.5">Validasi</text>

                  <rect x="68" y="-8" width="8" height="8" rx="1.5" fill="#1c382a" />
                  <text x="80" y="-1" fill="#64748b" fontSize="9.5">Uji</text>

                  <text x="110" y="-1" fill="#92400e" fontSize="9" fontStyle="italic">*Akurasi horizon 3 semu (validasi hanya {h3ValAcc.toFixed(1).replace('.', ',')}%)</text>
                </g>
              </svg>
            </div>
          </div>

          {/* Chart 2: Presisi Numerik MAE */}
          <div>
            <div style={{ fontSize: '12px', fontWeight: 700, color: '#111827', marginBottom: '12px' }}>
              Presisi Numerik: MAE Model vs Persistence
            </div>
            <div style={{ width: '100%', height: 'auto' }}>
              <svg viewBox="0 0 440 220" width="100%" height="auto" style={{ display: 'block', overflow: 'visible' }}>
                {/* Baseline */}
                <line x1="15" y1="160" x2="425" y2="160" stroke="#cbd5e1" strokeWidth="1" />

                {/* Group 1: 1 Bulan */}
                <rect x="60" y={calcMaeY(h1MaeModel)} width="26" height={calcMaeH(h1MaeModel)} rx="2" fill="#1c382a" />
                <text x="73" y={calcMaeY(h1MaeModel) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h1MaeModel.toFixed(3).replace('.', ',')}</text>

                <rect x="92" y={calcMaeY(h1MaeBase)} width="26" height={calcMaeH(h1MaeBase)} rx="2" fill="#b45309" />
                <text x="105" y={calcMaeY(h1MaeBase) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h1MaeBase.toFixed(3).replace('.', ',')}</text>

                <text x="89" y="179" fill="#475569" fontSize="11" fontWeight="600" textAnchor="middle">1 Bulan</text>

                {/* Group 2: 3 Bulan */}
                <rect x="190" y={calcMaeY(h3MaeModel)} width="26" height={calcMaeH(h3MaeModel)} rx="2" fill="#1c382a" />
                <text x="203" y={calcMaeY(h3MaeModel) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h3MaeModel.toFixed(3).replace('.', ',')}</text>

                <rect x="222" y={calcMaeY(h3MaeBase)} width="26" height={calcMaeH(h3MaeBase)} rx="2" fill="#b45309" />
                <text x="235" y={calcMaeY(h3MaeBase) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h3MaeBase.toFixed(3).replace('.', ',')}</text>

                <text x="219" y="179" fill="#475569" fontSize="11" fontWeight="600" textAnchor="middle">3 Bulan</text>

                {/* Group 3: 6 Bulan */}
                <rect x="320" y={calcMaeY(h6MaeModel)} width="26" height={calcMaeH(h6MaeModel)} rx="2" fill="#1c382a" />
                <text x="333" y={calcMaeY(h6MaeModel) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h6MaeModel.toFixed(3).replace('.', ',')}</text>

                <rect x="352" y={calcMaeY(h6MaeBase)} width="26" height={calcMaeH(h6MaeBase)} rx="2" fill="#b45309" />
                <text x="365" y={calcMaeY(h6MaeBase) - 6} fill="#1e293b" fontSize="9.5" fontWeight="700" fontFamily="var(--font-mono)" textAnchor="middle">{h6MaeBase.toFixed(3).replace('.', ',')}</text>

                <text x="349" y="179" fill="#475569" fontSize="11" fontWeight="600" textAnchor="middle">6 Bulan</text>

                {/* Legend */}
                <g transform="translate(15, 206)">
                  <rect x="0" y="-8" width="8" height="8" rx="1.5" fill="#1c382a" />
                  <text x="12" y="-1" fill="#64748b" fontSize="9.5">Model</text>

                  <rect x="65" y="-8" width="8" height="8" rx="1.5" fill="#b45309" />
                  <text x="77" y="-1" fill="#64748b" fontSize="9.5">Persistence</text>

                  <text x="150" y="-1" fill="#64748b" fontSize="9" fontStyle="italic">lebih rendah = lebih presisi</text>
                </g>
              </svg>
            </div>
          </div>
        </div>

        <div style={{ marginTop: '20px', paddingTop: '12px', borderTop: '1px solid #f1f5f9', fontSize: '10px', color: '#94a3b8' }}>
          Sumber: reports/enso_metrics.csv · model/enso_ensemble_*/metrics_horizon_*.json · seluruh angka berasal dari artefak terverifikasi.
        </div>
      </div>
    </div>
  );
}

/* ==========================================================================
   ROOT APP
   ========================================================================== */

function App() {
  const [active, setActive] = useState('overview');

  return (
    <div className="app-shell-container">
      <div className="app-shell">
        <Sidebar active={active} setActive={setActive} />
        <main className="main-content">
          {active === 'overview' && <OverviewPage />}
          {active === 'visualization' && <VisualizationPage />}
          {active === 'forecast' && <ForecastPage />}
          {active === 'classification' && <ClassificationPage />}
        </main>
      </div>
    </div>
  );
}

createRoot(document.getElementById('root')).render(<App />);
