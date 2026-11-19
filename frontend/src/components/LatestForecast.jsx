import React, { useEffect, useState } from 'react';
import { monthLabel, num } from '../utils/format';

const PHASE_ORDER = ['La Niña', 'Netral', 'El Niño'];

export default function LatestForecast({ horizon }) {
  const [forecast, setForecast] = useState(null);
  const [error, setError] = useState('');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const controller = new AbortController();

    async function loadForecast() {
      setLoading(true);
      setError('');
      try {
        const response = await fetch(
          `/api/v1/forecast/latest?horizon=${encodeURIComponent(horizon)}`,
          { signal: controller.signal, cache: 'no-store' },
        );
        const body = await response.json();
        if (!response.ok) {
          throw new Error(body.detail || `Permintaan gagal (${response.status})`);
        }
        setForecast(body);
      } catch (requestError) {
        if (requestError.name !== 'AbortError') {
          setError(requestError.message || 'Tidak dapat memuat prediksi model.');
          setForecast(null);
        }
      } finally {
        if (!controller.signal.aborted) {
          setLoading(false);
        }
      }
    }

    loadForecast();
    return () => controller.abort();
  }, [horizon]);

  return (
    <div className="lp-chart-card lp-live-forecast-card" aria-busy={loading}>
      <div className="lp-live-forecast-heading">
        <div>
          <h3 className="lp-rail-title">Inferensi model terbaru</h3>
          <p className="chart-subtitle">
            Causal LSTM + XGBoost · horizon {horizon} bulan
          </p>
        </div>
        {loading && <span role="status">Menghitung prediksi…</span>}
      </div>

      {error && (
        <div className="lp-alert lp-live-forecast-error" role="alert">
          <strong>Prediksi belum tersedia.</strong>
          {error}
        </div>
      )}

      {forecast && (
        <>
          <div className="lp-inner-cards">
            <article className="lp-inner-card">
              <span className="lp-card-label">Proyeksi ONI</span>
              <strong className="lp-card-value">
                {num(forecast.predicted_oni, 2)} °C
              </strong>
              <span className="lp-card-note">
                Target {monthLabel(`${forecast.target_month}-01`)}
              </span>
            </article>
            <article className="lp-inner-card">
              <span className="lp-card-label">Fase prediksi</span>
              <strong className="lp-card-value">
                {forecast.predicted_phase.label}
              </strong>
              <span className="lp-card-note">Keluaran klasifikasi XGBoost</span>
            </article>
            <article className="lp-inner-card">
              <span className="lp-card-label">Probabilitas fase</span>
              <span className="lp-card-note">
                {PHASE_ORDER.map((phase) => (
                  <React.Fragment key={phase}>
                    {phase}: {Math.round(forecast.phase_probabilities[phase] * 100)}%
                    {phase !== PHASE_ORDER[PHASE_ORDER.length - 1] ? ' · ' : ''}
                  </React.Fragment>
                ))}
              </span>
            </article>
          </div>
          <p className="lp-live-forecast-note">
            Fitur masukan tersedia sampai {monthLabel(`${forecast.input_through}-01`)}.
            Ini inferensi langsung dari artefak model, bukan data observasi real-time.
          </p>
        </>
      )}
    </div>
  );
}
