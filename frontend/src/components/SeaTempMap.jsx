import React from 'react';
import { INDONESIA_PATH, MAP_VIEWBOX, projectPoint } from '../data/indonesiaShape';
import { num } from '../utils/format';
import { sstColor } from '../utils/sstScale';

// Titik lima domain pengukuran (lon, lat) + penempatan label rapi
const DOMAINS = {
  nino34: { lon: 152.5, lat: 0, dx: -20, dy: -36 },
  karimata: { lon: 107.5, lat: -0.5, dx: -35, dy: -42 },
  makassar: { lon: 118, lat: -1.5, dx: 24, dy: -26 },
  jawa: { lon: 110, lat: -9.5, dx: 0, dy: 24 },
  maluku: { lon: 132.5, lat: 0, dx: 20, dy: -36 },
};

export default function SeaTempMap({ regions = [], variant = 'heatmap' }) {
  const { width, height } = MAP_VIEWBOX;

  // Varian hero: peta Indonesia minimalis elegan di atas latar putih bersih (kontras lembut)
  if (variant === 'hero') {
    return (
      <svg
        viewBox={`0 0 ${width} ${height}`}
        preserveAspectRatio="xMidYMid meet"
        className="hero-map-svg"
        aria-hidden="true"
        focusable="false"
      >
        <rect width={width} height={height} fill="#ffffff" rx="16" />
        <path
          className="hero-map-land"
          d={INDONESIA_PATH}
          fill="#f8fafc"
          stroke="#cbd5e1"
          strokeWidth="0.8"
        />
        {Object.values(DOMAINS).map((d, i) => {
          const pt = projectPoint(d.lon, d.lat);
          return (
            <g key={`hero-pt-${i}`}>
              <circle cx={pt.x} cy={pt.y} r="18" fill="#0284c7" fillOpacity="0.04" stroke="#0284c7" strokeWidth="0.5" strokeDasharray="2 2" />
              <circle cx={pt.x} cy={pt.y} r="4" fill="#ffffff" stroke="#0284c7" strokeWidth="1.5" />
              <circle cx={pt.x} cy={pt.y} r="1.5" fill="#0284c7" />
            </g>
          );
        })}
      </svg>
    );
  }

  const domains = regions
    .filter((region) => DOMAINS[region.key])
    .map((region) => ({
      ...region,
      ...DOMAINS[region.key],
      point: projectPoint(DOMAINS[region.key].lon, DOMAINS[region.key].lat),
    }));

  return (
    <div className="sea-map geo-card-map">
      <div className="map-badge-overlay">
        <span className="map-badge-dot" />
        <span>5 Domain Pengamatan Maritim</span>
      </div>

      <div className="map-controls-overlay" aria-hidden="true">
        <button type="button" tabIndex={-1}>+</button>
        <button type="button" tabIndex={-1}>−</button>
      </div>

      <svg
        viewBox={`0 0 ${width} ${height}`}
        className="sea-map-svg"
        role="img"
        aria-label="Peta suhu permukaan laut dan anomali di lima domain perairan Indonesia"
      >
        {/* Air laut bersih gaya GeoAether */}
        <rect width={width} height={height} fill="#eef6fc" rx="14" />

        {/* Zona panas / radar konsentris halus tiap domain */}
        {domains.map((domain) => {
          const color = sstColor(domain.sst);
          return (
            <g key={`radar-${domain.key}`}>
              <circle
                cx={domain.point.x}
                cy={domain.point.y}
                r="46"
                fill={color}
                fillOpacity="0.08"
                stroke={color}
                strokeWidth="0.75"
                strokeDasharray="3 3"
                strokeOpacity="0.35"
              />
              <circle
                cx={domain.point.x}
                cy={domain.point.y}
                r="24"
                fill={color}
                fillOpacity="0.2"
                stroke={color}
                strokeWidth="1"
                strokeOpacity="0.6"
              />
            </g>
          );
        })}

        {/* Kepulauan Indonesia (Daratan Putih Bersih dengan Garis Halus) */}
        <path
          className="sea-map-land"
          d={INDONESIA_PATH}
          fill="#ffffff"
          stroke="#94a3b8"
          strokeWidth="0.75"
          strokeLinejoin="round"
        />

        {/* Pin Titik Pengamatan */}
        {domains.map((domain) => {
          const color = sstColor(domain.sst);
          return (
            <g key={`pin-${domain.key}`}>
              <circle
                cx={domain.point.x}
                cy={domain.point.y}
                r="6.5"
                fill="#ffffff"
                stroke="#64748b"
                strokeWidth="1.2"
              />
              <circle
                cx={domain.point.x}
                cy={domain.point.y}
                r="3.5"
                fill={color}
              />
            </g>
          );
        })}
      </svg>

      {/* Floating Labels / Station Tooltips */}
      <div className="sea-map-labels">
        {domains.map((domain) => (
          <span
            key={domain.key}
            className="sea-label"
            style={{
              left: `${(domain.point.x / width) * 100}%`,
              top: `${(domain.point.y / height) * 100}%`,
              '--dx': `${domain.dx}px`,
              '--dy': `${domain.dy}px`,
            }}
          >
            <span className="sea-label-value font-mono">{num(domain.sst, 1)} °C</span>
            <span className="sea-label-name">{domain.name}</span>
          </span>
        ))}
      </div>
    </div>
  );
}
