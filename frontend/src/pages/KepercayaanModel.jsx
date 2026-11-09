import React from 'react';

export default function KepercayaanModel() {
  const skillMatrix = [
    { lead: 'Lead 1 Bulan', djf: 0.94, mam: 0.88, jja: 0.91, son: 0.95, avg: 0.92 },
    { lead: 'Lead 3 Bulan', djf: 0.86, mam: 0.72, jja: 0.81, son: 0.89, avg: 0.82 },
    { lead: 'Lead 6 Bulan', djf: 0.74, mam: 0.58, jja: 0.69, son: 0.78, avg: 0.70 }
  ];

  return (
    <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-lg)' }}>
      
      {/* Row 1: Plume Prakiraan & Evaluasi Skill Musiman */}
      <div className="grid-2col">
        
        {/* Plume Prakiraan KMRV vs IRI */}
        <section className="data-card">
          <div className="card-header">
            <h2 className="card-title">Perbandingan Proyeksi Trajektori Anomali Niño 3.4</h2>
            <p className="card-meta">
              Garis gelap menunjukkan lintasan ensemble KMRV; garis putus-putus menunjukkan ambang batas operasional (+0,5 °C).
            </p>
          </div>

          <div style={{ height: '220px' }}>
            <svg width="100%" height="100%" viewBox="0 0 520 220" fill="none" aria-label="Grafik ensemble plume">
              <line x1="40" y1="65" x2="490" y2="65" stroke="var(--color-elnino)" strokeWidth="1" strokeDasharray="4 4" />
              <text x="45" y="58" fill="var(--color-elnino)" fontSize="10" fontFamily="var(--font-body)">+0,5 °C Ambang El Niño</text>

              <line x1="40" y1="110" x2="490" y2="110" stroke="var(--color-rule-2)" strokeWidth="1" />
              <text x="45" y="105" fill="var(--color-muted)" fontSize="10" fontFamily="var(--font-body)">0,0 °C Netral</text>

              <line x1="40" y1="155" x2="490" y2="155" stroke="var(--color-lanina)" strokeWidth="1" strokeDasharray="4 4" />
              <text x="45" y="168" fill="var(--color-lanina)" fontSize="10" fontFamily="var(--font-body)">-0,5 °C Ambang La Niña</text>

              {/* Garis observasi masa lalu */}
              <path d="M40 135 L 100 125 L 160 115 L 220 95" stroke="var(--color-ink)" strokeWidth="2.5" fill="none" />
              <circle cx="220" cy="95" r="4" fill="var(--color-ink)" />

              {/* Anggota ensemble IRI */}
              <path d="M220 95 Q 320 80 480 60" stroke="var(--color-muted)" strokeWidth="1" opacity="0.4" fill="none" />
              <path d="M220 95 Q 330 90 480 75" stroke="var(--color-muted)" strokeWidth="1" opacity="0.4" fill="none" />
              <path d="M220 95 Q 340 70 480 50" stroke="var(--color-muted)" strokeWidth="1" opacity="0.4" fill="none" />

              {/* Rata-rata KMRV model */}
              <path d="M220 95 Q 340 65 480 48" stroke="var(--color-kmrv-model)" strokeWidth="3" fill="none" />
              <circle cx="480" cy="48" r="5" fill="var(--color-kmrv-model)" />
              <text x="410" y="40" fill="var(--color-kmrv-model)" fontSize="11" fontWeight="600" fontFamily="var(--font-body)">KMRV Proyeksi</text>
            </svg>
          </div>
        </section>

        {/* Matriks Korelasi Skill per Musim */}
        <section className="data-card">
          <div className="card-header">
            <h2 className="card-title">Stabilitas Akurasi & Pengaruh Spring Predictability Barrier</h2>
            <p className="card-meta">
              Nilai Correlation Coefficient (ACC) mendekati 1,00 menandakan kemampuan prediksi tinggi. MAM menunjukkan penurunan wajar akibat barrier musim semi.
            </p>
          </div>

          <div style={{ display: 'flex', flexDirection: 'column', gap: 'var(--space-xs)' }}>
            <div style={{ display: 'grid', gridTemplateColumns: '120px repeat(4, 1fr) 60px', fontSize: 'var(--text-xs)', fontWeight: 600, color: 'var(--color-muted)', paddingBottom: 'var(--space-2xs)', borderBottom: 'var(--rule-hair) solid var(--color-rule)' }}>
              <span>Horizon</span>
              <span style={{ textAlign: 'center' }}>DJF</span>
              <span style={{ textAlign: 'center' }}>MAM</span>
              <span style={{ textAlign: 'center' }}>JJA</span>
              <span style={{ textAlign: 'center' }}>SON</span>
              <span style={{ textAlign: 'right' }}>Rerata</span>
            </div>

            {skillMatrix.map((item) => (
              <div
                key={item.lead}
                style={{
                  display: 'grid',
                  gridTemplateColumns: '120px repeat(4, 1fr) 60px',
                  alignItems: 'center',
                  fontSize: 'var(--text-xs)',
                  paddingBlock: 'var(--space-xs)',
                  borderBottom: 'var(--rule-hair) solid var(--color-rule-2)'
                }}
              >
                <span style={{ fontWeight: 600, color: 'var(--color-ink)' }}>{item.lead}</span>
                <span style={{ textAlign: 'center', fontFamily: 'var(--font-outlier)' }}>{item.djf.toFixed(2)}</span>
                <span style={{ textAlign: 'center', fontFamily: 'var(--font-outlier)', color: item.mam < 0.7 ? 'var(--color-elnino)' : 'inherit' }}>{item.mam.toFixed(2)}</span>
                <span style={{ textAlign: 'center', fontFamily: 'var(--font-outlier)' }}>{item.jja.toFixed(2)}</span>
                <span style={{ textAlign: 'center', fontFamily: 'var(--font-outlier)' }}>{item.son.toFixed(2)}</span>
                <span style={{ textAlign: 'right', fontFamily: 'var(--font-outlier)', fontWeight: 600, color: 'var(--color-kmrv-model)' }}>{item.avg.toFixed(2)}</span>
              </div>
            ))}
          </div>
        </section>

      </div>

    </div>
  );
}
