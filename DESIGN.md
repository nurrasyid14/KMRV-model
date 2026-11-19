# DESIGN.md: Product

## 1. Design Read (Evidence-Based)

- **Product:** Lautan.id — static SPA dashboard for maritime climate monitoring and honest ENSO model evaluation for Indonesian waters.
- **Target Audience:** Academic examiners (rigor, methodology) and general curious visitors (plain-language ENSO status). Balanced deliberately.
- **Product Type:** Dashboard (data-monitoring + evaluation).
- **Primary User Goal:** Understand current ENSO phase (ONI) and the model's real, limited skill in one scan.
- **User Roles & Workflows:** Single anonymous role. Screens: (1) Dashboard — latest ONI/SOI/DMI + 5-domain SST anomalies; (2) Evaluation — metrics per horizon, confusion matrices, persistence baseline; (3) Historical archive — ONI Jan 2016–Jun 2025 with test-period annotation. No auth-gated workflows (Clerk v6 present in stack but no role defined → `TBD`).
- **Brand / Aesthetic Direction:** Institutional-scientific, editorial, utilitarian. Flat neutral surfaces, hairline rules, monospaced numerals, restrained sea-blue accent. No decorative gradients or glass.
- **Key Personality Traits:** Honest, legible, evidence-first.

## 2. Design Dials

- **DESIGN_VARIANCE: 2** — Data consistency is paramount; identical metric cards and chart frames must read predictably across horizons and domains. Variation is reserved for content structure (tables vs. charts), not decoration.
- **MOTION_INTENSITY: 2** — Users scan numbers; animation must not delay reading. Motion limited to focus/hover feedback (opacity, transform) at 120–160ms.
- **VISUAL_DENSITY: 7** — Evaluation page carries metrics, confusion matrices, and baseline tables; density is required but bounded by whitespace and hairline dividers, not boxes.

## 3. Visual Identity & Product-Type Adaptation

Adaptation for a dashboard: strong left-aligned hierarchy, tabular numeric alignment, scannable metric rows, and a persistent ONI status banner. Distinctiveness comes from **typographic contrast + monospaced figures + Indonesian decimal-comma notation**, not ornament. Charts are Recharts with neutral gridlines and a single accent series; El Niño/La Niña states are labeled with text + shape, never color alone.

## 4. Semantic Color System

```css
:root {
  --color-primary: #00a3c4;   /* brand sea-blue, PRD-mandated */
  --color-secondary: #0b3d4a; /* deep sea, headings/emphasis */
  --color-accent: #00a3c4;    /* active nav, primary CTA only */
  --color-success: #1f7a4d;   /* La Niña / positive-skill marker */
  --color-warning: #b26a00;   /* Netral / caution */
  --color-danger: #b3261e;    /* El Niño / failed horizon */
  --color-bg: #f7f8f9;        /* page background */
  --color-surface: #ffffff;   /* panel background */
  --color-fg: #14181b;        /* primary text */
  --color-muted: #5a6672;     /* secondary text */
  --color-border: #d9dee3;    /* hairline rules */
}
```

**Usage rules:** Neutrals (`bg`, `surface`, `fg`, `muted`, `border`) form ~90% of pixels. `--color-primary` is reserved for active nav, links, and the single primary CTA per viewport. `--color-success/warning/danger` map strictly to ENSO phase and model-skill verdicts, always paired with a text label. Neon blue/purple gradients are prohibited.

## 5. Typography & Type Scale

- **Primary (UI/body):** `Inter` — neutral, high legibility at small sizes for dense tables.
- **Numeric (values):** `Roboto Mono` — PRD mandates monospaced numerals; ensures column alignment and decimal-comma clarity.
- Load via Google Fonts: `Inter:wght@400;500;600` and `Roboto+Mono:wght@400;500`.

| Level | Size | Weight | Line-Height | Tracking | Rationale |
|:---|:---|:---|:---|:---|:---|
| h1 | 1.75rem | 600 | 1.2 | -0.01em | Page title, single per view |
| h2 | 1.25rem | 600 | 1.3 | 0 | Section headers |
| h3 | 1rem | 600 | 1.4 | 0 | Panel titles |
| body | 0.9375rem | 400 | 1.6 | 0 | Prose, explanations |
| metric | 1.5rem mono | 500 | 1.1 | -0.02em | ONI/SOI/DMI values |
| caption | 0.75rem | 400 | 1.4 | 0.01em | Units, timestamps, footnotes |

