# Smart Environment Monitor — Design Tokens

Extracted from `web/static/style.css`. Every value below maps to an existing CSS declaration. No new colors or spacing were invented.

---

## Palette

| Token | Value | Usage |
|-------|-------|-------|
| `--bg-page` | `#f4f6f8` | Page background |
| `--bg-surface` | `#ffffff` | Cards, panels, inputs, modals, tables |
| `--bg-surface-alt` | `#f8fafc` | Code blocks, table headers, health detail groups |
| `--bg-hover` | `#eef2f6` | Button/link hover, badge backgrounds, table header |
| `--bg-focus` | `#fbfcfe` | Focused input background |
| `--bg-modal-overlay` | `rgba(15, 23, 42, 0.54)` | Modal backdrop |
| `--bg-modal-header` | `#fafbfc` | Modal header bar |
| `--bg-modal-filter` | `#fafbfc` | Modal filter section |
| `--bg-table-row-hover` | `#f0f7ff` | Table row hover |
| `--bg-table-header` | `#e4ebf3` | Table header row |
| `--text-primary` | `#1f2933` | Headings, primary body text, dark badges |
| `--text-secondary` | `#344054` | Card titles, table headers, secondary headings |
| `--text-muted` | `#667085` | Labels, descriptions, hints, empty state body |
| `--text-strong` | `#101828` | Emphasized text |
| `--text-link` | `#2563eb` | Links, active accents |
| `--border-default` | `#d7dee8` | Cards, panels, tables, empty state |
| `--border-input` | `#cbd5e1` | Inputs, buttons, pagination, filters |
| `--border-focus` | `#b9c6d6` | Focused input border |
| `--border-table` | `#e4e9f0` | Table cell separators |
| `--status-online-bg` | `#dcfce7` | Online health badge |
| `--status-online-text` | `#166534` | Online health badge text |
| `--status-offline-bg` | `#fee2e2` | Offline health badge |
| `--status-offline-text` | `#991b1b` | Offline health badge text |
| `--badge-green` | `#157347` | Success badge background |
| `--badge-yellow` | `#9a6700` | Warning badge background |
| `--badge-purple` | `#6d28d9` | Info badge background |
| `--shadow-modal` | `rgba(15, 23, 42, 0.22)` | Modal box shadow |

---

## Typography

| Token | Value | Usage |
|-------|-------|-------|
| `--font-family` | `Arial, "Hiragino Sans", "Yu Gothic", sans-serif` | Global stack |
| `--font-size-h1` | `28px` | Page title (desktop) |
| `--font-size-h1-mobile` | `24px` | Page title (mobile, ≤640px) |
| `--font-size-h2` | `18px` | Section headings |
| `--font-size-h2-empty` | `20px` | Empty state heading |
| `--font-size-h3` | `16px` | Card titles, filter panel heading |
| `--font-size-h3-health` | `17px` | Health card heading |
| `--font-size-h4` | `15px` | Modal heading |
| `--font-size-body` | `14px` | Body text, buttons, links, table text |
| `--font-size-label` | `13px` | Form labels, field hints, code blocks, modal labels |
| `--font-size-small` | `12px` | Badges, metric labels, small captions, API tags |
| `--font-size-xs` | `11px` | Code snippets, tiny labels |

---

## Spacing

### Scale
All padding, margin, and gap values used in the CSS:
`0`, `4px`, `5px`, `6px`, `7px`, `8px`, `9px`, `10px`, `12px`, `14px`, `16px`, `18px`, `20px`, `28px`

### Component spacing
| Token | Value | Usage |
|-------|-------|-------|
| `--page-margin-top` | `28px` | Desktop page top margin |
| `--page-margin-top-mobile` | `16px` | Mobile page top margin |
| `--page-width` | `min(100% - 20px, 1120px)` | Content max width |
| `--card-padding` | `14px` / `16px` / `18px` | Card internal padding |
| `--card-gap` | `16px` | Gap between cards |
| `--panel-padding` | `14px` | Filter/health panel padding |
| `--panel-margin-bottom` | `14px` | Panel bottom margin |
| `--input-padding-x` | `10px` | Input horizontal padding |
| `--input-min-height` | `36px` | Input/button minimum height |
| `--button-padding-x` | `12px` / `14px` | Button horizontal padding |
| `--badge-padding-x` | `8px` | Badge horizontal padding |
| `--badge-min-height` | `25px` | Badge minimum height |
| `--empty-state-padding` | `28px` | Empty state internal padding |

