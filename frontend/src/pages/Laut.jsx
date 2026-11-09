import React from 'react';
import SSTMap from '../components/SSTMap';
import { regionalOceanData, mhwEventsRecords } from '../data/climateData';

export default function Laut({ selectedRegion, setSelectedRegion, isAnalystMode }) {
  const currentRegion =
    regionalOceanData.find((r) => r.name === selectedRegion) ||
    regionalOceanData[1]; // default Selat Makassar

  return (
    <div className="ocean-page">
      {/* 1. Peta Interaktif Telemetri Suhu Permukaan Laut (SST) */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">
              Peta Telemetri Suhu Permukaan Laut (SST) & Domain Riset KMRV
            </h2>
            <p className="chart-subtitle">
              Satelit NOAA Daily OISST v2.1 resolusi 0,25°. Klik salah satu poligon perairan untuk memusatkan analisis data deret waktu dan MHW.
            </p>
          </div>
          <span className="dataset-label">NOAA OISST v2.1</span>
        </div>

        <SSTMap
          regions={regionalOceanData}
          selectedRegion={selectedRegion}
          onSelectRegion={(reg) => setSelectedRegion(reg)}
        />

        <div className="map-legend-bar">
          <div className="legend-item">
            <span className="legend-indicator elnino" />
            <span>Anomali Positif / Hangat (&gt; 0 °C)</span>
          </div>
          <div className="legend-item">
            <span className="legend-indicator neutral" />
            <span>Kondisi Rata-rata Normal (±0,1 °C)</span>
          </div>
          <div className="legend-item">
            <span className="legend-indicator lanina" />
            <span>Anomali Negatif / Dingin (&lt; 0 °C)</span>
          </div>
          <div className="legend-tip">
            Klik poligon pada peta untuk memilih domain perairan.
          </div>
        </div>
      </section>

      {/* 2. Deret Waktu SST vs Klimatologi Lokal Wilayah Terpilih */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">
              Deret Waktu SST 12 Bulan Terakhir vs Klimatologi 30 Tahun: {currentRegion.name}
            </h3>
            <p className="chart-subtitle">
              Perbandingan suhu permukaan laut harian aktual terhadap baseline normal periode 1991 sampai 2020.
            </p>
          </div>
          <span className="dummy-tag">Simulasi Sensor</span>
        </div>

        <div className="sst-climatology-chart-wrap">
          <svg
            width="100%"
            height="180"
            viewBox="0 0 600 180"
            fill="none"
            className="sst-climatology-svg"
            role="img"
            aria-label={`Grafik suhu aktual vs klimatologi ${currentRegion.name}`}
          >
            {/* Grid Horizontal */}
            <line x1="50" y1="40" x2="560" y2="40" stroke="var(--color-rule)" strokeWidth="1" />
            <text x="40" y="44" textAnchor="end" fill="var(--color-muted)" fontSize="12" fontFamily="var(--font-outlier)">31 °C</text>

            <line x1="50" y1="80" x2="560" y2="80" stroke="var(--color-rule)" strokeWidth="1" />
            <text x="40" y="84" textAnchor="end" fill="var(--color-muted)" fontSize="12" fontFamily="var(--font-outlier)">29 °C</text>

            <line x1="50" y1="120" x2="560" y2="120" stroke="var(--color-rule)" strokeWidth="1" />
            <text x="40" y="124" textAnchor="end" fill="var(--color-muted)" fontSize="12" fontFamily="var(--font-outlier)">27 °C</text>

            {/* Garis Ambang Persentil ke-90 (P90) MHW - Garis Putus Merah Tipis */}
            <path
              d="M 50 68 Q 200 62 350 65 T 560 62"
              stroke="var(--color-elnino)"
              strokeWidth="1.2"
              strokeDasharray="4 4"
              fill="none"
            />
            <text x="480" y="56" fill="var(--color-elnino)" fontSize="12" fontFamily="var(--font-body)">
              Ambang P90 (Batas MHW)
            </text>

            {/* Garis Klimatologi 30 Tahun (Abu-abu Halus) */}
            <path
              d="M 50 85 Q 200 80 350 84 T 560 82"
              stroke="var(--color-muted)"
              strokeWidth="1.8"
              fill="none"
            />
            <text x="70" y="98" fill="var(--color-muted)" fontSize="12" fontFamily="var(--font-body)">
              Rata-rata Normal (1991 sampai 2020)
            </text>

            {/* Garis SST Aktual (Biru Brand Pekat) */}
            <path
              d="M 50 88 Q 180 82 280 75 Q 380 62 480 60 L 560 58"
              stroke="var(--color-brand)"
              strokeWidth="2.5"
              fill="none"
            />
            <circle cx="560" cy="58" r="4.5" fill="var(--color-brand)" />
            <text x="560" y="46" textAnchor="end" fill="var(--color-brand)" fontSize="12" fontFamily="var(--font-outlier)" fontWeight="600">
              Aktual {currentRegion.sstVal} °C ({currentRegion.anomaly} °C)
            </text>
          </svg>
        </div>

        <div className="chart-footer-note">
          <span>Klimatologi dihitung dari 30 tahun historis OISST. Kejadian MHW terdeteksi ketika garis aktual berada di atas garis P90 minimal 5 hari berturut-turut.</span>
        </div>
      </section>

      {/* 3. Tabel Kejadian Marine Heatwave (MHW) */}
      <section className="chart-card">
        <div className="chart-header">
          <div>
            <h3 className="chart-title">
              Catatan Kejadian Gelombang Panas Laut (MHW) di Perairan Indonesia
            </h3>
            <p className="chart-subtitle">
              Klasifikasi kategori intensitas MHW mengacu pada kerangka kerja Hobday et al. (2016).
            </p>
          </div>
          <span className="dummy-tag">Data contoh</span>
        </div>

        <div className="table-responsive">
          <table className="data-table">
            <thead>
              <tr>
                <th>Wilayah Perairan</th>
                <th>Mulai Kejadian</th>
                <th>Status</th>
                <th>Durasi</th>
                <th>Intensitas Maks</th>
                <th>Kategori Hobday</th>
                <th>Ringkasan Dampak Ekologis</th>
              </tr>
            </thead>
            <tbody>
              {mhwEventsRecords.map((mhw) => (
                <tr key={mhw.region}>
                  <td><strong>{mhw.region}</strong></td>
                  <td>{mhw.startDate}</td>
                  <td>
                    <span className={`status-pill ${mhw.status.includes('berlangsung') ? 'is-warning' : 'is-normal'}`}>
                      {mhw.status}
                    </span>
                  </td>
                  <td className="table-numeric">{mhw.duration}</td>
                  <td className="table-numeric"><strong>{mhw.maxIntensity}</strong></td>
                  <td>
                    <span className="category-pill">{mhw.category}</span>
                  </td>
                  <td className="table-text-muted">{mhw.impactSummary}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        <div className="chart-footer-note">
          <span>
            Peringatan: Ambang MHW dihitung dari klimatologi suhu laut lokal dan TIDAK sama dengan ambang indeks ENSO (RONI).
          </span>
        </div>
      </section>
    </div>
  );
}
