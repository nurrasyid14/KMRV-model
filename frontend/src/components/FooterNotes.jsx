import React from 'react';
import { meta } from '../data/realData';
import { monthLabel } from '../utils/format';

export default function FooterNotes() {
  return (
    <footer className="footer-dock">
      <div className="footer-meta-bar">
        <div className="footer-brand-meta">
          <span className="footer-model-badge">lautan.id</span>
          <span className="footer-meta-item">Model KMRV (Causal LSTM + XGBoost Ensemble)</span>
          <span className="footer-meta-item">
            Dataset: {monthLabel(meta.datasetStart)} – {monthLabel(meta.datasetEnd)}
          </span>
        </div>

        <div className="footer-sources-meta">
          <span className="source-tag">dataset/*_features.csv</span>
          <span className="source-tag">model/enso_ensemble_*</span>
        </div>

        <div className="footer-disclaimer-meta">
          <span>Prediksi memakai input terakhir yang tersedia; bukan feed real-time. Peringatan resmi tetap milik BMKG.</span>
        </div>
      </div>
    </footer>
  );
}
