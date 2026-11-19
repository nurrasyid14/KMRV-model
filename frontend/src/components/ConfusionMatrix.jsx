import React from 'react';

const LABELS = ['La Niña', 'Netral', 'El Niño'];

export default function ConfusionMatrix({ matrix, showSummary = true }) {
  const max = Math.max(...matrix.flat(), 1);
  const total = matrix.flat().reduce((a, b) => a + b, 0);
  const correct = matrix.reduce((sum, row, i) => sum + row[i], 0);
  const accuracyPct = total > 0 ? Math.round((correct / total) * 100) : 0;

  return (
    <div className="cm-wrapper">
      {/* Label arah sumbu kolom */}
      <div className="cm-top-axis">
        <span className="cm-axis-hint">Tebakan Model →</span>
      </div>

      <div className="cm-body-row">
        {/* Label arah sumbu baris */}
        <div className="cm-left-axis">
          <span className="cm-axis-hint cm-axis-hint--vertical">Kondisi Sebenarnya ↓</span>
        </div>

        <div className="cm-grid" role="table" aria-label="Confusion matrix fase ENSO">
          <span className="cm-axis cm-corner" aria-hidden="true" />
          {LABELS.map((label) => (
            <span key={label} className="cm-axis cm-axis--col">{label}</span>
          ))}

          {matrix.map((row, rowIndex) => (
            <React.Fragment key={LABELS[rowIndex]}>
              <span className="cm-axis cm-axis--row">{LABELS[rowIndex]}</span>
              {row.map((value, colIndex) => {
                const isDiag = rowIndex === colIndex;
                const isCorrect = isDiag && value > 0;
                const isMiss = !isDiag && value > 0;

                return (
                  <span
                    key={`${rowIndex}-${colIndex}`}
                    className={`cm-cell ${isDiag ? 'is-diag' : ''} ${isCorrect ? 'is-hit' : ''} ${isMiss ? 'is-miss' : ''}`}
                    style={{
                      backgroundColor: isDiag
                        ? value > 0 ? 'rgba(34, 197, 94, 0.14)' : '#f8fafc'
                        : value > 0 ? 'rgba(239, 68, 68, 0.1)' : '#f8fafc'
                    }}
                  >
                    <span className="cm-num font-mono">{value}</span>
                    {isDiag && (
                      <span className={`cm-diag-tag ${value > 0 ? 'is-good' : 'is-zero'}`}>
                        {value > 0 ? '✓ Tepat' : '0 tepat'}
                      </span>
                    )}
                    {!isDiag && value > 0 && (
                      <span className="cm-miss-tag">Salah</span>
                    )}
                  </span>
                );
              })}
            </React.Fragment>
          ))}
        </div>
      </div>

      {showSummary && (
        <div className="cm-summary-bar">
          <span className={`cm-summary-badge ${correct > 0 ? 'is-good' : 'is-poor'}`}>
            Tebakan benar: <strong>{correct}</strong> dari <strong>{total}</strong> bulan ({accuracyPct}%)
          </span>
        </div>
      )}
    </div>
  );
}
