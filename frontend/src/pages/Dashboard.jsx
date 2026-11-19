import React, { useState } from 'react';
import ConfusionMatrix from '../components/ConfusionMatrix';
import OniHistoryChart from '../components/OniHistoryChart';
import SeaTempMap from '../components/SeaTempMap';
import TestPredictionChart from '../components/TestPredictionChart';
import { facts, latest, meta, metrics, regions, testPredictions } from '../data/realData';
import { num, signed, monthLabel, shortMonth } from '../utils/format';
import { sstColor } from '../utils/sstScale';

const HORIZON_OPTIONS = [
  { value: '1', label: '1 bulan ke depan' },
  { value: '3', label: '3 bulan ke depan' },
  { value: '6', label: '6 bulan ke depan' },
];

const best = metrics['1'];

export default function Dashboard() {
  const [selectedHorizon, setSelectedHorizon] = useState('1');

  const activeMetric = metrics[selectedHorizon];
  const activePredictions = testPredictions[selectedHorizon] || [];
  const isWeakLead = selectedHorizon !== '1';
  const h = parseInt(selectedHorizon, 10);

  // date column = tanggal INPUT (kapan prediksi dibuat)
  // tanggal TARGET = input + h bulan
  const addMonths = (dateStr, months) => {
    const d = new Date(dateStr);
    d.setMonth(d.getMonth() + months);
    return d.toISOString().slice(0, 7);
  };

  const activeInputRange = activePredictions.length > 0
    ? `${shortMonth(activePredictions[0].date.slice(0, 7))} – ${shortMonth(activePredictions[activePredictions.length - 1].date.slice(0, 7))}`
    : '';
  const activeTargetRange = activePredictions.length > 0
    ? `${shortMonth(addMonths(activePredictions[0].date, h))} – ${shortMonth(addMonths(activePredictions[activePredictions.length - 1].date, h))}`
    : '';

  const validationMatrix = activeMetric.validation.confusion_matrix;
  const testMatrix = activeMetric.test.confusion_matrix;
  const validationSamples = validationMatrix.flat().reduce((sum, value) => sum + value, 0);
  const testSamples = testMatrix.flat().reduce((sum, value) => sum + value, 0);

  return (
    <div className="lp-page">
      {/* 1 — Pembuka */}
      <section className="lp-hero" id="awal" aria-labelledby="heroTitle">
        <div className="lp-wrap lp-hero-grid">
          <div className="lp-hero-copy">
            <span className="lp-hero-pill">Model KMRV · Causal LSTM + LightGBM</span>
            <h1 id="heroTitle" className="lp-brand">Lautan.id</h1>
            <p className="lp-tagline">Pantau Iklim & Dinamika Laut Indonesia</p>
            <p className="lp-hero-text">
              Monitoring anomali suhu muka laut (SST) di lima domain maritim nusantara
              serta prakiraan fenomena El Niño & La Niña berbasis kecerdasan buatan.
            </p>
            <div className="lp-hero-actions">
              <a className="lp-cta" href="#prediksi">
                Lihat Prediksi <span aria-hidden="true">→</span>
              </a>
              <a className="lp-cta-ghost" href="#suhu-laut">
                Peta Suhu Laut
              </a>
            </div>
          </div>

          <div className="lp-hero-visual" aria-hidden="true">
            <SeaTempMap variant="hero" />
          </div>
        </div>
      </section>

      {/* 2 — Suhu laut */}
      <section className="lp-section" id="suhu-laut" aria-labelledby="sstTitle">
        <div className="lp-wrap">
          <header className="lp-head">
            <h2 id="sstTitle" className="lp-title">Kondisi Suhu Lautan</h2>
            <p className="lp-sub">
              Suhu permukaan laut dan anomali lima domain perairan Indonesia pada{' '}
              {monthLabel(latest.date)}. Warna laut adalah perkiraan visual antardomain,
              bukan grid SST penuh.
            </p>
          </header>

          <div className="lp-map-layout">
            <SeaTempMap regions={regions} variant="heatmap" />

            <div className="lp-rail">
              <h3 className="lp-rail-title">Penjelasan</h3>
              <ul className="sea-domain-list">
                {regions.map((region) => (
                  <li key={region.key} className="sea-domain-item">
                    <span className="sea-domain-dot" style={{ background: sstColor(region.sst) }} />
                    <span className="sea-domain-name">{region.name}</span>
                    <span className="sea-domain-sst">{num(region.sst, 1)} °C</span>
                    <span className="sea-domain-anom">{signed(region.anomaly)}</span>
                  </li>
                ))}
              </ul>
            </div>
          </div>

          <div className="lp-keterangan">
            <h3 className="lp-rail-title">Keterangan</h3>
            <div className="lp-scale">
              <div className="sea-scale-bar" />
              <div className="sea-scale-ticks">
                <span>26</span>
                <span>27</span>
                <span>28</span>
                <span>29</span>
                <span>30</span>
                <span>31 °C</span>
              </div>
            </div>
            <p className="sea-map-note">
              Angka kecil di kanan adalah anomali terhadap rata-rata bulan yang sama,
              dihitung dari data {monthLabel(meta.datasetStart)} – {monthLabel(meta.datasetEnd)}.
            </p>
          </div>
        </div>
      </section>

      {/* 3 — ONI historis */}
      <section className="lp-section" id="laut" aria-labelledby="oniTitle">
        <div className="lp-wrap">
          <header className="lp-head">
            <h2 id="oniTitle" className="lp-title">Apa yang Terjadi pada Laut?</h2>
            <p className="lp-sub">
              Dinamika Oceanic Niño Index (ONI) bulanan {monthLabel(meta.datasetStart)} – {monthLabel(meta.datasetEnd)}.
              ONI mengukur anomali suhu permukaan laut di Samudra Pasifik ekuatorial tengah-timur (wilayah Niño 3.4).
            </p>
          </header>

          {/* Kotak penjelasan ringkas makna fase ONI */}
          <div className="lp-explainer-grid">
            <div className="lp-explainer-item">
              <span className="explainer-badge el-nino">El Niño (≥ +0,5 °C)</span>
              <p>
                Suhu laut Pasifik menghangat di atas normal. Dampak di Indonesia: pasokan uap air berkurang, memicu musim kemarau lebih kering dan risiko kekeringan.
              </p>
            </div>
            <div className="lp-explainer-item">
              <span className="explainer-badge neutral">Netral (−0,5 s.d. +0,5 °C)</span>
              <p>
                Suhu laut Pasifik berada pada batas normal klimatologis. Pola cuaca dan curah hujan mengikuti siklus musim lokal tanpa gangguan ekstrem.
              </p>
            </div>
            <div className="lp-explainer-item">
              <span className="explainer-badge la-nina">La Niña (≤ −0,5 °C)</span>
              <p>
                Suhu laut Pasifik mendingin di bawah normal. Dampak di Indonesia: penguapan meningkat pesat, curah hujan bertambah, risiko banjir dan cuaca basah tinggi.
              </p>
            </div>
          </div>

          <div className="lp-chart-card">
            <OniHistoryChart />

            <div className="lp-legend-row" style={{ marginTop: '12px' }}>
              <span className="legend-chip legend-chip--plain">
                <span className="legend-swatch swatch-observed" />
                ONI bulanan
              </span>
              <span className="legend-chip legend-chip--plain">
                <span className="legend-swatch swatch-warm" />
                Ambang El Niño +0,5 °C
              </span>
              <span className="legend-chip legend-chip--plain">
                <span className="legend-swatch swatch-cool" />
                Ambang La Niña −0,5 °C
              </span>
              <span className="legend-chip legend-chip--plain">
                <span className="legend-swatch swatch-test" />
                Periode data uji
              </span>
            </div>

            <div className="lp-inner-cards">
              <article className="lp-inner-card">
                <span className="lp-card-label">El Niño terkuat</span>
                <strong className="lp-card-value">{signed(facts.warmestOni.value)} °C</strong>
                <span className="lp-card-note">{monthLabel(facts.warmestOni.date)}</span>
              </article>

              <article className="lp-inner-card">
                <span className="lp-card-label">La Niña terkuat</span>
                <strong className="lp-card-value">{signed(facts.coldestOni.value)} °C</strong>
                <span className="lp-card-note">{monthLabel(facts.coldestOni.date)}</span>
              </article>

              <article className="lp-inner-card">
                <span className="lp-card-label">Sebaran fase</span>
                <strong className="lp-card-value">
                  {facts.counts.elNino} / {facts.counts.netral} / {facts.counts.laNina}
                </strong>
                <span className="lp-card-note">El Niño / Netral / La Niña</span>
              </article>
            </div>
          </div>
        </div>
      </section>

      {/* 4 — Prediksi */}
      <section className="lp-section" id="prediksi" aria-labelledby="prediksiTitle">
        <div className="lp-wrap">
          <header className="lp-head">
            <h2 id="prediksiTitle" className="lp-title">Prediksi Nilai ONI</h2>
            <p className="lp-sub">
              Peramalan nilai kontinu ONI dengan model <strong>Causal LSTM</strong> (target proyeksi {selectedHorizon} bulan ke depan).
              Garis hitam adalah nilai observasi asli NOAA, garis putus-putus biru adalah proyeksi model.
            </p>
          </header>

          <div className="lp-guide-card">
            <strong>Cara Kerja Prediksi:</strong> Model AI menggabungkan dua tahap: (1) <strong>Causal LSTM</strong> memproyeksikan deret angka ONI {selectedHorizon} bulan ke depan dari batas observasi, lalu (2) <strong>LightGBM</strong> mengklasifikasikan kategori fasenya.
          </div>

          <div className="lp-chart-card">
            <div className="lp-chart-toolbar">
              <div className="lp-seg" role="group" aria-label="Pilih horizon prediksi">
                {HORIZON_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={`lp-seg-btn ${selectedHorizon === option.value ? 'is-active' : ''}`}
                    aria-pressed={selectedHorizon === option.value}
                    onClick={() => setSelectedHorizon(option.value)}
                  >
                    {option.label} {option.value === '1' ? '★' : ''}
                  </button>
                ))}
              </div>
            </div>

            {isWeakLead && (
              <div className="lp-alert" role="note">
                <strong>Prakiraan {selectedHorizon} bulan ke depan belum terbukti.</strong>
                Akurasi validasi {num(activeMetric.validation.accuracy)} — model mengalami degradasi keterampilan pada lead waktu panjang. Gunakan horizon 1 bulan untuk hasil yang dapat diandalkan.
              </div>
            )}

            <TestPredictionChart horizon={selectedHorizon} />

            {/* Stat cards dimasukkan di dalam box putih di bawah chart & diperkecil */}
            <div className="lp-inner-cards">
              <article className="lp-inner-card">
                <span className="lp-card-label">Akurasi uji</span>
                <strong className="lp-card-value">
                  {Math.round(activeMetric.test.accuracy * 100)}%
                </strong>
                <span className="lp-card-note">{testSamples} bulan uji ({selectedHorizon === '1' ? '5 benar dari 7' : selectedHorizon === '3' ? 'semua Netral' : '0 benar'})</span>
              </article>

              <article className="lp-inner-card">
                <span className="lp-card-label">Rata-rata meleset</span>
                <strong className="lp-card-value">{num(activeMetric.test.lstm_oni_rmse)} °C</strong>
                <span className="lp-card-note">RMSE ONI pada data uji</span>
              </article>

              <article className="lp-inner-card">
                <span className="lp-card-label">Akurasi validasi</span>
                <strong className="lp-card-value">
                  {Math.round(activeMetric.validation.accuracy * 100)}%
                </strong>
                <span className="lp-card-note">
                  {validationSamples} bulan · seimbang{' '}
                  {Math.round(activeMetric.validation.balanced_accuracy * 100)}%
                </span>
              </article>
            </div>
          </div>

          {selectedHorizon === '3' && (
            <p className="sea-map-note" style={{ marginTop: '12px' }}>
              Catatan: Akurasi 100% pada horizon 3 bulan berasal dari 7 sampel yang kebetulan seluruhnya Netral — ini hasil tebakan kelas mayoritas, bukan keterampilan nyata model.
            </p>
          )}
        </div>
      </section>

      {/* 5 — Evaluasi */}
      <section className="lp-section" id="model" aria-labelledby="modelTitle">
        <div className="lp-wrap">
          <header className="lp-head">
            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start', flexWrap: 'wrap', gap: '12px' }}>
              <div>
                <h2 id="modelTitle" className="lp-title">
                  {selectedHorizon === '1'
                    ? 'Seberapa Akurat Modelnya? (Prakiraan 1 Bulan ke Depan)'
                    : selectedHorizon === '3'
                      ? 'Prakiraan 3 Bulan ke Depan: Hasil Trivial'
                      : 'Prakiraan 6 Bulan ke Depan: Belum Bisa Diandalkan'}
                </h2>
                <p className="lp-sub">
                  Evaluasi klasifikasi fase ENSO (*La Niña*, *Netral*, *El Niño*) pada data validasi dan data uji kronologis.
                </p>
              </div>

              <div className="lp-seg" role="group" aria-label="Pilih horizon evaluasi">
                {HORIZON_OPTIONS.map((option) => (
                  <button
                    key={option.value}
                    type="button"
                    className={`lp-seg-btn ${selectedHorizon === option.value ? 'is-active' : ''}`}
                    aria-pressed={selectedHorizon === option.value}
                    onClick={() => setSelectedHorizon(option.value)}
                  >
                    {option.label}
                  </button>
                ))}
              </div>
            </div>
          </header>

          {/* Sampaikan kesimpulannya dulu sebelum tabel */}
          {selectedHorizon === '1' && (
            <div className="lp-conclusion-banner is-proven">
              <span className="lp-conclusion-title">✓ Kesimpulan: Model terbukti andal pada horizon 1 bulan (Akurasi Uji 71%)</span>
              <p className="lp-conclusion-desc">
                Pada prakiraan 1 bulan ke depan, model berhasil menebak fase dengan benar pada <strong>5 dari 7 bulan uji</strong>. Ini adalah satu-satunya horizon yang lulus validasi ilmiah di <code>model_manifest.json</code>.
              </p>
            </div>
          )}

          {selectedHorizon === '3' && (
            <div className="lp-conclusion-banner is-trivial">
              <span className="lp-conclusion-title">ℹ Kesimpulan: Akurasi semu 100% pada horizon 3 bulan (Trivial Majority Class)</span>
              <p className="lp-conclusion-desc">
                Seluruh 7 bulan uji berkondisi Netral dan model menebak Netral untuk semuanya. Angka 100% ini terjadi karena model menebak kelas mayoritas saja, bukan karena kepandaian prediktif model.
              </p>
            </div>
          )}

          {selectedHorizon === '6' && (
            <div className="lp-conclusion-banner is-failed">
              <span className="lp-conclusion-title">⚠ Kesimpulan: Prakiraan 6 bulan ke depan belum bisa dipercaya (Akurasi Uji 0%)</span>
              <p className="lp-conclusion-desc">
                Pada horizon 6 bulan, model salah di semua 7 bulan uji. Model terus-menerus menebak <em>El Niño</em>, padahal kondisi sebenarnya di laut adalah <em>La Niña</em> atau <em>Netral</em>.
              </p>
            </div>
          )}

          {/* Petunjuk membaca tabel sederhana dengan contoh konkret */}
          <div className="lp-guide-card">
            <strong>Cara Membaca Tabel:</strong> Baris menunjukkan <strong>kondisi sebenarnya</strong> di alam, kolom menunjukkan <strong>tebakan model</strong>. Kotak hijau berlabel <strong>✓ Tepat</strong> adalah tebakan yang benar.
            <br />
            <strong>Contoh nyata:</strong> Angka 4 di baris <em>Netral</em> dan kolom <em>El Niño</em> berarti ada 4 bulan yang sebenarnya Netral keliru ditebak model sebagai El Niño.
          </div>

          <div className="lp-cm-grid">
            <div className="cm-block">
              <div style={{ marginBottom: '8px' }}>
                <span className="cm-label" style={{ fontWeight: 700, color: '#0f172a' }}>
                  Validasi · {validationSamples} bulan
                </span>
                <p style={{ fontSize: '11px', color: '#64748b', margin: '2px 0 0' }}>
                  Dipakai untuk melatih dan menyetel hyperparameter model.
                </p>
              </div>
              <ConfusionMatrix matrix={validationMatrix} />
            </div>

            <div className="cm-block">
              <div style={{ marginBottom: '8px' }}>
                <span className="cm-label" style={{ fontWeight: 700, color: '#0f172a' }}>
                  Uji · {testSamples} bulan
                </span>
                <p style={{ fontSize: '11px', color: '#64748b', margin: '2px 0 0' }}>
                  Pengujian akhir pada bulan yang belum pernah dilihat model sama sekali.
                </p>
              </div>
              <ConfusionMatrix matrix={testMatrix} />
            </div>
          </div>
        </div>
      </section>

    </div>
  );
}
