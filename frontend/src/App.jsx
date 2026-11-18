import React, { useState } from 'react';
import Sidebar from './components/Sidebar';
import Dashboard from './pages/Dashboard';

export default function App() {
  const [selectedRegion, setSelectedRegion] = useState('Selat Makassar');

  return (
    <div className="dashboard-fullscreen-layout">
      <a className="skip-link" href="#main-content">Lompat ke konten</a>

      <Sidebar />

      <div className="dashboard-main-area">
        <main id="main-content" className="dashboard-page-container lp-shell" tabIndex={-1}>
          <Dashboard
            selectedRegion={selectedRegion}
            setSelectedRegion={setSelectedRegion}
          />
        </main>
      </div>
    </div>
  );
}
