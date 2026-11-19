import React, { useMemo, useState } from 'react';
import { createRoot } from 'react-dom/client';
import { evaluation, forecastSeries, latest, oniArchive, splitMeta, sstDomains } from './data';
import './styles.css';

const fmt = (value, digits = 2) => new Intl.NumberFormat('id-ID', { minimumFractionDigits: digits, maximumFractionDigits: digits }).format(value);
const signed = (value, digits = 2) => `${value >= 0 ? '+' : '−'}${fmt(Math.abs(value), digits)}`;

function BrandMark() {
  return <div className="brand-mark" aria-hidden="true"><span></span><span></span><span></span></div>;
}

function Icon({ name }) {
  const paths = {
    grid: <><rect x="3" y="3" width="7" height="7" rx="1"/><rect x="14" y="3" width="7" height="7" rx="1"/><rect x="3" y="14" width="7" height="7" rx="1"/><rect x="14" y="14" width="7" height="7" rx="1"/></>,
    chart: <><path d="M4 19V5"/><path d="M4 19h17"/><path d="m7 15 4-5 3 2 5-7"/></>,
    history: <><path d="M3 12a9 9 0 1 0 3-6.7"/><path d="M3 4v5h5"/><path d="M12 7v5l3 2"/></>,
    info: <><circle cx="12" cy="12" r="9"/><path d="M12 11v5"/><path d="M12 8h.01"/></>,
    arrow: <><path d="M5 12h14"/><path d="m13 6 6 6-6 6"/></>,
    external: <><path d="M14 3h7v7"/><path d="m21 3-9 9"/><path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"/></>,
    wave: <path d="M3 12c2.2-7 4.8 7 7 0s4.8-7 7 0 4.8 7 7 0"/>
  };
  return <svg viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.8" strokeLinecap="round" strokeLinejoin="round" aria-hidden="true">{paths[name]}</svg>;
}

function Sidebar({ active, setActive }) {
  const items = [
    ['overview', 'Ikhtisar', 'grid'],
    ['evaluation', 'Evaluasi model', 'chart'],
    ['archive', 'Arsip ONI', 'history'],
    ['method', 'Panduan baca', 'info']
  ];
  return <aside className="sidebar">
    <div className="brand"><BrandMark /><div><div className="brand-name">Lautan<span>.id</span></div><div className="brand-sub">MARITIME INTELLIGENCE</div></div></div>
    <div className="sidebar-rule"></div>
    <p className="nav-label">NAVIGASI</p>
    <nav aria-label="Navigasi dashboard">
      {items.map(([id, label, icon]) => <button key={id} className={`nav-item ${active === id ? 'active' : ''}`} onClick={() => { setActive(id); document.getElementById(id)?.scrollIntoView({ behavior: 'smooth', block: 'start' }); }}><Icon name={icon} /><span>{label}</span>{active === id && <i />}</button>)}
    </nav>
  </aside>;
}

function Topbar({ onAbout }) {
  return <header className="topbar"><div className="crumb"><span>Dashboard</span><b>/</b><strong>Kondisi terbaru</strong></div><div className="top-actions"><div className="status-pill"><span></span> DATA HISTORIS</div><button className="about-btn" onClick={onAbout}><Icon name="info" /> Tentang data</button></div></header>;
}

function StatCard({ label, value, unit, meta, accent, icon }) {
  return <article className={`stat-card ${accent || ''}`}><div className="stat-top"><span>{label}</span><span className="stat-icon"><Icon name={icon || 'wave'} /></span></div><div className="stat-value mono">{value}<em>{unit}</em></div><div className="stat-meta">{meta}</div></article>;
}

function PhaseCard() {
  return <article className="phase-card"><div className="phase-top"><div><p className="eyebrow">KONDISI TERKINI</p><h2>Fase ENSO</h2></div><span className="neutral-chip">● NETRAL</span></div><div className="phase-main"><div className="phase-orbit"><div className="orbit-ring"></div><div className="orbit-dot"></div><span>ONI</span></div><div><div className="phase-title">{latest.phase}</div><p>{latest.note}</p></div></div><div className="phase-scale"><div className="scale-track"><span className="scale-marker" style={{ left: `${((latest.oni + 2) / 4) * 100}%` }}></span></div><div><span>La Niña</span><span>Netral</span><span>El Niño</span></div></div></article>;
}