---

## Components

### Card / Panel
- `border: 1px solid #d7dee8`
- `border-radius: 8px`
- `background: #ffffff`
- `padding: 14px` or `16px` or `18px`

### Button (Secondary / Refresh)
- `display: inline-flex`
- `align-items: center`
- `min-height: 36px`
- `padding: 0 12px` (secondary) or `0 14px` (refresh)
- `border: 1px solid #cbd5e1`
- `border-radius: 6px`
- `background: #ffffff`
- `color: #1f2933`
- `font-size: 14px`
- Hover: `background: #eef2f6`
- Disabled: `opacity: 0.65`, `cursor: wait`

### Input / Select
- `min-height: 36px`
- `width: 100%`
- `padding: 0 10px`
- `border: 1px solid #cbd5e1`
- `border-radius: 6px`
- `background: #ffffff`
- `color: #1f2933`
- `font: inherit`
- Focus: `border-color: #b9c6d6`, `background: #fbfcfe`

### Badge / Pill
- `min-height: 25px`
- `padding: 0 8px`
- `border-radius: 999px`
- `font-size: 12px`
- `color: #ffffff` (filled) or contextual text color

### Filter Panel
- `margin-bottom: 14px`
- `padding: 14px`
- `border: 1px solid #d7dee8`
- `border-radius: 8px`
- `background: #ffffff`

### Empty State
- `border: 1px solid #d7dee8`
- `border-radius: 8px`
- `background: #ffffff`
- `padding: 28px`
- Heading: `font-size: 20px`, `margin: 0 0 8px`
- Body: `color: #667085`, `margin: 0`

---

## States

| State | Rules |
|-------|-------|
| **Hover** | `background: #eef2f6` on buttons, links, table rows |
| **Disabled** | `opacity: 0.65`, `cursor: wait` |
| **Focus** | `border-color: #b9c6d6`, `background: #fbfcfe` on inputs |
| **Online** | `background: #dcfce7`, `color: #166534` |
| **Offline** | `background: #fee2e2`, `color: #991b1b` |

---

## Responsiveness

Breakpoint: `@media (max-width: 640px)`

| Element | Desktop | Mobile (≤640px) |
|---------|---------|-----------------|
| `.page` | `margin-top: 28px` | `margin-top: 16px`, `width: min(100% - 20px, 1120px)` |
| `.page-header` | `flex-direction: row` | `flex-direction: column`, `align-items: flex-start` |
| `.header-actions` | `width: auto` | `width: 100%` |
| `.toolbar` | `flex-direction: row` | `flex-direction: column`, `align-items: stretch` |
| `.filter-grid` | `grid-template-columns: repeat(4, 1fr)` | `grid-template-columns: 1fr` |
| `.filter-field-wide` | `grid-column: span 2` | `grid-column: auto` |
| `.health-list` | `grid-template-columns: repeat(2, 1fr)` | `grid-template-columns: 1fr` |
| `.graph-grid` | multi-column | `grid-template-columns: 1fr` |
| `.graph-pane` | default height | `height: 280px`, `padding: 10px` |
| `.chart-modal-panel` | default | `width: calc(100% - 20px)`, `height: calc(100% - 32px)`, `margin: 16px auto`, `padding: 10px` |
| Buttons / inputs | auto width | `width: 100%` |
| `h1` | `font-size: 28px` | `font-size: 24px` |

---

## Implementation Guardrails

1. **Color-scheme**: `light` only (`:root`). Do not add dark-mode tokens.
2. **Box-sizing**: `border-box` globally.
3. **No new raw colors**: Every color must come from the palette table above.
4. **No arbitrary spacing**: Use only the gap, padding, and margin values listed in the spacing section.
5. **Border radius**: Use `6px` (buttons/inputs), `8px` (cards/panels), or `999px` (pills) only.
6. **Min-heights**: `20px`, `25px`, `30px`, `32px`, `36px`, `40px` are the existing scale.
7. **Font stack**: Do not change the global `font-family` without updating the token table.
