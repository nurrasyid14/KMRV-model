import React from 'react';

export default function FooterNotes() {
  return (
    <footer className="footer-dock">
      <div className="footer-grid">
        <div className="footer-col">
          <span className="footer-col-title">Interpretasi indeks iklim</span>
          <p className="footer-col-desc">
            Relative Oceanic Niño Index (RONI) mengukur anomali SST Niño 3.4 relatif terhadap rata-rata perairan tropis.
            Nilai melampaui +0,5 °C selama lima periode 3-bulanan berturut-turut merupakan definisi operasional El Niño.
          </p>
        </div>

        <div className="footer-col">
          <span className="footer-col-title">Pembeda ENSO dan marine heatwave</span>
          <p className="footer-col-desc">
            Ambang ±0,5 °C berlaku untuk klasifikasi skala cekungan Pasifik. Marine Heatwave (MHW) perairan lokal
            dihitung berdasarkan suhu harian melampaui persentil ke-90 klimatologi musiman setempat selama minimal lima hari.
          </p>
        </div>

        <div className="footer-col">
          <span className="footer-col-title">Rujukan & integritas data</span>
          <p className="footer-col-desc">
            Data telemetri diolah dari NOAA Daily OISST v2.1 (resolusi grid 0,25°) dan indeks CPC. Seluruh proyeksi
            bersifat probabilistik untuk mendukung pengambilan keputusan dini BMKG, BPBD, dan Kementerian Pertanian.
          </p>
        </div>
      </div>
    </footer>
  );
}