function SstPanel() {
  const available = sstDomains.filter(d => d.value !== null);
  const max = Math.max(...available.map(d => Math.abs(d.value)), 1);
  return <section className="panel sst-panel" id="domains"><div className="panel-heading"><div><p className="eyebrow">LAUT INDONESIA</p><h2>Anomali SST regional</h2></div><span className="unit-tag">°C · terhadap normal bulanan</span></div><div className="sst-grid">{sstDomains.map((domain) => <div className="sst-row" key={domain.name}><div className="sst-label"><strong>{domain.name}</strong><small>{domain.role}</small></div><div className={`sst-bar-wrap ${domain.value === null ? 'unavailable-track' : ''}`}>{domain.value !== null && <div className={`sst-bar ${domain.value >= 0 ? 'warm' : 'cool'}`} style={{ width: `${Math.max(9, Math.abs(domain.value) / max * 100)}%` }}></div>}<span className="zero-line"></span></div><div className={`sst-value mono ${domain.value === null ? 'unavailable-text' : domain.value >= 0 ? 'warm-text' : 'cool-text'}`}>{domain.value === null ? '—' : signed(domain.value, 3)}</div><div className="sst-status">{domain.status}</div></div>)}</div><div className="panel-footnote"><span className="legend-dot cool-dot"></span> lebih dingin <span className="legend-dot warm-dot"></span> lebih hangat <span className="footnote-sep">|</span> Anomali, bukan suhu absolut</div></section>;
}

function ArchiveChart() {
  const width = 900, height = 260, padX = 22, padY = 20, min = -1.5, max = 2.8;
  const x = (i) => padX + i * ((width - padX * 2) / Math.max(oniArchive.length - 1, 1));
  const y = (v) => height - padY - ((v - min) / (max - min)) * (height - padY * 2);
  const points = oniArchive.map((d, i) => `${x(i)},${y(d.value)}`).join(' ');
  const area = oniArchive.length ? `${padX},${y(0)} ${points} ${x(oniArchive.length - 1)},${y(0)}` : '';
  return <section className="panel archive-panel" id="archive"><div className="panel-heading"><div><p className="eyebrow">ARSIP INDEKS</p><h2>ONI historis</h2></div><div className="archive-range">Jan 2016 <span>→</span> Jun 2025</div></div><div className="chart-legend"><span><i className="legend-block train"></i> Train · 72 bulan</span><span><i className="legend-block val"></i> Validasi · 24 bulan</span><span><i className="legend-block test"></i> Uji · 18 bulan</span></div><div className="line-chart"><div className="y-labels"><span>+2,0</span><span>+1,0</span><span>0</span><span>−1,0</span></div><svg viewBox={`0 0 ${width} ${height}`} role="img" aria-label="Grafik ONI historis Januari 2016 hingga Juni 2025"><defs><linearGradient id="oniFill" x1="0" x2="0" y1="0" y2="1"><stop offset="0" stopColor="#00a3c4" stopOpacity=".28"/><stop offset="1" stopColor="#00a3c4" stopOpacity="0"/></linearGradient></defs><line x1="0" x2={width} y1={y(0)} y2={y(0)} className="zero-axis"/><line x1="0" x2={width} y1={y(1)} y2={y(1)} className="grid-axis"/><line x1="0" x2={width} y1={y(-1)} y2={y(-1)} className="grid-axis"/>{oniArchive.length ? <><polygon points={area} fill="url(#oniFill)"/><polyline points={points} className="oni-line"/><circle cx={x(oniArchive.length - 1)} cy={y(oniArchive[oniArchive.length - 1].value)} r="5" className="last-point"/></> : <text x={width / 2} y={y(0) - 8} textAnchor="middle" className="chart-empty">Seri arsip tidak tersedia di lampiran</text>}</svg><div className="x-labels"><span>2016</span><span>2018</span><span>2020</span><span>2022</span><span>2024</span><span>2025</span></div></div><div className="archive-callout"><span className="callout-mark">↗</span><div><strong>Terakhir: {latest.date}</strong><p>ONI {signed(latest.oni)} °C · Fase Netral</p></div><span className="callout-note">Seri bulanan lengkap dihitung dari dataset historis 2016–2025.</span></div></section>;
}

