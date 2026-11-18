// Skala warna suhu permukaan laut (°C), dari dingin ke hangat.
const SST_STOPS = [
  [26.0, '#1d4ed8'],
  [27.0, '#0284c7'],
  [27.6, '#06b6d4'],
  [28.2, '#10b981'],
  [28.8, '#a3e635'],
  [29.4, '#facc15'],
  [30.0, '#fb923c'],
  [30.8, '#dc2626'],
];

function hexToRgb(hex) {
  const value = parseInt(hex.slice(1), 16);
  return [(value >> 16) & 255, (value >> 8) & 255, value & 255];
}

export function sstColor(value) {
  const min = SST_STOPS[0][0];
  const max = SST_STOPS[SST_STOPS.length - 1][0];
  const clamped = Math.min(Math.max(value, min), max);

  for (let i = 1; i < SST_STOPS.length; i += 1) {
    const [upperValue, upperColor] = SST_STOPS[i];
    if (clamped <= upperValue) {
      const [lowerValue, lowerColor] = SST_STOPS[i - 1];
      const t = (clamped - lowerValue) / (upperValue - lowerValue);
      const from = hexToRgb(lowerColor);
      const to = hexToRgb(upperColor);
      return `rgb(${from.map((channel, index) => Math.round(channel + (to[index] - channel) * t)).join(', ')})`;
    }
  }

  return SST_STOPS[SST_STOPS.length - 1][1];
}
