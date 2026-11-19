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
            <span className="brand-dot-logo">
              <span className="dot-inner" />
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
