# Lautan.id — Logo & Brand Guidelines

Panduan ringkas identitas visual resmi Lautan.id (Intelijen Iklim Maritim Indonesia).

---

## 1. Identitas & Konsep Desain

- **Nama Mark:** Arus Nusantara (*Abstract Oceanic Dynamic*)
- **Filosofi:** Dua aliran massa air dinamis berpadu membentuk dinamika siklus osilasi iklim ENSO (El Niño & La Niña) dan sirkulasi Arlindo (*Indonesian Throughflow*).
- **Varian Utama:**
  - **Horizontal Lockup:** Symbol + `Lautan.id` (standar header web & media digital)
  - **Symbol Only:** Standar favicon, app icon, avatar media sosial
  - **Stacked Lockup:** Format vertikal untuk kartu, merchandise, dan signage
  - **Wordmark Only:** Untuk format ultra-lebar atau penempatan tipografi murni

---

## 2. Struktur File Master (`brand/`)

| File | Tipe | Deskripsi & Penggunaan |
|---|---|---|
| `brand/lautan-symbol.svg` | SVG Master | Mark 256×256 solid `#1C382A` |
| `brand/lautan-horizontal.svg` | SVG Lockup | Horizontal light: symbol `#1C382A` + `.id` `#0E7490` |
| `brand/lautan-horizontal-dark.svg` | SVG Lockup | Horizontal dark: white text + lime accent `#C9F26B` |
| `brand/lautan-stacked.svg` | SVG Lockup | Stacked centered format |
| `brand/lautan-wordmark.svg` | SVG Tipografi | Wordmark vektor murni (tanpa tag `<text>`) |
| `brand/lautan-symbol-app-icon.svg` | SVG App Icon | Ikon app tile sudut tumpul |
| `brand/favicon.ico` | ICO (16/32/48) | Favicon browser multi-resolusi |
| `brand/favicon.svg` | SVG Tab | Favicon vektor modern |
| `brand/apple-touch-icon.png` | PNG (180px) | Ikon iOS Home Screen |
| `brand/icon-192.png` & `512.png` | PNG PWA | Ikon Progressive Web App |
| `brand/site.webmanifest` | JSON Manifest | Manifest web & PWA |
| `brand/presentation.html` | Interactive Deck | Presentasi visual merek lengkap 5 slide |
| `brand/slides/slide-01..05.png` | PNG Slides | Render mockup (README, App Icon, Web, Terminal) |

---

## 3. Clear Space & Batas Aman

- Pertahankan zona aman minimum **1× X** di sekeliling logo, dengan **X** = tinggi kurva eye mark.
- Jangan meletakkan teks, garis pemisah, atau elemen grafis lain di dalam zona aman ini.

---

## 4. Ukuran Minimum

| Varian | Layar Digital | Cetak / Print |
|---|---|---|
| Horizontal Lockup | 96 px lebar | 28 mm lebar |
| Symbol Mark | 16 px (gunakan `favicon.svg` / `-small`) | 6 mm tinggi |
| Stacked Lockup | 80 px lebar | 24 mm lebar |

---

## 5. Sistem Warna Resmi

| Peran | Nama Warna | HEX | RGB | CMYK | Pantone Eq. |
|---|---|---|---|---|---|
| **Primary** | Maritime Forest Green | `#1C382A` | `rgb(28, 56, 42)` | `C80 M45 Y75 K60` | `Pantone 5605 C` |
| **Accent** | Dynamic Neo Lime | `#C9F26B` | `rgb(201, 242, 107)` | `C25 M0 Y75 K0` | `Pantone 2297 C` |
| **Secondary** | Deep Oceanic Teal | `#0E7490` | `rgb(14, 116, 144)` | `C85 M35 Y25 K10` | `Pantone 7700 C` |
| **Surface Dark** | Midnight Marine Slate | `#0D1F18` | `rgb(13, 31, 24)` | `C85 M60 Y75 K80` | `Pantone Black 7 C` |
| **Surface Light** | Ocean Mist Page | `#F4F5F0` | `rgb(244, 245, 240)` | `C3 M2 Y4 K0` | `Pantone Cool Gray 1 C` |
| **Contrast** | Crisp White | `#FFFFFF` | `rgb(255, 255, 255)` | `C0 M0 Y0 K0` | — |

### Pasangan Kontras Disetujui:
1. **Latar Terang (`#FFFFFF` / `#F4F5F0`):** Gunakan `lautan-horizontal.svg` atau `lautan-symbol.svg` (tinta `#1C382A` / `#0E7490`).
2. **Latar Gelap (`#0D1F18` / `#1C382A`):** Gunakan `lautan-horizontal-dark.svg` (tinta `#FFFFFF` dengan aksen `#C9F26B`).
3. **Monokrom:** Hitam pekat `#000000` pada dokumen print faks/memo; putih bersih pada foto latar maritim kontras tinggi.

---

## 6. Tipografi Pendamping

- **Judul & Interface:** `Inter`, SemiBold / Bold (fallback: `Segoe UI`, `system-ui`).
- **Data & Telemetri:** `Roboto Mono`, Regular / Bold (fallback: `Courier New`, monospace).
- **Aturan Wordmark:** Selalu gunakan file SVG kurva vektor outlined master; **dilarang mengetik ulang wordmark dengan font biasa** untuk menjaga integritas kerning dan ligatur.

---

## 7. Pantangan Penggunaan (*Don'ts*)

- **Jangan mendistorsi rasio:** Jangan menarik atau memipihkan logo secara non-proporsional.
- **Jangan mengganti warna sembarangan:** Gunakan hanya palet warna yang telah ditetapkan di atas.
- **Jangan memutar posisi mark:** Orientasi kurva Arus Nusantara harus tetap horizontal (aliran kiri ke kanan).
- **Jangan menambahkan bayangan tebal (*drop shadows*) atau bevel/emboss:** Pertahankan estetika flat vector modern.
- **Jangan menempatkan logo di atas latar belakang foto yang terlalu ramai** tanpa filter kontras atau pelindung kontainer.
