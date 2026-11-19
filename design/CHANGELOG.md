# Changelog · vertciti DNA

All notable changes to the DNA (`design/`) are recorded here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · Versioning: [SemVer](https://semver.org/) via `tokens.json` `version`.
Releases are tagged `dna-vX.Y.Z` after merge; consumers pin that tag in `dna-drift` (`ref:`).

## [4.1.2] — 2026-11-12

### Fixed
- **Focus ring on the accent (yellow) surface measured 2.28:1** (2.02:1 on its soft fill), under WCAG 2.2
  SC 1.4.11's 3:1. `--focus-ring` is `3px solid var(--pointer)`, and a custom property's `var()` resolves
  where it is declared, so `.dna-card--accent` re-declaring only `--pointer` (black) still inherited the
  orange ring from `:root`. Every scoped surface now re-declares `--focus-ring`, so the ring follows the
  surface: black on accent (14.08:1). Found by the new non-text gate; the token-level pair check could not
  see it because it compares `--pointer`, not the ring that is drawn.

### Added
- **Non-text contrast gate** `standards/a11y/nontext_audit.js` (SOTA DS-1, #125): component boundaries
  and keyboard focus indicators must reach 3:1 against what is painted around them, measured in a real
  browser. Runs in the `design` workflow on both preview pages × light/dark × 390/1280, and must still fail
  its known-bad fixture (`standards/a11y/fixtures/nontext-bad.html`, 4 defects).

## [4.1.1] — 2026-11-09

Puts every DNA font size and spacing value on the scales the fleet's website QA gates enforce (#101), so a
product that vendors the DNA passes gates A1 and A2 with no local overrides. No variable or class was removed.

### Added
- **`build.py --check` enforces the QA-gate scales** with website-qa-gates' own A1/A2 patterns, over
  `src/base.css`, both `dist/` stylesheets and the `font.size` tokens, so a DNA change can no longer
  reintroduce an off-scale value. Tests: `design/test_build.py` (run by the `design` workflow).

### Changed
- **Font sizes off the type scale** (gate A1 rejects 13/15/17/19px): hints, the utility bar, footer and
  `.dna-stat__src` 13px → 14px; `.dna-tab` 15px → 16px; `.dna-empty__text` 17px → 18px; the
  `--fs-md` token 17px → 18px (a product writing `font-size: var(--fs-md)` would otherwise fail A1).
- **Spacing off the 4px scale** (gate A2 allows 0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 120):
  table cells `10px 12px` → `8px 12px`; `.dna-btn` `0 28px` → `0 24px`; `.dna-card` 28px → 24px; inputs
  `12px 14px` → `12px 16px`; `.dna-tab` `0 14px` → `0 16px`; `.dna-badge` `2px 8px` → `4px 8px`;
  `.dna-alert` `14px 16px` → `12px 16px`; `.dna-logo` `10px 0` → `8px 0`; `.dna-pagehead` clamp bounds
  72/28px → 64/24px; `.dna-seg` clamp bounds 10/18px → 8/16px.
- **`.dna-seg` joins its segments by dropping the left border** of every segment after the first, instead
  of a `-2px` margin.

## [4.1.0] — 2026-11-03

Closes the design-system findings of the independent SOTA assessment (#40). No CSS variable or class was
removed, so vendored apps keep working; several values changed (listed below), so re-vendor and look.

### Fixed
- **Dark mode text contrast on cards and soft surfaces** (WCAG 1.4.3). `--ok`, `--bad` and `--info` measured
  3.52, 2.84 and 4.44:1 on the v4.0 dark card (`#3F3F3F`). Dark `--card` is now `#161616`, `--soft` `#262626`,
  `--bad` `#E87272`. Light `--ok` on `--soft` measured 4.31:1; light `--ok` is now green-700 `#166B3B`.
- **`.dna-grid` children without a `dna-span-*` class** took 1/12 of the row, so their text wrapped one
  character per line. They now take the full row.
- **Tap targets under 44 px** (AESTHETICS §7; WCAG 2.5.8): tabs, utility-bar links and buttons, header-end
  links, footer links and the logo now have a 44 px minimum. The utility bar is 44 px tall (was 40).

### Changed
- **Motion follows IBM Carbon productive tokens** (SOTA MOT-2/3/7): new `--motion-fast-01` 70ms,
  `--motion-fast-02` 110ms, `--motion-moderate-01` 150ms, `--motion-moderate-02` 240ms, `--motion-slow-01`
  400ms and `--ease-standard/entrance/exit`. The v4.0 names stay as aliases with new values:
  `--dur-fast` 110ms (was 150ms), `--dur-base` 240ms (was 250ms), `--dur-slow` 400ms (was 1.2s),
  `--ease` = standard curve. Only `transform` animates; colour, shadow and width changes are instant;
  exits are one step faster than entries.
- **Data bar `.dna-bar > span` is ink, not orange**, and no longer animates its width (SOTA DES-1: orange is a
  pointer only; MOT-5: data-true). The reading-progress bar stays orange.
- **Inverse surfaces are tokens**: `color.ink` and `color.accent` in `tokens.json`, emitted as scoped rules on
  `.dna-card--ink`, `.dna-utility`, `.dna-code` and `.dna-card--accent`. Component CSS has no colour literals
  (SOTA DES-2). Inside the yellow accent surface the pointer (focus ring, link underline) is ink, because
  orange on yellow is 2.3:1.
- **Focus ring and pointer marks use the new `--pointer` token** (`#FF4713`; `--orange` is unchanged).
- Print colours are generated from the light theme.

### Added
- `.dna-empty` / `.dna-empty__text` empty-state component; the gallery shows loading, empty and error states.
- `dist/tokens.dtcg.json`: a W3C DTCG 2025.10 export of every representable token, validated by
  `build.py --check`. `tokens.json` no longer claims the DTCG `$schema` it did not follow.
- `preview/surfaces.html` (generated): every text token on every surface, rendered by the contrast gate.
- `standards/a11y/layout_audit.js`: CI gate for horizontal overflow, collapsed text and tap targets.
- `build.py --check` now checks the full matrix: every text token on bg, soft and card of light, dark, ink
  and accent, plus the pointer at 3:1 (WCAG 1.4.11).
- `dna-drift.yml` takes an optional `ref` input so consumers can pin a DNA release.

## [4.0.0] — 2026-10-22

Initial extraction from vertciti.com (官网 v4, `site.css`).