function ForecastPanel() {
  const [horizon, setHorizon] = useState(1);
  const [hover, setHover] = useState(null);
  const series = forecastSeries[horizon] || [];
  const verdict = evaluation[horizon];
  const width = 920, height = 270, padX = 40, padY = 24, min = -1.2, max = 0.6;
  const x = (i) => padX + i * ((width - padX * 2) / Math.max(series.length - 1, 1));
  const y = (v) => height - padY - ((v - min) / (max - min)) * (height - padY * 2);

  // Indeks batas observasi (06/25) adalah 3
  const splitIdx = 3;
  const splitX = x(splitIdx);

  const actualPoints = series
    .filter(d => d.actual !== null && d.actual !== undefined)
    .map(d => `${x(series.indexOf(d))},${y(d.actual)}`)
    .join(' ');

  const predictedPoints = series
    .filter(d => d.prediction !== null && d.prediction !== undefined)
    .map(d => `${x(series.indexOf(d))},${y(d.prediction)}`)
    .join(' ');

  const bands = [
    { label: 'El Niño (≥ +0,5)', from: 0.5, to: max, tone: 'elnino' },
    { label: 'Netral (−0,5 s.d. +0,5)', from: -0.5, to: 0.5, tone: 'neutral' },
    { label: 'La Niña (≤ −0,5)', from: min, to: -0.5, tone: 'lanina' }
  ];

  const tooltipStyle = hover ? { left: `${Math.min(78, Math.max(4, (hover.x / width) * 100))}%`, top: `${Math.max(4, (hover.y / height) * 100 - 18)}%` } : {};

  return (
    <section className="panel forecast-panel" id="forecast">
      <div className="panel-heading forecast-heading">
        <div>
          <p className="eyebrow">PRAKIRAAN TIME SERIES</p>
          <h2>ONI aktual vs proyeksi model</h2>
          <p className="panel-subtitle">
            Garis biru adalah observasi aktual. Garis putus-putus merah-coral adalah proyeksi model untuk {horizon} bulan ke depan.
          </p>
        </div>
        <div className="forecast-controls">
          <div className="horizon-tabs" role="tablist" aria-label="Pilih horizon chart time series">
            {[1, 3, 6].map(h => (
              <button
                key={h}
                onClick={() => { setHorizon(h); setHover(null); }}
                className={horizon === h ? 'selected' : ''}
                role="tab"
                aria-selected={horizon === h}
              >
                {h} bulan
              </button>
            ))}
          </div>
          <span className={`reliability-badge ${verdict.tone}`}>
            <i />{verdict.verdict}
          </span>
        </div>
      </div>

      <div className="forecast-legend">
        <span><i className="line-key actual-key"></i> Aktual observasi</span>
        <span><i className="line-key prediction-key"></i> Proyeksi model ({horizon} bln ke depan)</span>
        <span><i className="window-key"></i> Jendela proyeksi target</span>
      </div>

      <div className="forecast-chart-wrap">
        <div className="forecast-y-labels">
          <span>+0,5</span>
          <span>0</span>
          <span>−0,5</span>
          <span>−1,0</span>
        </div>

        <svg className="forecast-chart" viewBox={`0 0 ${width} ${height}`} role="img" aria-label={`Prakiraan ONI aktual dan proyeksi horizon ${horizon} bulan`}>
          {/* Zona proyeksi */}
          <rect x={splitX} y="0" width={width - splitX} height={height} className="test-window" />

          {/* Ambang batas ENSO */}
          {bands.map(b => (
            <g key={b.label}>
              <rect x="0" y={y(b.to)} width={width} height={y(b.from) - y(b.to)} className={`phase-band ${b.tone}`} />
              <text x={width - 8} y={y((b.from + b.to) / 2) + 3} textAnchor="end" className="phase-label">{b.label}</text>
            </g>
          ))}

          <line x1="0" x2={width} y1={y(0)} y2={y(0)} className="forecast-zero" />
          <line x1="0" x2={width} y1={y(0.5)} y2={y(0.5)} className="forecast-grid" strokeDasharray="3 3" />
          <line x1="0" x2={width} y1={y(-0.5)} y2={y(-0.5)} className="forecast-grid" strokeDasharray="3 3" />

          {/* Batas observasi */}
          <line x1={splitX} x2={splitX} y1="0" y2={height} className="test-divider" />
          <text x={splitX - 6} y="16" textAnchor="end" fill="#64748b" fontSize="10" fontFamily="var(--mono)">Batas Observasi (06/25)</text>
          <text x={splitX + 8} y="16" textAnchor="start" fill="#e87561" fontSize="10" fontWeight="600" fontFamily="var(--mono)">Proyeksi {horizon} Bulan →</text>

          {/* Garis aktual */}
          <polyline points={actualPoints} className="forecast-actual-line" />

          {/* Garis prediksi */}
          <polyline points={predictedPoints} className="forecast-prediction-line" />

          {/* Titik-titik dan interaksi */}
          {series.map((d, i) => {
            const posX = x(i);
            const posY = y(d.prediction ?? d.actual);
            return (
              <g
                key={`${d.date}-${i}`}
                onMouseEnter={() => setHover({ ...d, x: posX, y: posY })}
                onMouseLeave={() => setHover(null)}
              >
                <circle
                  cx={posX}
                  cy={y(d.actual)}
                  r="5"
                  className="forecast-hit"
                  tabIndex="0"
                />
                {d.isPrediction && (
                  <circle
                    cx={posX}
                    cy={y(d.prediction)}
                    r="5"
                    fill="#e87561"
                    stroke="#fff"
                    strokeWidth="2"
                  />
                )}
                {/* Nilai numerik di atas titik proyeksi */}
                {d.isPrediction && (
                  <text
                    x={posX}
                    y={y(d.prediction) - 10}
                    textAnchor="middle"
                    fill="#e87561"
                    fontSize="11"
                    fontWeight="700"
                    fontFamily="var(--mono)"
                  >
                    {d.prediction.toFixed(2).replace('.', ',')}
                  </text>
                )}
              </g>
            );
          })}
        </svg>

        {hover && (
          <div className="forecast-tooltip" style={tooltipStyle}>
            <strong>Bulan: {hover.date}</strong>
            <span>Aktual: <b>{hover.actual !== null ? `${signed(hover.actual)} °C` : '—'}</b></span>
            {hover.prediction !== null && (
              <span>Prediksi: <b>{signed(hover.prediction)} °C</b></span>
            )}
          </div>
        )}

        {/* Dynamic X labels */}
        <div
          className="forecast-x-labels"
          style={{
            display: 'flex',
            justifyContent: 'space-between',
            paddingLeft: `${padX}px`,
            paddingRight: `${padX}px`,
            position: 'absolute',
            bottom: '6px',
            left: 0,
            right: 0
          }}
        >
          {series.map((d) => (
            <span
              key={d.date}
              style={{
                fontFamily: 'var(--mono)',
                fontSize: '10px',
                fontWeight: d.isPrediction ? 700 : 500,
                color: d.isPrediction ? '#e87561' : '#64748b'
              }}
            >
              {d.date}
            </span>
          ))}
        </div>
      </div>

      <div className="forecast-footnote">
        <span>ⓘ</span>
        <p>
          Batas observasi data historis adalah <strong>Juni 2025</strong>. Pilihan tab horizon (1, 3, 6 bulan) menampilkan lintasan peramalan model ke depan dari batas observasi tersebut.
        </p>
      </div>
    </section>
  );
}

