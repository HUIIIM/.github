# Changelog · vertciti DNA

All notable changes to the DNA (`design/`) are recorded here.
Format: [Keep a Changelog](https://keepachangelog.com/en/1.1.0/) · Versioning: [SemVer](https://semver.org/) via `tokens.json` `version`.
Releases are tagged `dna-vX.Y.Z` after merge; consumers pin that tag in `dna-drift` (`ref:`).

## [4.1.0] — unreleased

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
