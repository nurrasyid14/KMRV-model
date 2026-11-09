import React from 'react';
import { climateGlossary } from '../data/climateData';

export default function Glosarium({ isAnalystMode }) {
  return (
    <div className="glossary-page">
      <section className="glossary-section">
        <div className="chart-header">
          <div>
            <h2 className="chart-title">
              Panduan Singkat & Glosarium Sains Iklim
            </h2>
            <p className="chart-subtitle">
              Penjelasan istilah kunci dalam bahasa sederhana agar hasil pemantauan laut dan prediksi ENSO tidak disalahpahami oleh masyarakat.
            </p>
          </div>
          <span className="dataset-label">Edukasi Publik</span>
        </div>

        <div className="glossary-grid">
          {climateGlossary.map((item) => (
            <article key={item.term} className="glossary-card">
              <div className="glossary-card-head">
                <h3 className="glossary-term">{item.term}</h3>
                <span className="glossary-badge">Konsep Kunci</span>
              </div>

              <strong className="glossary-short">{item.short}</strong>
              <p className="glossary-detail">{item.detail}</p>

              {isAnalystMode && (
                <div className="glossary-analyst-box">
                  <span className="glossary-analyst-title">Catatan Teknis / Analis BMKG:</span>
                  <p className="glossary-analyst-text">{item.analystNote}</p>
                </div>
              )}
            </article>
          ))}
        </div>

        <div className="chart-footer-note">
          <span>
            Disusun berdasarkan literatur WMO (World Meteorological Organization) dan modul pemantauan iklim operasional BMKG.
          </span>
        </div>
      </section>
    </div>
  );
}