function Matrix({ matrix }) {
  const labels = ['La Niña', 'Netral', 'El Niño'];
  return <div className="matrix-wrap"><div className="matrix-y-label">AKTUAL</div><div className="matrix-content"><div className="matrix-pred">PREDIKSI</div><div className="matrix-table"><div className="matrix-corner"></div>{labels.map(l => <div className="matrix-head" key={`h-${l}`}>{l}</div>)}{matrix.map((row, i) => <React.Fragment key={labels[i]}><div className="matrix-row-label">{labels[i]}</div>{row.map((n, j) => <div className={`matrix-cell ${n > 0 ? (i === j ? 'correct' : 'incorrect') : ''}`} key={`${i}-${j}`}>{n}</div>)}</React.Fragment>)}</div></div></div>;
}

function EvaluationPanel() {
  const [horizon, setHorizon] = useState(1);
  const item = evaluation[horizon];
  const metrics = [
    ['Akurasi uji', `${fmt(item.accuracy.test, 1)}%`, item.tone],
    ['RMSE LSTM', `${fmt(item.rmse.test, 3)} °C`, 'neutral'],
    ['MAE model', fmt(item.maeModel, 3), 'neutral'],
    ['MAE persistence', fmt(item.maeBaseline, 3), item.maeBaseline < item.maeModel ? 'bad' : 'good']
  ];
  return <section className="panel eval-panel" id="evaluation"><div className="panel-heading eval-heading"><div><p className="eyebrow">BUKTI MODEL</p><h2>Evaluasi prakiraan ENSO</h2></div><div className="horizon-tabs" role="tablist" aria-label="Pilih horizon prakiraan">{[1, 3, 6].map(h => <button key={h} onClick={() => setHorizon(h)} className={horizon === h ? 'selected' : ''} role="tab" aria-selected={horizon === h}>{h} bln</button>)}</div></div><div className={`verdict-banner ${item.tone}`}><span className="verdict-icon">{item.tone === 'good' ? '✓' : item.tone === 'warn' ? '!' : '×'}</span><div><strong>Horizon {item.label}: {item.verdict}</strong><p>{horizon === 1 ? 'Satu-satunya horizon dengan sinyal yang relatif dapat dipertimbangkan — tetap kalah dari persistence.' : horizon === 3 ? 'Akurasi 100% terlihat tinggi, tetapi seluruh data uji adalah kelas Netral sehingga metrik ini menyesatkan.' : 'Model selalu memilih satu kelas pada evaluasi; jangan gunakan sebagai dasar prakiraan.'}</p></div><span className="artifact-tag">ARTIFACT VERIFIED</span></div><div className="metrics-strip">{metrics.map(([label, value, tone]) => <div className="metric" key={label}><span>{label}</span><strong className={`mono ${tone}`}>{value}</strong></div>)}</div><div className="eval-detail"><div className="matrix-card"><div className="subheading"><h3>Confusion matrix · uji</h3><span>n = 7</span></div><Matrix matrix={item.matrix} /><p className="matrix-note">{item.matrixNote}</p></div><div className="baseline-card"><div className="subheading"><h3>Model vs persistence</h3><span>MAE ONI · lebih kecil lebih baik</span></div><div className="compare-bars"><div className="compare-row"><span>Ensemble</span><div><i style={{ width: `${item.maeModel / .22 * 100}%` }}></i></div><strong className="mono">{fmt(item.maeModel, 3)}</strong></div><div className="compare-row baseline"><span>Persistence</span><div><i style={{ width: `${item.maeBaseline / .22 * 100}%` }}></i></div><strong className="mono">{fmt(item.maeBaseline, 3)}</strong></div></div><div className="baseline-callout"><span>↘</span><p>Persistence mengungguli model pada horizon ini.</p></div><div className="validation-mini"><div><span>Validasi</span><strong className="mono">{fmt(item.accuracy.val, 1)}% akurasi</strong></div><div><span>RMSE LSTM</span><strong className="mono">{fmt(item.rmse.val, 3)} °C</strong></div></div></div></div></section>;
}

