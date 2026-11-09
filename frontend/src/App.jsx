import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import FooterNotes from './components/FooterNotes';
import LandingPage from './pages/LandingPage';
import Ringkasan from './pages/Ringkasan';
import PrakiraanENSO from './pages/PrakiraanENSO';
import Laut from './pages/Laut';
import DampakIndonesia from './pages/DampakIndonesia';
import Metode from './pages/Metode';
import Glosarium from './pages/Glosarium';

export default function App() {
  const [viewMode, setViewMode] = useState('landing');
  const [activeTab, setActiveTab] = useState('ringkasan');
  const [isAnalystMode, setIsAnalystMode] = useState(false);
  const [selectedRegion, setSelectedRegion] = useState('Selat Makassar');
  const [selectedLead, setSelectedLead] = useState('3 bulan');

  // Sinkronisasi dengan URL hash jika user bookmark
  useEffect(() => {
    const handleHashChange = () => {
      const hash = window.location.hash;
      if (hash === '#dashboard') {
        setViewMode('dashboard');
      } else if (hash === '#landing' || hash === '') {
        setViewMode('landing');
      }
    };

    handleHashChange();
    window.addEventListener('hashchange', handleHashChange);
    return () => window.removeEventListener('hashchange', handleHashChange);
  }, []);

  const openDashboard = (tab = 'ringkasan') => {
    setActiveTab(tab);
    window.location.hash = '#dashboard';
    setViewMode('dashboard');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const openLanding = () => {
    window.location.hash = '#landing';
    setViewMode('landing');
    window.scrollTo({ top: 0, behavior: 'smooth' });
  };

  const renderActivePage = () => {
    switch (activeTab) {
      case 'ringkasan':
        return (
          <Ringkasan
            selectedRegion={selectedRegion}
            setSelectedRegion={setSelectedRegion}
            selectedLead={selectedLead}
            isAnalystMode={isAnalystMode}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        );
      case 'prakiraan':
        return (
          <PrakiraanENSO
            selectedLead={selectedLead}
            setSelectedLead={setSelectedLead}
            isAnalystMode={isAnalystMode}
          />
        );
      case 'laut':
        return (
          <Laut
            selectedRegion={selectedRegion}
            setSelectedRegion={setSelectedRegion}
            isAnalystMode={isAnalystMode}
          />
        );
      case 'dampak':
        return <DampakIndonesia isAnalystMode={isAnalystMode} />;
      case 'metode':
        return <Metode isAnalystMode={isAnalystMode} />;
      case 'glosarium':
        return <Glosarium isAnalystMode={isAnalystMode} />;
      default:
        return (
          <Ringkasan
            selectedRegion={selectedRegion}
            setSelectedRegion={setSelectedRegion}
            selectedLead={selectedLead}
            isAnalystMode={isAnalystMode}
            onNavigateTab={(tab) => setActiveTab(tab)}
          />
        );
    }
  };

  if (viewMode === 'landing') {
    return <LandingPage onOpenDashboard={openDashboard} />;
  }

  return (
    <div className="dashboard-app-layout">
      <a className="skip-link" href="#main-content">Lompat ke konten</a>

      {/* Bilah instrumen atas */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        onOpenLanding={openLanding}
      />

      {/* Area Konten Utama */}
      <div className="dashboard-main-area">
        <Header
          isAnalystMode={isAnalystMode}
          setIsAnalystMode={setIsAnalystMode}
          selectedRegion={selectedRegion}
          setSelectedRegion={setSelectedRegion}
          selectedLead={selectedLead}
          setSelectedLead={setSelectedLead}
        />

        <main id="main-content" className="dashboard-page-container" tabIndex={-1}>
          {renderActivePage()}
        </main>

        <FooterNotes />
      </div>
    </div>
  );
}