## 6. Layout Strategy & Anti-Repetition Rules

- **Dashboard:** full-width status banner (ONI + phase) → 3-column metric row (ONI/SOI/DMI) → 5-domain SST anomaly **table** (not cards) → recent ONI sparkline.
- **Evaluation:** tabbed by horizon (1/3/6 bulan). Each tab = metrics table + confusion matrix grid + persistence comparison table. No repeated card grids.
- **Archive:** single ONI line chart + annotated test-period band + data table fallback.
- **Grid/Spacing:** 12-col grid, max content width 1200px, gutters 24px, section rhythm 32/48px. Spacing scale: 4/8/12/16/24/32/48px.

## 7. Anti-AI-Slop Rules

- **Avoid** three-card feature grids → **Prefer** structured tables and metric rows.
- **Avoid** every section in rounded cards → **Prefer** whitespace + hairline dividers.
- **Avoid** purple/blue AI gradients or mesh blobs → **Prefer** flat neutrals with one accent.
- **Avoid** decorative icons/badges → **Prefer** typographic hierarchy and text status labels.
- **Avoid** decorative animation → **Prefer** interaction-feedback transitions only.

## 8. Card & Container Discipline

A card (surface + 1px border + 12px padding) is allowed **only** for self-contained dashboard widgets (metric tiles, chart frames, confusion-matrix cells). Forbidden for prose sections, lists, and archive tables — use dividers instead. **Card nesting is prohibited.**

## 9. Component Rules & Action Hierarchy

- **Primary:** solid `--color-primary` fill, white text — max one per viewport (e.g., "Lihat Evaluasi Model").
- **Secondary:** 1px border, transparent fill, `--color-fg` text.
- **Tertiary:** text link, underline on hover.
- **States:** hover = 6% darken; focus = 2px `--color-primary` ring, 2px offset; disabled = 40% opacity + `cursor:not-allowed`; selected tab = 2px bottom border in primary.

## 10. Behavioral Responsive Design

- **≥1024px:** 3-col metric row, side-by-side chart+table.
- **768–1023px:** metrics 2-col, charts full width.
- **<768px:** top nav → bottom tab bar; metric row stacks; SST table collapses to domain + value columns (secondary columns hidden); confusion matrix scrolls horizontally.

## 11. States (Loading, Empty, Error)

- **Loading:** skeleton blocks matching metric-tile and chart-frame dimensions (no spinners). Note: data is static from `realData.js`, so loading applies only to chart mount.
- **Empty:** contextual message + next step (e.g., "Data horizon ini tidak tersedia.").
- **Error:** inline alert with `--color-danger` border, message, and "Muat Ulang" button.

## 12. Accessibility & Inclusivity (WCAG 2.1 AA)

Keyboard-operable tabs and nav; visible 2px focus ring with offset; charts carry `role="img"` + accessible title/description; touch targets ≥44×44px; ENSO phase conveyed via text label + icon shape, never color alone; contrast ≥4.5:1 for body text.

## 13. Design Rationale

Density-7 with variance-2 serves examiners (rigor, comparable tables) and general visitors (single scannable ONI banner). Monospaced numerals and Indonesian decimal-comma notation make every figure traceable and legible — directly serving the PRD principle "kejujuran adalah desain." Restrained motion and neutral palette keep attention on evidence, not ornament.

## 14. NO Invented Design Content Rule

No fabricated testimonials, user logos, screenshots, or statistics. Every displayed number originates from `realData.js` (dataset + model artifacts). Missing values render as `—`, never invented.

## 15. Design Pre-Flight Checklist

- [ ] Design is derived from PRD/project context.
- [ ] Design Read is specific.
- [ ] Design dials are intentional.
- [ ] Visual direction is justified.
- [ ] Color hierarchy is intentional.
- [ ] Typography is intentional.
- [ ] Cards are not overused.
- [ ] Layouts are not repetitive.
- [ ] No generic AI aesthetic was introduced without justification.
- [ ] Motion has a purpose.
- [ ] Responsive behavior is defined.
- [ ] Loading states are defined where relevant.
- [ ] Empty states are defined where relevant.
- [ ] Error states are defined where relevant.
- [ ] Accessibility is defined.
- [ ] No fake content was invented.
- [ ] Design feels specific to the product.
- [ ] A coding agent can implement the design without inventing major visual decisions.
- [ ] Design System is cohesive and reusable.