function MethodPanel() {
  return <section className="method-section" id="method"><div className="method-intro"><p className="eyebrow">PANDUAN MEMBACA</p><h2>Mulai dari sinyal,<br /><em>bukan angka.</em></h2><p>Gunakan ONI untuk membaca fase ENSO, lalu lihat SOI, DMI, dan anomali SST untuk memahami konteks atmosfer serta respons laut di wilayah Indonesia.</p><a href="#limitations" className="text-link">Lihat batas penggunaan <Icon name="arrow" /></a></div><div className="method-card insight-card"><div className="insight-row"><span className="insight-icon">01</span><div><strong>Fase ENSO</strong><small>ONI −0,5 hingga +0,5 berarti Netral. Jangan membaca satu indikator secara terpisah.</small></div></div><div className="insight-row"><span className="insight-icon">02</span><div><strong>SST regional</strong><small>Anomali menunjukkan lebih hangat atau dingin dibanding normal bulan yang sama, bukan suhu absolut.</small></div></div><div className="insight-row"><span className="insight-icon">03</span><div><strong>Prakiraan model</strong><small>Horizon 1 bulan paling layak dipertimbangkan; horizon 3 dan 6 bulan perlu kehati-hatian tinggi.</small></div></div></div></section>;
}

function Limitations({ onClose }) {
  return <div className="modal-backdrop" onClick={onClose}><div className="modal" onClick={e => e.stopPropagation()} role="dialog" aria-modal="true" aria-labelledby="modal-title"><button className="close-btn" onClick={onClose} aria-label="Tutup">×</button><p className="eyebrow">TENTANG DATA</p><h2 id="modal-title">Batas yang perlu<br /><em>diingat.</em></h2><div className="limit-list"><div><span>01</span><p><strong>Bukan realtime</strong>Data terakhir adalah Juni 2025. Tidak ada feed NOAA langsung.</p></div><div><span>02</span><p><strong>Baseline lebih kuat</strong>Persistence mengalahkan model pada semua horizon berdasarkan MAE.</p></div><div><span>03</span><p><strong>Horizon panjang lemah</strong>Horizon 3 bulan bersifat trivial majority class; horizon 6 bulan gagal total.</p></div><div><span>04</span><p><strong>Proxy terbatas</strong>MHW mayoritas nol/konstan dan curah hujan hanya proxy, bukan observasi regional Indonesia.</p></div></div><div className="modal-source">Sumber upstream: NOAA OISST v2.1 · CPC ONI · PSL SOI & DMI</div></div></div>;
}

