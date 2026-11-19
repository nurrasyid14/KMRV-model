export function num(value, digits = 2) {
  return Number(value).toFixed(digits).replace('.', ',');
}

export function signed(value, digits = 2) {
  if (Math.abs(value) < 0.0001) return num(0, digits);
  const text = num(Math.abs(value), digits);
  return value > 0 ? `+${text}` : `−${text}`;
}

export function phaseLabel(phase) {
  if (phase === 'El Nino') return 'El Niño';
  if (phase === 'La Nina') return 'La Niña';
  return phase;
}

const MONTHS = [
  'Januari', 'Februari', 'Maret', 'April', 'Mei', 'Juni',
  'Juli', 'Agustus', 'September', 'Oktober', 'November', 'Desember'
];

export function monthLabel(value) {
  const [year, month] = value.split('-');
  return `${MONTHS[Number(month) - 1]} ${year}`;
}

export function shortMonth(value) {
  const [year, month] = value.split('-');
  return `${MONTHS[Number(month) - 1].slice(0, 3)} ${year}`;
}
