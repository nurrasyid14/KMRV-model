import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

export default function SSTMap({ regions, selectedRegion, onSelectRegion }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const layersRef = useRef({});

  useEffect(() => {
    if (!mapContainerRef.current) return;
    if (mapInstanceRef.current) return;

    // Inisialisasi peta Leaflet terpusat di perairan maritim Indonesia & barat Pasifik
    const map = L.map(mapContainerRef.current, {
      center: [-2.0, 122.0],
      zoom: 4,
      minZoom: 3,
      maxZoom: 9,
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true
    });

    // CartoDB Dark Matter - tiles gelap untuk telemetri malam
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
      maxZoom: 19,
      subdomains: 'abcd',
      attribution: '&copy; OpenStreetMap &copy; CARTO'
    }).addTo(map);

    // Bounding box 5 domain laut riset KMRV
    const domainBounds = {
      'Pasifik Niño 3.4': {
        bounds: [[-5, 145], [5, 160]], // Representasi proyeksi Pasifik barat ekuator pada fokus viewport
        displayBounds: [[-5, -170], [5, -120]],
        center: [0, 152.5],
        desc: 'Domain indeks rujukan global ENSO'
      },
      'Selat Makassar': {
        bounds: [[-5, 116], [2, 120]],
        center: [-1.5, 118],
        desc: 'Jalur utama Arlindo & retensi panas laut'
      },
      'Selat Karimata': {
        bounds: [[-3, 105], [2, 110]],
        center: [-0.5, 107.5],
        desc: 'Penghubung perairan dangkal paparan Sunda'
      },
      'Selatan Jawa': {
        bounds: [[-12, 105], [-8, 115]],
        center: [-10, 110],
        desc: 'Zona upwelling musiman & respon IOD'
      },
      'Maluku-Papua': {
        bounds: [[-3, 125], [3, 140]],
        center: [0, 132.5],
        desc: 'Kolam hangat Pasifik barat & konveksi aktif'
      }
    };

    const newLayers = {};

    regions.forEach((reg) => {
      const config = domainBounds[reg.name];
      if (!config) return;

      const isSelected = selectedRegion === reg.name;
      const isPositive = reg.num > 0;
      const strokeColor = isPositive ? 'var(--color-elnino)' : 'var(--color-lanina)';

      // Poligon kotak koordinat
      const polygon = L.rectangle(config.bounds, {
        color: strokeColor,
        weight: isSelected ? 2.5 : 1.5,
        fillColor: strokeColor,
        fillOpacity: isSelected ? 0.35 : 0.18,
        dashArray: reg.name.includes('Niño') ? '4, 4' : null
      }).addTo(map);

      // Label penanda teks di pusat wilayah
      const marker = L.circleMarker(config.center, {
        radius: isSelected ? 7 : 5,
        color: strokeColor,
        fillColor: 'var(--color-cotton)',
        fillOpacity: 1,
        weight: 2
      }).addTo(map);

      // Tooltip data instrumen
      const tooltipContent = `
        <div style="font-family: var(--font-body); font-size: var(--text-xs); line-height: 1.4; color: var(--color-ink);">
          <strong style="display: block; font-size: var(--text-sm); font-weight: 600;">${reg.name}</strong>
          <div>Anomali SST: <strong style="font-family: var(--font-outlier); color: ${strokeColor};">${reg.value} °C</strong></div>
          <div style="color: var(--color-muted); font-size: 11px;">${config.desc}</div>
        </div>
      `;

      polygon.bindTooltip(tooltipContent, { permanent: false, direction: 'top' });
      marker.bindTooltip(tooltipContent, { permanent: false, direction: 'top' });

      const handleClick = () => {
        onSelectRegion(reg.name);
      };

      polygon.on('click', handleClick);
      marker.on('click', handleClick);

      newLayers[reg.name] = { polygon, marker, config };
    });

    layersRef.current = newLayers;
    mapInstanceRef.current = map;

    return () => {
      map.remove();
      mapInstanceRef.current = null;
    };
  }, [regions]);

  // Efek perubahan selectedRegion untuk update style poligon
  useEffect(() => {
    if (!layersRef.current) return;

    Object.entries(layersRef.current).forEach(([name, item]) => {
      const isSelected = selectedRegion === name;
      const reg = regions.find(r => r.name === name);
      const isPositive = reg ? reg.num > 0 : true;
      const strokeColor = isPositive ? 'var(--color-elnino)' : 'var(--color-lanina)';

      item.polygon.setStyle({
        weight: isSelected ? 2.5 : 1.5,
        fillOpacity: isSelected ? 0.38 : 0.16,
        color: strokeColor
      });

      item.marker.setRadius(isSelected ? 8 : 5);

      if (isSelected && mapInstanceRef.current && item.config) {
        mapInstanceRef.current.panTo(item.config.center, { animate: true, duration: 0.6 });
      }
    });
  }, [selectedRegion, regions]);

  return (
    <div className="map-wrapper" aria-label="Peta telemetri anomali suhu permukaan laut">
      <div className="map-header">
        <div className="map-legend">
          <span className="legend-item">
            <span className="legend-indicator elnino" aria-hidden="true"></span>
            Anomali hangat (&gt; +0,5 °C El Niño)
          </span>
          <span className="legend-item">
            <span className="legend-indicator neutral" aria-hidden="true"></span>
            Kondisi netral (±0,5 °C)
          </span>
          <span className="legend-item">
            <span className="legend-indicator lanina" aria-hidden="true"></span>
            Anomali dingin (&lt; -0,5 °C La Niña)
          </span>
        </div>
        <div className="map-hint">Klik wilayah di peta untuk fokus analisis</div>
      </div>
      <div ref={mapContainerRef} className="map-canvas" style={{ minHeight: '360px', width: '100%' }}></div>
    </div>
  );
}
