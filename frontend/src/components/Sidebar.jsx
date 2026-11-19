import React from 'react';

const navItems = [
  { href: '#awal', label: 'Awal' },
  { href: '#suhu-laut', label: 'Suhu laut' },
  { href: '#laut', label: 'ONI' },
  { href: '#prediksi', label: 'Prediksi' },
  { href: '#model', label: 'Evaluasi' }
];

export default function Sidebar() {
  return (
    <header className="app-bar" role="banner">
      <div className="app-bar-inner">
        <div className="app-brand">
          <button
            type="button"
            className="app-brand-link"
            onClick={() => window.scrollTo({ top: 0, behavior: 'smooth' })}
            aria-label="lautan.id, kembali ke atas"
          >
            <span className="brand-dot-logo" style={{ display: 'inline-flex', alignItems: 'center', justifyContent: 'center', width: 28, height: 28, background: '#1c382a', borderRadius: 6 }}>
              <svg viewBox="0 0 256 256" width="18" height="18" fill="none" aria-hidden="true">
                <path
                  d="M 38,154 C 52,94 100,56 162,64 C 198,68 222,94 226,116 C 214,106 190,92 154,90 C 114,88 80,112 62,154 C 54,172 34,172 38,154 Z"
                  fill="#C9F26B"
                />
                <path
                  d="M 218,102 C 204,162 156,200 94,192 C 58,188 34,162 30,140 C 42,150 66,164 102,166 C 142,168 176,144 194,102 C 202,84 222,84 218,102 Z"
                  fill="#FFFFFF"
                />
              </svg>
            </span>
            <span className="app-brand-name">
              <strong>lautan</strong>.id
            </span>
          </button>
        </div>

        <nav className="app-nav-links" aria-label="Bagian dashboard">
          {navItems.map((item) => (
            <a key={item.href} href={item.href} className="app-link-tab">
              {item.label}
            </a>
          ))}
        </nav>
      </div>
    </header>
  );
}