function App() {
  const [active, setActive] = useState('overview');
  const [aboutOpen, setAboutOpen] = useState(false);
  const activeDate = useMemo(() => latest.date, []);
  return <div className="app-shell"><Sidebar active={active} setActive={setActive} /><main className="main"><Topbar onAbout={() => setAboutOpen(true)} /><div className="content"><section className="hero" id="overview"><div><div className="live-line"><span className="pulse"></span> SNAPSHOT DATASET · {activeDate.toUpperCase()}</div><h1>Pantau iklim &<br /><em>dinamika laut</em> Indonesia.</h1><p className="hero-copy">Sinyal ENSO terkini, anomali laut regional, dan bukti performa model — dalam satu ruang pantau yang jujur.</p></div><div className="hero-stamp"><span>PEMBARUAN TERAKHIR</span><strong>{activeDate}</strong><small>114 baris data bulanan</small></div></section><section className="latest-grid"><PhaseCard /><div className="stat-stack"><StatCard label="ONI" value={signed(latest.oni)} unit="°C" meta="Indeks Niño 3.4 · anomali" accent="primary" icon="wave" /><StatCard label="SOI" value={signed(latest.soi, 3)} unit="" meta="Southern Oscillation Index" icon="chart" /><StatCard label="DMI" value={signed(latest.dmi, 3)} unit="°C" meta="Dipole Mode Index" accent="coral" icon="wave" /></div></section><SstPanel /><ArchiveChart /><ForecastPanel /><EvaluationPanel /><MethodPanel /><section className="limitations" id="limitations"><div><p className="eyebrow">CATATAN PENTING</p><h2>Gunakan sebagai<br /><em>bukti, bukan janji.</em></h2></div><div className="limitation-grid"><div><span>↳</span><p>Data historis hingga <strong>Juni 2025</strong>, bukan kondisi hari ini.</p></div><div><span>↳</span><p>Model belum disajikan sebagai <strong>inferensi live</strong>.</p></div><div><span>↳</span><p>Peringatan iklim resmi tetap wewenang <strong>BMKG</strong>.</p></div></div></section><footer><span>© 2025 LAUTAN.ID</span><span>PROYEK SISTEM CERDAS · SEMESTER 5</span><span>Data bersumber dari NOAA · Dataset lokal</span></footer></div></main>{aboutOpen && <Limitations onClose={() => setAboutOpen(false)} />}</div>;
}

createRoot(document.getElementById('root')).render(<App />);
