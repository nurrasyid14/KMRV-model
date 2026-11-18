import React, { useEffect, useRef } from 'react';
import L from 'leaflet';

function formatAnomaly(value) {
  const abs = Math.abs(value).toFixed(2).replace('.', ',');
  return `${value > 0 ? '+' : value < 0 ? '−' : ''}${abs}`;
}

function createBeaconIcon(anomaly, isPositive, isSelected) {
  const color = isPositive ? '#ea580c' : '#0284c7';
  return L.divIcon({
    className: 'custom-map-beacon',
    html: `
      <div class="beacon-wrap ${isSelected ? 'is-selected' : ''}" style="--beacon-color: ${color};">
        <span class="beacon-ripple"></span>
        <span class="beacon-dot"></span>
        <span class="beacon-badge font-mono">${formatAnomaly(anomaly)} °C</span>
      </div>
    `,
    iconSize: [84, 42],
    iconAnchor: [42, 21]
  });
}

const DOMAIN_CONFIGS = {
  'Pasifik Niño 3.4': { center: [0, 152.5], desc: 'Domain indeks rujukan global ENSO' },
  'Selat Makassar': { center: [-1.5, 118], desc: 'Jalur utama Arlindo dan retensi panas laut' },
  'Selat Karimata': { center: [-0.5, 107.5], desc: 'Perairan dangkal paparan Sunda' },
  'Selatan Jawa': { center: [-9.5, 110], desc: 'Zona upwelling musiman dan respons IOD' },
  'Maluku-Papua': { center: [0, 132.5], desc: 'Kolam hangat Pasifik barat' }
};

export default function SSTMap({ regions, selectedRegion, onSelectRegion }) {
  const mapContainerRef = useRef(null);
  const mapInstanceRef = useRef(null);
  const markersRef = useRef({});
  const lastSelectedRef = useRef(selectedRegion);

  useEffect(() => {
    if (!mapContainerRef.current || mapInstanceRef.current) return;

    const map = L.map(mapContainerRef.current, {
      center: [-1.5, 126.5],
      zoom: 4,
      minZoom: 3,
      maxZoom: 9,
      scrollWheelZoom: false,
      zoomControl: true,
      attributionControl: true,
      fadeAnimation: false
    });

    L.tileLayer('https://server.arcgisonline.com/ArcGIS/rest/services/World_Street_Map/MapServer/tile/{z}/{y}/{x}', {
      maxZoom: 18,
      attribution: 'Tiles &copy; Esri'
    }).addTo(map);

    const markers = {};
    regions.forEach((region) => {
      const config = DOMAIN_CONFIGS[region.name];
      if (!config) return;

      const isSelected = selectedRegion === region.name;
      const marker = L.marker(
        config.center,
        { icon: createBeaconIcon(region.anomaly, region.anomaly >= 0, isSelected) }
      ).addTo(map);

      const tooltipContent = `
        <div style="font-family: var(--font-display); font-size: 12px; line-height: 1.4; color: #0f172a; padding: 2px 4px;">
          <strong style="display: block; font-size: 13px; font-weight: 700;">${region.name}</strong>
          <div>Anomali SST: <strong style="font-family: var(--font-outlier); color: #0284c7; font-weight: 700;">${formatAnomaly(region.anomaly)} °C</strong></div>
          <div style="color: #64748b; font-size: 11px;">${config.desc}</div>
        </div>
      `;

      marker.bindTooltip(tooltipContent, { permanent: false, direction: 'top' });
      marker.on('click', () => onSelectRegion(region.name));

      markers[region.name] = { marker, config, isPositive: region.anomaly >= 0 };
    });

    markersRef.current = markers;
    mapInstanceRef.current = map;

    const container = mapContainerRef.current;
    const resizeObserver = new ResizeObserver(() => map.invalidateSize());
    resizeObserver.observe(container);
    requestAnimationFrame(() => map.invalidateSize());

    return () => {
      resizeObserver.disconnect();
      map.remove();
      mapInstanceRef.current = null;
    };
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  useEffect(() => {
    if (!mapInstanceRef.current) return;

    Object.entries(markersRef.current).forEach(([name, data]) => {
      const region = regions.find((item) => item.name === name);
      const isSelected = selectedRegion === name;
      const anomaly = region ? region.anomaly : 0;

      data.marker.setIcon(createBeaconIcon(anomaly, anomaly >= 0, isSelected));
    });

    if (lastSelectedRef.current === selectedRegion) return;
    lastSelectedRef.current = selectedRegion;

    const config = DOMAIN_CONFIGS[selectedRegion];
    if (config) {
      mapInstanceRef.current.panTo(config.center, { animate: true, duration: 0.6 });
    }
  }, [selectedRegion, regions]);

  return (
    <div className="map-wrapper">
      <div ref={mapContainerRef} className="map-canvas" style={{ width: '100%', height: '100%' }} />
    </div>
  );
}
