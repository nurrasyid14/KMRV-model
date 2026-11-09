import React, { useState } from 'react';
import { currentClimateState, climateDatasetMeta } from '../data/climateData';

export default function Header({
  isAnalystMode,
  setIsAnalystMode,
  selectedRegion,
  setSelectedRegion,
  selectedLead,
  setSelectedLead
}) {
  const [copyFeedback, setCopyFeedback] = useState(false);

  const handleCopySummary = () => {
    const summaryText = `[KMRV ENSO INTELLIGENCE - ${climateDatasetMeta.lastUpdated}]
Status: ${currentClimateState.roniStatus} (RONI: ${currentClimateState.roniLatest > 0 ? '+' : ''}${currentClimateState.roniLatest} °C).
Proyeksi Lead ${selectedLead}: ${currentClimateState.leadTimes[selectedLead]?.elNinoProb}% El Niño, ${currentClimateState.leadTimes[selectedLead]?.neutralProb}% Netral, ${currentClimateState.leadTimes[selectedLead]?.laNinaProb}% La Niña.
Wilayah Terpilih: ${selectedRegion}.
Sumber: NOAA OISST v2.1 & CPC NOAA. Peringatan: Prakiraan bersifat probabilistik. Rujuk BMKG untuk peringatan dini resmi.`;

    navigator.clipboard?.writeText(summaryText).then(() => {
      setCopyFeedback(true);
      setTimeout(() => setCopyFeedback(false), 2400);
    });
  };

  const handleExportCsv = () => {
    const csvContent = "data:text/csv;charset=utf-8," 
      + "Indeks,Nilai,Periode,Ambang_ElNino,Ambang_LaNina,Sumber\n"
      + `RONI,${currentClimateState.roniLatest},${currentClimateState.roniDate},+0.5,-0.5,NOAA CPC\n`
      + `ONI,${currentClimateState.oniHistorical},Okt 2026,+0.5,-0.5,NOAA CPC\n`
      + `SOI,${currentClimateState.soiValue},Okt 2026,-7.0,+7.0,BOM Australia\n`
      + `DMI,${currentClimateState.dmiValue},Okt 2026,+0.4,-0.4,JAMSTEC\n`;
    
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `kmrv_climate_telemetry_${Date.now()}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <header className="top-header" role="banner">
      <div className="top-header-main">
        <div className="header-meta-group">
          <div className="dataset-badge">
            <span className="dataset-text">
              Data per {climateDatasetMeta.lastUpdated} (NOAA Daily OISST v2.1)
            </span>
          </div>
          <h1 className="header-page-title">
            Pemantauan ENSO & Laut Indonesia
          </h1>
          <p className="header-subtitle">
            {isAnalystMode
              ? 'Mode Analis (BMKG/Peneliti): Menampilkan angka eksak, pita ketidakpastian (CI 80%), metrik error model, dan provenance sensor.'
              : 'Mode Ringkas (Publik): Ringkasan kondisi laut saat ini, peluang fase mendatang, dan arti dampaknya bagi masyarakat.'}
          </p>
        </div>

        {/* Global Toolbar & Mode Switcher */}
        <div className="header-controls" role="region" aria-label="Pengaturan data & filter">
          <div className="mode-toggle-group" role="group" aria-label="Pilih mode audiens">
            <button
              type="button"
              className={`mode-btn ${!isAnalystMode ? 'is-active' : ''}`}
              onClick={() => setIsAnalystMode(false)}
              aria-pressed={!isAnalystMode}
            >
              Mode Ringkas
            </button>
            <button
              type="button"
              className={`mode-btn ${isAnalystMode ? 'is-active' : ''}`}
              onClick={() => setIsAnalystMode(true)}
              aria-pressed={isAnalystMode}
            >
              Mode Analis
            </button>
          </div>

          <div className="header-action-group">
            <button
              type="button"
              className="btn btn--subtle"
              onClick={handleCopySummary}
              title="Salin ringkasan teks untuk laporan atau media sosial"
            >
              {copyFeedback ? 'Tersalin ke Clipboard' : 'Salin Ringkasan'}
            </button>

            <button
              type="button"
              className="btn btn--subtle"
              onClick={handleExportCsv}
              title="Unduh data metrik saat ini dalam format CSV"
            >
              Ekspor CSV
            </button>
          </div>
        </div>
      </div>

      {/* Filter Bar (Progressive Disclosure Controls) */}
      <div className="header-filter-bar">
        <div className="filter-group">
          <label htmlFor="lead-time-select" className="filter-label">
            Horizon Proyeksi
          </label>
          <select
            id="lead-time-select"
            className="filter-select"
            value={selectedLead}
            onChange={(e) => setSelectedLead(e.target.value)}
          >
            <option value="1 bulan">1 Bulan ke Depan (Des 2026)</option>
            <option value="3 bulan">3 Bulan ke Depan (Feb 2027)</option>
            <option value="6 bulan">6 Bulan ke Depan (Mei 2027)</option>
          </select>
        </div>

        <div className="filter-group">
          <label htmlFor="region-select" className="filter-label">
            Fokus Perairan Indonesia
          </label>
          <select
            id="region-select"
            className="filter-select"
            value={selectedRegion}
            onChange={(e) => setSelectedRegion(e.target.value)}
          >
            <option value="Semua wilayah">Semua 5 Domain Observasi</option>
            <option value="Pasifik Niño 3.4">Pasifik Niño 3.4 (Rujukan Global)</option>
            <option value="Selat Makassar">Selat Makassar (Jalur Arlindo)</option>
            <option value="Selat Karimata">Selat Karimata (Paparan Sunda)</option>
            <option value="Selatan Jawa">Selatan Jawa (Zona Upwelling)</option>
            <option value="Maluku-Papua">Maluku-Papua (Kolam Hangat)</option>
          </select>
        </div>

        <div className="filter-note">
          <span className="dummy-tag" title="Fitur prediksi masih dalam tahap pengembangan model">
            Data contoh model
          </span>
          <span className="note-text">
            Hasil modul prediksi KMRV bersifat simulasi dan probabilistik.
          </span>
        </div>
      </div>
    </header>
  );
}
