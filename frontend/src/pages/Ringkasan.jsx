import React from 'react';
import RoniTraceChart from '../components/RoniTraceChart';
import {
  currentClimateState,
  regionalOceanData,
  regionalRainfallMatrix
} from '../data/climateData';

export default function Ringkasan({
  selectedRegion,
  setSelectedRegion,
  selectedLead,
  isAnalystMode,
  onNavigateTab
}) {
  const currentLeadData =
    currentClimateState.leadTimes[selectedLead] ||
    currentClimateState.leadTimes['3 bulan'];

  // Wilayah terpilih
  const currentRegionData =
    regionalOceanData.find((r) => r.name === selectedRegion) ||
    regionalOceanData[1]; // default Selat Makassar

  return (
    <div className="overview-page">
      {/* 1. Hero Status ENSO: Simple Large Text + Kejujuran Data */}
      <section className="hero-status-card" aria-labelledby="enso-hero-title">
        <div className="hero-status-top">
          <div className="hero-status-label-group">
            <h2 id="enso-hero-title" className="hero-enso-state">
              Fase {currentClimateState.roniStatus}
            </h2>
          </div>

          <div className="hero-metric-pill">
            <span className="hero-metric-label">Indeks RONI Terbaru</span>
            <strong className="hero-metric-number">
              {currentClimateState.roniLatest > 0 ? '+' : ''}
              {currentClimateState.roniLatest} °C
            </strong>
            <span className="hero-metric-sub">Rata-rata 3 bulan Niño 3.4</span>
          </div>
        </div>

        {/* 1 Kalimat arti dalam bahasa awam */}
        <p className="hero-laymen-explanation">
          Laut Pasifik tengah saat ini sedikit lebih hangat dari normal (+0,62 °C).
          Pengaruhnya ke curah hujan di Indonesia berbeda tiap wilayah dan musim;
          sebagian wilayah selatan (Jawa, Bali, Nusa Tenggara) berpotensi mengalami musim kemarau lebih kering.
        </p>

        <div className="roni-gauge" aria-hidden="true">
          <div className="roni-gauge-track">
            <span className="roni-zone is-cool" />
            <span className="roni-zone is-neutral" />
            <span className="roni-zone is-warm" />
            <span
              className="roni-gauge-marker"
              style={{ left: `${((currentClimateState.roniLatest + 1) / 3) * 100}%` }}
            />
          </div>
          <div className="roni-gauge-labels">
            <span>-1,0</span>
            <span>-0,5</span>
            <span>0</span>
            <span>+0,5</span>
            <span>+2,0</span>
          </div>
        </div>

        {/* Mode Analis: Detail angka eksak & metrik pendukung */}
        {isAnalystMode && (
          <div className="analyst-meta-drawer" role="region" aria-label="Metrik teknis instansi">
            <div className="analyst-kpi-item">
              <span className="analyst-kpi-label">Ambang Operasional NOAA</span>
              <span className="analyst-kpi-val">&gt; +0,50 °C (5 periode)</span>
            </div>
            <div className="analyst-kpi-item">
              <span className="analyst-kpi-label">Indeks ONI Historis</span>
              <span className="analyst-kpi-val">+{currentClimateState.oniHistorical} °C</span>
            </div>
            <div className="analyst-kpi-item">
              <span className="analyst-kpi-label">Southern Oscillation (SOI)</span>
              <span className="analyst-kpi-val">{currentClimateState.soiValue} (Melemah)</span>
            </div>
            <div className="analyst-kpi-item">
              <span className="analyst-kpi-label">Dipole Mode (DMI / IOD)</span>
              <span className="analyst-kpi-val">+{currentClimateState.dmiValue} °C (Netral)</span>
            </div>
            <div className="analyst-kpi-item">
              <span className="analyst-kpi-label">Akurasi MAE ({selectedLead})</span>
              <span className="analyst-kpi-val">
                {currentLeadData.kmrvMae} °C (KMRV) vs {currentLeadData.persMae} °C (Persistensi)
              </span>
            </div>
          </div>
        )}
      </section>

      {/* 2. Tiga Kartu KPI: Peluang Fase + Anomali SST Wilayah + Status MHW */}
      <section className="kpi-grid" aria-label="Tiga indikator utama kondisi laut">
        {/* KPI 1: Peluang Fase 3 Bulan ke Depan */}
        <article className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-card-title">Peluang Fase ({selectedLead})</span>
            <span className="dummy-tag">Simulasi</span>
          </div>

          <div className="kpi-big-number">
            {currentLeadData.elNinoProb}%
            <span className="kpi-sub-unit">Peluang El Niño</span>
          </div>

          {/* 100% Horizontal Stacked Bar */}
          <div className="stacked-prob-bar" role="img" aria-label={`Peluang El Nino ${currentLeadData.elNinoProb}%, Netral ${currentLeadData.neutralProb}%, La Nina ${currentLeadData.laNinaProb}%`}>
            <div
              className="stacked-seg seg-elnino"
              style={{ width: `${currentLeadData.elNinoProb}%` }}
              title={`El Niño: ${currentLeadData.elNinoProb}%`}
            />
            <div
              className="stacked-seg seg-neutral"
              style={{ width: `${currentLeadData.neutralProb}%` }}
              title={`Netral: ${currentLeadData.neutralProb}%`}
            />
            <div
              className="stacked-seg seg-lanina"
              style={{ width: `${currentLeadData.laNinaProb}%` }}
              title={`La Niña: ${currentLeadData.laNinaProb}%`}
            />
          </div>

          <div className="stacked-legend">
            <span className="legend-chip legend-chip-elnino">El Niño {currentLeadData.elNinoProb}%</span>
            <span className="legend-chip legend-chip-neutral">Netral {currentLeadData.neutralProb}%</span>
            <span className="legend-chip legend-chip-lanina">La Niña {currentLeadData.laNinaProb}%</span>
          </div>
        </article>

        {/* KPI 2: Anomali SST Wilayah Terpilih */}
        <article className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-card-title">SST {currentRegionData.name}</span>
            <span className="dataset-label">OISST v2.1</span>
          </div>

          <div className="kpi-big-number">
            {currentRegionData.anomaly} °C
            <span className="kpi-sub-unit">Anomali SST Harian</span>
          </div>

          <div className="kpi-metric-row">
            <span className="kpi-row-label">Suhu Pengukuran</span>
            <strong className="kpi-row-val">{currentRegionData.sstVal} °C</strong>
          </div>
          <div className="kpi-metric-row">
            <span className="kpi-row-label">Rata-rata Normal (Klimatologi)</span>
            <strong className="kpi-row-val">{currentRegionData.climatology} °C</strong>
          </div>

          <p className="kpi-context-note">
            {currentRegionData.significance}
          </p>
        </article>

        {/* KPI 3: Status Marine Heatwave (MHW) */}
        <article className="kpi-card">
          <div className="kpi-card-header">
            <span className="kpi-card-title">Marine Heatwave (MHW)</span>
            <span className="dummy-tag">Data contoh</span>
          </div>

          <div className="kpi-big-number">
            {currentRegionData.mhwStatus.includes('Aktif') ? 'Aktif' : 'Normal'}
            <span className="kpi-sub-unit">Ambang Persentil ke-90</span>
          </div>

          <div className="kpi-metric-row">
            <span className="kpi-row-label">Wilayah Terdampak</span>
            <strong className="kpi-row-val">{currentRegionData.name}</strong>
          </div>
          <div className="kpi-metric-row">
            <span className="kpi-row-label">Durasi Terdeteksi</span>
            <strong className="kpi-row-val">
              {currentRegionData.mhwDuration > 0 ? `${currentRegionData.mhwDuration} hari beruntun` : '0 hari'}
            </strong>
          </div>

          <p className="kpi-context-note">
            MHW dihitung berdasarkan SST lokal &gt; P90 selama minimal 5 hari berturut-turut.
          </p>
        </article>
      </section>

      {/* 3. Grafik Utama: Deret Waktu 24 Bulan RONI + Prakiraan KMRV dengan Pita Ketidakpastian */}
      <section className="chart-card" aria-labelledby="roni-chart-title">
        <div className="chart-header">
          <div>
            <h3 id="roni-chart-title" className="chart-title">
              Indeks RONI Melampaui +0,5 °C; Anomali Hangat Diproyeksikan Bertahan Hingga Awal 2027
            </h3>
            <p className="chart-subtitle">
              <span className="chart-subtitle--wide">Deret waktu 24 bulan observasi historis dan 6 bulan proyeksi KMRV dengan pita ketidakpastian (80% CI).</span>
              <span className="chart-subtitle--compact">Deret 14 bulan terakhir dan 6 bulan proyeksi KMRV dengan pita ketidakpastian (80% CI).</span>
            </p>
          </div>

          <div className="chart-tag-group">
            <span className="dummy-tag">Proyeksi Model</span>
            <span className="dataset-label">NOAA CPC + KMRV</span>
          </div>
        </div>

        <div className="chart-container chart-container--wide">
          <RoniTraceChart />
        </div>
        <div className="chart-container chart-container--compact">
          <RoniTraceChart compact />
        </div>

        <div className="chart-footer-note">
          <span className="source-citation">
            Sumber: Indeks RONI NOAA CPC (3-month running mean) & Model KMRV v2.1.
          </span>
          <span className="caution-citation">
            Pita arsir menunjukkan interval keyakinan 80%. Semakin jauh horizon waktu, ketidakpastian semakin lebar.
          </span>
        </div>
      </section>

      {/* 4. Panel "Apa artinya bagi Indonesia?": Dampak Hujan Sederhana */}
      <section className="impact-laymen-section" aria-labelledby="laymen-impact-title">
        <div className="impact-header-group">
          <div>
            <h3 id="laymen-impact-title" className="section-title">
              Apa Artinya Kondisi Ini Bagi Indonesia?
            </h3>
            <p className="section-lead">
              Pemanasan di Pasifik tengah cenderung mengurangi pembentukan awan hujan di sebagian wilayah Indonesia.
              Berikut gambaran risiko per pulau:
            </p>
          </div>
          <button
            type="button"
            className="btn btn--subtle"
            onClick={() => onNavigateTab('dampak')}
          >
            Buka Heatmap Dampak
          </button>
        </div>

        <div className="impact-cards-grid">
          {regionalRainfallMatrix.map((item) => (
            <article key={item.region} className="impact-region-card">
              <div className="impact-region-head">
                <strong className="impact-region-name">{item.region}</strong>
                <span className="impact-deviation-pill">
                  {item.jja}% (Musim Kemarau)
                </span>
              </div>
              <p className="impact-region-desc">{item.primaryRisk}</p>
            </article>
          ))}
        </div>

        <div className="uncertainty-disclaimer-box">
          <strong className="disclaimer-title">Catatan Kejujuran Ilmiah & Batasan Model:</strong>
          <p className="disclaimer-text">
            Prakiraan ini bersifat probabilistik musiman dan bukan jaminan cuaca harian.
            Dampak El Niño sangat dipengaruhi oleh interaksi lokal seperti topografi pegunungan, suhu lokal Selat Makassar,
            dan dinamika Samudra Hindia (IOD). Rujuk selalu buletin iklim dan peringatan resmi BMKG untuk kebijakan publik.
          </p>
        </div>
      </section>
    </div>
  );
}
