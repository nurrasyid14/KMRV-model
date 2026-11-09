import React, { useState } from 'react';
import { regionalRainfallMatrix } from '../data/climateData';

export default function DampakIndonesia() {
  const [activeSeason, setActiveSeason] = useState('jja');

  const seasons = [
    { id: 'djf', label: 'DJF (Des–Feb)', name: 'Puncak Musim Hujan' },
    { id: 'mam', label: 'MAM (Mar–Mei)', name: 'Peralihan Musim I' },
    { id: 'jja', label: 'JJA (Jun–Agu)', name: 'Puncak Musim Kemarau' },
    { id: 'son', label: 'SON (Sep–Nov)', name: 'Peralihan Musim II' }
  ];

  // Helper warna sel heatmap
  const getCellBg = (val) => {
    if (val < -30) return 'var(--color-elnino)'; // defisit kuat
    if (val < -15) return 'var(--color-elnino-soft)'; // defisit sedang
    if (val < 0) return 'var(--color-paper-3)'; // defisit tipis
    return 'var(--color-lanina-soft)'; // surplus
  };

  const getCellTextColor = (val) => {
    if (val < -30) return 'var(--color-paper-2)';
    if (val < -15) return 'var(--color-ink)';
    return 'var(--color-ink)';
  };

  return (
    <div className="impact-page">
      {/* 1. Pengantar & Heatmap Matriks Deviasi Curah Hujan */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">
              Matriks Respons Anomali Curah Hujan Indonesia per Wilayah dan Musim
            </h2>
            <p className="chart-subtitle">
              Persentase deviasi curah hujan dari klimatologi 1991 sampai 2020 selama episode El Niño aktif. Angka negatif menandakan defisit hujan.
            </p>
          </div>
          <span className="dummy-tag">Simulasi ERA5/CHIRPS</span>
        </div>

        {/* Heatmap Table */}
        <div className="table-responsive">
          <table className="heatmap-table">
            <thead>
              <tr>
                <th>Wilayah Kepulauan</th>
                <th className={activeSeason === 'djf' ? 'col-highlight' : ''}>DJF (Des–Feb)</th>
                <th className={activeSeason === 'mam' ? 'col-highlight' : ''}>MAM (Mar–Mei)</th>
                <th className={activeSeason === 'jja' ? 'col-highlight' : ''}>JJA (Jun–Agu)</th>
                <th className={activeSeason === 'son' ? 'col-highlight' : ''}>SON (Sep–Nov)</th>
                <th>Sektor Risiko Utama</th>
              </tr>
            </thead>
            <tbody>
              {regionalRainfallMatrix.map((row) => (
                <tr key={row.region}>
                  <td className="heatmap-region-name">
                    <strong>{row.region}</strong>
                  </td>

                  {/* DJF */}
                  <td
                    className="heatmap-cell"
                    style={{ backgroundColor: getCellBg(row.djf), color: getCellTextColor(row.djf) }}
                  >
                    <strong>{row.djf > 0 ? `+${row.djf}` : row.djf}%</strong>
                  </td>

                  {/* MAM */}
                  <td
                    className="heatmap-cell"
                    style={{ backgroundColor: getCellBg(row.mam), color: getCellTextColor(row.mam) }}
                  >
                    <strong>{row.mam > 0 ? `+${row.mam}` : row.mam}%</strong>
                  </td>

                  {/* JJA */}
                  <td
                    className="heatmap-cell"
                    style={{ backgroundColor: getCellBg(row.jja), color: getCellTextColor(row.jja) }}
                  >
                    <strong>{row.jja > 0 ? `+${row.jja}` : row.jja}%</strong>
                  </td>

                  {/* SON */}
                  <td
                    className="heatmap-cell"
                    style={{ backgroundColor: getCellBg(row.son), color: getCellTextColor(row.son) }}
                  >
                    <strong>{row.son > 0 ? `+${row.son}` : row.son}%</strong>
                  </td>

                  <td className="heatmap-desc-cell">
                    {row.primaryRisk}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="heatmap-legend-row">
          <span className="legend-label">Skala Anomali:</span>
          <div className="legend-scale-bar">
            <span className="scale-item" style={{ backgroundColor: 'var(--color-elnino)' }}>
              &lt; -30% (Kering Ekstrem)
            </span>
            <span className="scale-item" style={{ backgroundColor: 'var(--color-elnino-soft)' }}>
              -15% s.d. -30% (Kering Sedang)
            </span>
            <span className="scale-item" style={{ backgroundColor: 'var(--color-paper-3)' }}>
              -1% s.d. -15% (Kering Ringan)
            </span>
            <span className="scale-item" style={{ backgroundColor: 'var(--color-lanina-soft)' }}>
              &gt; 0% (Normal/Basah)
            </span>
          </div>
        </div>
      </section>

      {/* 2. Simulasi Musim Terpilih */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">
              Eksplorasi Musim: Evaluasi Respons Curah Hujan
            </h3>
            <p className="chart-subtitle">
              Pilih musim untuk melihat pola dampak spasial yang paling relevan bagi kalender tanam dan kesiapsiagaan kekeringan.
            </p>
          </div>

          <div className="season-toggle-group">
            {seasons.map((s) => (
              <button
                key={s.id}
                type="button"
                className={`season-btn ${activeSeason === s.id ? 'is-active' : ''}`}
                aria-pressed={activeSeason === s.id}
                onClick={() => setActiveSeason(s.id)}
              >
                {s.label}
              </button>
            ))}
          </div>
        </div>

        <div className="season-detail-box">
          <div className="season-meta-banner">
            <strong>Fokus: {seasons.find((s) => s.id === activeSeason)?.name} ({activeSeason.toUpperCase()})</strong>
            <span>
              {activeSeason === 'jja' && 'Puncak kemarau: Jawa, Bali, NTB, dan NTT mengalami defisit curah hujan paling tajam (-35% hingga -45%).'}
              {activeSeason === 'son' && 'Musim peralihan: Terjadi keterlambatan awal musim hujan rata-rata 2 hingga 4 dasarian di wilayah Indonesia selatan.'}
              {activeSeason === 'djf' && 'Musim hujan: Dampak El Niño melemah karena suplai monsun Asia barat laut, anomali curah hujan relatif minim.'}
              {activeSeason === 'mam' && 'Peralihan I: Penurunan hujan ringan hingga moderat di wilayah penghasil padi Jawa dan Sulawesi.'}
            </span>
          </div>
        </div>

        <div className="chart-footer-note">
          <span>
            Peringatan: Seluruh nilai dampak curah hujan dihitung dari komposit multidekade satelit CHIRPS & ERA5.
            Model KMRV tidak membuat prediksi cuaca harian. Validasi lapangan resmi merupakan kewenangan BMKG.
          </span>
        </div>
      </section>
    </div>
  );
}
