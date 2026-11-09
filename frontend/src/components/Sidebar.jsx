import React from 'react';

const navItems = [
  { id: 'ringkasan', label: 'Ringkasan' },
  { id: 'prakiraan', label: 'ENSO & Prakiraan' },
  { id: 'laut', label: 'Laut Indonesia' },
  { id: 'dampak', label: 'Dampak Hujan' },
  { id: 'metode', label: 'Kualitas & Metode', isAnalystOnly: true },
  { id: 'glosarium', label: 'Glosarium' }
];

export default function Sidebar({ activeTab, setActiveTab, onOpenLanding }) {
  return (
    <header className="app-bar" role="banner">
      <div className="app-bar-inner">
        <div className="app-brand">
          <button
            type="button"
            className="app-brand-link"
            onClick={onOpenLanding}
            aria-label="KMRV, kembali ke halaman depan"
          >
            <span className="app-brand-mark" aria-hidden="true">
              <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.6" strokeLinecap="round" strokeLinejoin="round">
                <line x1="3" y1="16.5" x2="21" y2="16.5" strokeDasharray="2 2" opacity="0.55" />
                <path d="M3.5 18 C 5.5 15.8 7.1 17.4 8.9 15.6 C 11.1 13.4 11.9 11 13.9 9 C 15.5 7.4 16.7 6.4 18.3 4.9" />
                <circle cx="19.2" cy="4.2" r="1.8" fill="currentColor" stroke="none" />
              </svg>
            </span>
            <span className="app-brand-name">KMRV</span>
          </button>
          <span className="app-brand-sub">Stasiun pantau ENSO maritim</span>
        </div>

        <nav className="app-nav" role="tablist" aria-label="Menu instrumen iklim">
          {navItems.map((item) => {
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                type="button"
                role="tab"
                aria-selected={isActive}
                tabIndex={isActive ? 0 : -1}
                className="app-nav-tab"
                onClick={() => setActiveTab(item.id)}
              >
                {item.label}
                {item.isAnalystOnly && (
                  <span className="app-nav-flag" title="Halaman teknis untuk analis">Analis</span>
                )}
              </button>
            );
          })}
        </nav>

        <div className="app-bar-actions">
          <button type="button" className="app-bar-link" onClick={onOpenLanding}>
            Halaman depan
          </button>
        </div>
      </div>
    </header>
  );
}
