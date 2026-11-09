import React from 'react';
import { currentClimateState } from '../data/climateData';

export default function PrakiraanENSO({ selectedLead, setSelectedLead, isAnalystMode }) {
  const leads = ['1 bulan', '3 bulan', '6 bulan'];

  return (
    <div className="forecast-page">
      {/* 1. Pengantar & Selector Lead Time */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">
              Probabilitas Fase ENSO Berdasarkan Horizon Waktu
            </h2>
            <p className="chart-subtitle">
              Prakiraan 100% stacked bar menunjukkan pergeseran peluang fase El Niño, Netral, dan La Niña seiring bertambahnya horizon prakiraan.
            </p>
          </div>

          <div className="chart-tag-group">
            <span className="dummy-tag">Simulasi Model</span>
            <span className="dataset-label">KMRV Ensemble v2.1</span>
          </div>
        </div>

        {/* 100% Horizontal Stacked Bar per Lead Time */}
        <div className="lead-stacked-container">
          {leads.map((leadKey) => {
            const data = currentClimateState.leadTimes[leadKey];
            const isSelected = selectedLead === leadKey;

            return (
              <div
                key={leadKey}
                className={`lead-stacked-row ${isSelected ? 'is-active-lead' : ''}`}
                onClick={() => setSelectedLead(leadKey)}
                role="button"
                tabIndex={0}
                aria-pressed={isSelected}
                onKeyDown={(e) => { if (e.key === 'Enter' || e.key === ' ') setSelectedLead(leadKey); }}
              >
                <div className="lead-row-meta">
                  <strong className="lead-row-title">{data.label}</strong>
                  <span className="lead-row-target">{data.targetMonth}</span>
                  <span className="lead-row-val">{data.roniForecast} ({data.uncertaintyBand})</span>
                </div>

                <div className="lead-stacked-track" role="img" aria-label={`${data.label}: El Nino ${data.elNinoProb}%, Netral ${data.neutralProb}%, La Nina ${data.laNinaProb}%`}>
                  <div
                    className="stacked-seg seg-elnino"
                    style={{ width: `${data.elNinoProb}%` }}
                  >
                    <span>{data.elNinoProb}%</span>
                  </div>
                  <div
                    className="stacked-seg seg-neutral"
                    style={{ width: `${data.neutralProb}%` }}
                  >
                    <span>{data.neutralProb}%</span>
                  </div>
                  <div
                    className="stacked-seg seg-lanina"
                    style={{ width: `${data.laNinaProb}%` }}
                  >
                    <span>{data.laNinaProb}%</span>
                  </div>
                </div>

                <div className="lead-row-action">
                  <span className={`lead-status-pill ${isSelected ? 'pill-selected' : ''}`}>
                    {isSelected ? 'Terpilih' : 'Pilih'}
                  </span>
                </div>
              </div>
            );
          })}
        </div>

        <div className="stacked-legend" style={{ marginTop: 'var(--space-md)' }}>
          <span className="legend-chip legend-chip-elnino">Oranye: El Niño (RONI &gt; +0,5 °C)</span>
          <span className="legend-chip legend-chip-neutral">Abu-abu: Fase Netral (-0,5 s.d. +0,5 °C)</span>
          <span className="legend-chip legend-chip-lanina">Biru: La Niña (RONI &lt; -0,5 °C)</span>
        </div>
      </section>

      {/* 2. Plume Prakiraan Ensemble KMRV vs Konsensus IRI */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">
              Lintasan Ensemble KMRV Menunjukkan Ketahanan Fase Hangat Hingga Kuartal II 2027
            </h3>
            <p className="chart-subtitle">
              Plume ensemble memetakan 20 lintasan simulasi kondisi awal laut-atmosfer untuk mengukur dispersi ketidakpastian.
            </p>
          </div>
          <span className="dummy-tag">Data contoh</span>
        </div>

        <div className="plume-chart-wrap">
          <svg
            width="100%"
            height="200"
            viewBox="0 0 600 200"
            fill="none"
            className="plume-svg"
            role="img"
            aria-label="Plume ensemble KMRV multi-member"
          >
            {/* Garis Ambang Operasional */}
            <line x1="40" y1="60" x2="560" y2="60" stroke="var(--color-elnino)" strokeWidth="1" strokeDasharray="4 4" />
            <text x="45" y="52" fill="var(--color-elnino)" fontSize="12" fontFamily="var(--font-outlier)">+0,5 °C Ambang El Niño</text>

            <line x1="40" y1="105" x2="560" y2="105" stroke="var(--color-rule-2)" strokeWidth="1" />
            <text x="45" y="100" fill="var(--color-muted)" fontSize="12" fontFamily="var(--font-outlier)">0,0 °C Netral</text>

            <line x1="40" y1="150" x2="560" y2="150" stroke="var(--color-lanina)" strokeWidth="1" strokeDasharray="4 4" />
            <text x="45" y="162" fill="var(--color-lanina)" fontSize="12" fontFamily="var(--font-outlier)">-0,5 °C Ambang La Niña</text>

            {/* Garis observasi masa lalu */}
            <path d="M40 120 L 100 115 L 160 100 L 220 85" stroke="var(--color-ink)" strokeWidth="2.5" fill="none" />
            <circle cx="220" cy="85" r="4" fill="var(--color-ink)" />
            <text x="210" y="74" fill="var(--color-ink)" fontSize="12" fontFamily="var(--font-body)" fontWeight="600">Saat Ini (+0,62 °C)</text>

            {/* Lintasan ensemble individual (dispersi abu-abu tipis) */}
            <path d="M220 85 Q 340 70 540 45" stroke="var(--color-brand)" strokeWidth="1" opacity="0.3" fill="none" />
            <path d="M220 85 Q 330 80 540 60" stroke="var(--color-brand)" strokeWidth="1" opacity="0.3" fill="none" />
            <path d="M220 85 Q 350 60 540 30" stroke="var(--color-brand)" strokeWidth="1" opacity="0.3" fill="none" />
            <path d="M220 85 Q 320 90 540 75" stroke="var(--color-brand)" strokeWidth="1" opacity="0.3" fill="none" />
            <path d="M220 85 Q 360 75 540 50" stroke="var(--color-brand)" strokeWidth="1" opacity="0.3" fill="none" />

            {/* Rata-rata Ensemble KMRV (Garis Biru Tebal) */}
            <path d="M220 85 Q 340 65 540 48" stroke="var(--color-brand)" strokeWidth="3" fill="none" />
            <circle cx="540" cy="48" r="5" fill="var(--color-brand)" />
            <text x="470" y="40" fill="var(--color-brand)" fontSize="12" fontWeight="600" fontFamily="var(--font-body)">
              Rata-rata KMRV (+1,20 °C)
            </text>

            {/* Rata-rata Konsensus IRI/CPC (Garis Putus Oranye) */}
            <path d="M220 85 Q 350 75 540 62" stroke="var(--color-elnino)" strokeWidth="2" strokeDasharray="4 4" fill="none" />
            <text x="470" y="76" fill="var(--color-elnino)" fontSize="12" fontFamily="var(--font-body)">
              Konsensus IRI (+0,95 °C)
            </text>
          </svg>
        </div>

        <p className="chart-footer-note">
          Catatan: Plume menampilkan ketidakpastian kondisi awal. Spring Predictability Barrier (antara Maret–Mei)
          secara alamiah meningkatkan dispersi ensemble pada prakiraan jarak jauh.
        </p>
      </section>

      {/* 3. Dua Kolom: Evaluasi Baseline vs Konteks Atmosfer-Laut (SOI & DMI) */}
      <div className="grid-2col">
        {/* Kolom A: Pembanding Performa Model vs Baseline */}
        <section className="kpi-card">
          <div className="kpi-card-header">
            <h3 className="kpi-card-title">Perbandingan Akurasi (MAE °C)</h3>
            <span className="dataset-label">Lead {selectedLead}</span>
          </div>

          <p className="kpi-context-note">
            Model KMRV dibandingkan terhadap dua model acuan standar meteorologi: Persistensi (asumsi kondisi tidak berubah) dan Klimatologi (rata-rata jangka panjang).
          </p>

          <div className="benchmark-bar-group">
            <div className="benchmark-item">
              <div className="benchmark-label-row">
                <span className="benchmark-model-name is-best">Model KMRV (Deep Learning)</span>
                <strong className="benchmark-num">{currentClimateState.leadTimes[selectedLead].kmrvMae} °C</strong>
              </div>
              <div className="benchmark-bar-track">
                <div
                  className="benchmark-bar-fill fill-kmrv"
                  style={{ width: `${(currentClimateState.leadTimes[selectedLead].kmrvMae / 1.0) * 100}%` }}
                />
              </div>
            </div>

            <div className="benchmark-item">
              <div className="benchmark-label-row">
                <span className="benchmark-model-name">Persistensi (Baseline 1)</span>
                <strong className="benchmark-num">{currentClimateState.leadTimes[selectedLead].persMae} °C</strong>
              </div>
              <div className="benchmark-bar-track">
                <div
                  className="benchmark-bar-fill fill-baseline"
                  style={{ width: `${(currentClimateState.leadTimes[selectedLead].persMae / 1.0) * 100}%` }}
                />
              </div>
            </div>

            <div className="benchmark-item">
              <div className="benchmark-label-row">
                <span className="benchmark-model-name">Klimatologi (Baseline 2)</span>
                <strong className="benchmark-num">{currentClimateState.leadTimes[selectedLead].klimMae} °C</strong>
              </div>
              <div className="benchmark-bar-track">
                <div
                  className="benchmark-bar-fill fill-baseline"
                  style={{ width: `${(currentClimateState.leadTimes[selectedLead].klimMae / 1.0) * 100}%` }}
                />
              </div>
            </div>
          </div>

          <div className="metric-callout-footer">
            <span>KMRV lebih presisi sekitar 24% dibanding model persistensi pada horizon ini.</span>
          </div>
        </section>

        {/* Kolom B: Konteks Atmosfer & Samudra Hindia (SOI & DMI) */}
        <section className="kpi-card">
          <div className="kpi-card-header">
            <h3 className="kpi-card-title">Konteks Dinamika Atmosfer & IOD</h3>
            <span className="dataset-label">BOM & JAMSTEC</span>
          </div>

          <div className="index-comparison-item">
            <div className="index-comp-head">
              <strong>Southern Oscillation Index (SOI)</strong>
              <span className="index-val-chip">{currentClimateState.soiValue}</span>
            </div>
            <p className="index-comp-desc">
              Nilai SOI negatif di bawah -7,0 mengonfirmasi melemahnya sirkulasi pasat ekuator di Samudra Pasifik,
              menandakan kopling antara laut dan atmosfer sudah terbentuk nyata.
            </p>
          </div>

          <div className="index-comparison-item">
            <div className="index-comp-head">
              <strong>Dipole Mode Index (DMI / IOD)</strong>
              <span className="index-val-chip">+{currentClimateState.dmiValue} °C</span>
            </div>
            <p className="index-comp-desc">
              Samudra Hindia berada dalam fase Netral (-0,4 s.d. +0,4 °C). Tidak ada amplifikasi ganda dari IOD Positif saat ini,
              sehingga anomali cuaca Indonesia murni dikontrol oleh sinyal pasifik.
            </p>
          </div>
        </section>
      </div>
    </div>
  );
}
