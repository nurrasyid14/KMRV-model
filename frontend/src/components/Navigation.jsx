import React from 'react';

export default function Navigation({ activeTab, setActiveTab }) {
  const tabs = [
    { id: 'ringkasan', label: 'Ringkasan prediksi & peluang' },
    { id: 'laut', label: 'Peta telemetri suhu laut' },
    { id: 'dampak', label: 'Dampak kekeringan & rekomendasi' },
    { id: 'kepercayaan', label: 'Evaluasi & akurasi model' },
    { id: 'metode', label: 'Metodologi & batasan' }
  ];

  return (
    <nav className="tab-dock" role="tablist" aria-label="Navigasi instrumen analisis ENSO">
      {tabs.map((tab) => {
        const isActive = activeTab === tab.id;
        return (
          <button
            key={tab.id}
            role="tab"
            aria-selected={isActive}
            tabIndex={isActive ? 0 : -1}
            type="button"
            className={`tab-anchor ${isActive ? 'is-active' : ''}`}
            onClick={() => setActiveTab(tab.id)}
          >
            {tab.label}
          </button>
        );
      })}
    </nav>
  );
}
