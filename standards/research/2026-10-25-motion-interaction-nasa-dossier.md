# Miao AI: motion, interaction and NASA-alignment benchmark dossier

Researched 2026-10-25. Primary sources were fetched and read unless marked **[unverified]** or **[from prior knowledge]**. No repo files were modified.

---

## 0. Executive summary

- **Motion.** For an institutional operator console, IBM Carbon's *productive* motion system is the best primary-source fit. It is short (70–240 ms), uses non-overshooting curves, and is explicitly meant "for moments when users are focused on tasks". Apple HIG, Vercel's Web Interface Guidelines, and WCAG point the same way: animate only to show cause and effect, keep every animation interruptible, never make motion the only carrier of information, and honor reduced motion. Material 3 changed its motion system to *springs* in May 2025 (M3 Expressive). Its "spatial" springs overshoot, so Miao should not adopt them. Only M3's no-overshoot "effects" behavior is compatible.
- **Telemetry UI.** NASA Open MCT gives the most transferable model for a live console: one global time conductor with *Real-time* and *Fixed* modes, telemetry metadata with `domain`/`range` hints, and limit evaluators. F Prime adds a strict event-severity taxonomy, event throttling, and red/orange/yellow telemetry limits.
- **Keyboard.** The best-in-class model, verified across Linear, Blueprint and Raycast: ⌘K command menu, `/` search, `?` shortcut sheet, `G`-then-letter navigation, Enter for the primary action and ⌘Enter for the secondary.
- **NASA mapping.** NPR 7150.2D (effective 2022-03-08, **expires 2027-03-08**) is binding only on NASA and its contractors. Miao can only be *mapped to* it. The honest analog is a **Class D** baseline (64 invoked requirements) plus a few Class C items. NPR 7150.2D's **SWE-134 a–l** safety/mission-critical behaviors should be adopted *voluntarily* for the control path (gateway, guard chain, safe-mode, kill switch). Those twelve items read almost like a spec of what Miao already does: known safe state at start, predefined transitions, two independent operator actions for overrides, rejection of out-of-sequence commands, prerequisite checks, and the ability to command safe state.
- **Theatre to avoid.** CMMI ratings, "NASA IV&V", blanket 100% MC/DC, literal Power-of-10 C rules in Python/TypeScript, NASA cost-model and repository submissions, and any use of the NASA name or insignia as an endorsement.

---

# PART A — Motion & interaction benchmark

## A.1 What each source actually says (verified extracts)

| Source | Verified content used here | URL |
|---|---|---|
| IBM Carbon motion | Productive standard `cubic-bezier(0.2,0,0.38,0.9)`, entrance `(0,0,0.38,0.9)`, exit `(0.2,0,1,0.9)`. Expressive standard `(0.4,0.14,0.3,1)`, entrance `(0,0,0.3,1)`, exit `(0.4,0.14,1,1)`. Durations: fast-01 70 ms (buttons, toggles), fast-02 110 ms (fades), moderate-01 150 ms (small expansion, short movement), moderate-02 240 ms (expansion, system communication, toasts), slow-01 400 ms (large expansion, important notifications), slow-02 700 ms (background dimming). Productive = "subtle and efficient… users are focused on tasks… dropdowns… rendering data tables". Expressive = reserved for "occasional significant moments". Duration scales with distance. | https://carbondesignsystem.com/elements/motion/overview/ |
| Material 3 tokens (material-web, v0.192) | Durations short1–4 = 50/100/150/200 ms, medium1–4 = 250–400, long1–4 = 450–600, extra-long1–4 = 700–1000. Easing: standard `(0.2,0,0,1)`, standard-decelerate `(0,0,0,1)`, standard-accelerate `(0.3,0,1,1)`, emphasized `(0.2,0,0,1)`, emphasized-decelerate `(0.05,0.7,0.1,1)`, emphasized-accelerate `(0.3,0,0.8,0.15)`, legacy `(0.4,0,0.2,1)`. | https://github.com/material-components/material-web/blob/main/tokens/versions/v0_192/_md-sys-motion.scss |
| Material 3 Expressive (May 2025) | "The physics system is replacing the previous system based on easing and duration." Springs are defined by stiffness, damping and initial velocity. Two schemes: *expressive* and *standard* ("more functional with minimal bounce… for utilitarian products"). *Spatial* springs "overshoot… and bounce into place". *Effects* springs (color, opacity) have no overshoot. | https://m3.material.io/styles/motion/overview/how-it-works |
| Apple HIG — Motion | "Don't add motion for the sake of adding motion." "Make motion optional… avoid using it as the only way to communicate important information." "Aim for brevity and precision in feedback animations." "In apps, generally avoid adding motion to UI interactions that occur frequently." "Let people cancel motion… don't make people wait for an animation to complete." visionOS: avoid motion in peripheral vision. Prefer fades over movement when relocation carries no meaning. Give people a stationary frame of reference. | https://developer.apple.com/design/human-interface-guidelines/motion |
| Vercel Web Interface Guidelines | Keyboard works everywhere (WAI-ARIA APG). `:focus-visible` rings that are never obscured. Focus traps with return of focus. Honor `prefers-reduced-motion`. Prefer CSS over WAAPI over JS. "Only animate when it clarifies cause & effect." Animations are interruptible. Never `transition: all`; animate `opacity`/`transform`. Correct transform origin. Loading: show-delay ~150–300 ms and minimum visible ~300–500 ms. URL as state; deep-link everything. Optimistic updates with rollback or Undo. Confirm destructive actions or offer Undo. POST/PATCH/DELETE complete in <500 ms. Tabular numbers. Tooltips: delay the first, no delay for its peers. Polite `aria-live` for async updates. Locale-aware shortcuts. Virtualize large lists. | https://github.com/vercel-labs/web-interface-guidelines (also vercel.com/design/guidelines) |
| Vercel Geist | High-contrast accessible colors, Geist Sans/Mono, materials, grid. The intro page gives no motion guidance. | https://vercel.com/geist/introduction |
| Linear UI redesign (2024) | Goals: "reduce visual noise, maintain visual alignment, and increase the hierarchy and density of navigation elements". Themes moved from HSL to LCH and are generated from 3 inputs (base, accent, contrast) instead of 98 variables. Less chrome color. An automatic high-contrast theme. Alignment is something users "feel after a few minutes". The post says nothing about motion. | https://linear.app/now/how-we-redesigned-the-linear-ui |
| Linear navigation guide | Cmd/Ctrl+K command menu runs actions or jumps to pages. Two-key `G`+letter navigation (G I Inbox, G M My Issues). `?` shows all shortcuts. `/` searches. | https://linear.app/enablement/guide/navigating-linear |
| Linear sync engine | Local-first sync engine (Tuomas Artman talks). Specific latency figures are **[unverified]**. | https://linear.app/now/scaling-the-linear-sync-engine |
| Blueprint (Palantir) hotkeys | Hotkeys must belong to a group or be marked global. `?` opens the global hotkeys dialog, which lists global hotkeys plus those of the focused element. One `HotkeysProvider` at the root. | https://unpkg.com/@blueprintjs/core@6.0.0/src/hooks/hotkeys/use-hotkeys.md |
| Raycast Action Panel | "The first and second action become the primary and secondary action": Enter and ⌘Enter in lists, ⌘Enter and ⌘⇧Enter in forms. Sections group related actions. | https://developers.raycast.com/api-reference/user-interface/action-panel |
| NASA Open MCT API | Domain objects plus composition. Telemetry metadata `values[]` with `hints` (`domain` = x-axis and first table columns, `range` = y-axis). Providers: `subscribe` (realtime), `request` (historical, `start`/`end`/`domain`), `latest` and `minmax` request strategies. Limit evaluators with 5 colors. Time API: time systems, bounds, clocks, clock offsets, **two modes: "Fixed" and "Real-time"**. The Time Conductor lets the user choose the time system, clock, bounds and offsets. | https://github.com/nasa/openmct/blob/master/API.md |
| F Prime / FPP | Components are active (thread + queue), queued, or passive. Ports are `sync`/`async`/`guarded` input or `output`. Event severities: `activity high`, `activity low`, `command`, `diagnostic`, `fatal`, `warning high`, `warning low`. Events support `throttle N every {seconds}`. Telemetry `update on change`/`always`, with `low {red, orange, yellow}` and `high {…}` limits. A generated **dictionary** tells the ground system how to interpret data. | https://nasa.github.io/fpp/fpp-users-guide.html |
| Grafana Live | Pub/sub over a single WebSocket per page. "Soft real-time": delays of several hundred ms are possible. Default 100 connections. | https://grafana.com/docs/grafana/latest/setup-grafana/set-up-grafana-live/ |
| NN/g response-time limits | 0.1 s feels instantaneous, 1 s keeps the flow of thought, 10 s keeps attention. | https://www.nngroup.com/articles/response-times-3-important-limits/ |
| Bloomberg Terminal UX | "Even something as simple as a font change or the relocation of a button can be disruptive." Redesigns roll out incrementally over weeks or months. Old and new versions are supported side by side for opt-in. "If you change the experience and the technology at the same time, and the experience is rejected… you now have to revert the technology too." Central runtime switches with staged rollout. Stability means "protecting against displaying wrong data". | https://www.bloomberg.com/company/stories/how-bloomberg-terminal-ux-designers-conceal-complexity/ |
| Stripe accessible color | Uses a perceptually uniform space (CIELAB). Any two colors "at least five levels apart" pass small-text contrast, and four levels apart pass icons and large text. | https://stripe.com/blog/accessible-color-systems |
| WCAG 2.2 **[from prior knowledge]** | 2.2.2 Pause, Stop, Hide (A): auto-moving content lasting >5 s needs a pause control. 2.3.3 Animation from Interactions (AAA). 2.4.7 Focus Visible (AA). 2.4.11 Focus Not Obscured (Minimum) (AA). | https://www.w3.org/TR/WCAG22/ |

**Not verified / not used as evidence:** Stripe Sessions motion talks (no primary transcript found). Arc's command bar internals. Datadog Live Tail UI rules. BlackRock Aladdin UI (no public design documentation; only marketing pages). Third-party "Linear loads in <100 ms" claims. Rules below do not depend on these.

## A.2 Ranked rules (22)

Format: **Rule** — why — source — application in Miao's console.

1. **Motion exists only to show cause→effect or a state change. Nothing animates decoratively.**
   - Why: decorative motion distracts, and it costs attention every time an operator looks at the screen.
   - Source: Apple HIG ("don't add motion for the sake of adding motion"); Vercel "Necessity check"; Carbon productive.
   - Miao: the system schematic may move only when a real sealed audit event arrives. The mission readout row, goal ledger and approvals queue never use idle shimmer, parallax or looping gradients.

2. **Use productive curves and keep UI motion to 240 ms or less. 400 ms is the ceiling, reserved for safe-mode and system-level notices.**
   - Why: these are task-focused screens, and Carbon defines productive motion for exactly this case.
   - Source: Carbon motion tokens.
   - Miao: palette open, drawers and toasts use 240 ms. Row insert into the approvals queue uses 150 ms. The DEGRADED/SAFE/HALTED banner uses 400 ms. Nothing exceeds that except the data-driven pulse travel described in Rule 8.

3. **No overshoot, bounce or elastic easing anywhere.**
   - Why: bounce reads as playful and "consumer". M3's own *standard* scheme exists for utilitarian products with "minimal bounce", and its *spatial* springs overshoot by design.
   - Source: M3 motion physics page; Carbon curves (none overshoot).
   - Miao: if a spring library is used, set it to critically damped (damping ratio ≥1). Opacity and color must never overshoot (M3's "effects" behavior).

4. **Exit faster than enter. Entrances decelerate, exits accelerate. Elements that stay on screen use standard easing.**
   - Why: an element leaving should get out of the way, and one arriving should settle.
   - Source: Carbon ("exit easing when an element leaves the screen permanently; for a side panel that stays nearby, use standard easing").
   - Miao: the twin "what-if" drawer opens over 240 ms with entrance easing and closes over 150 ms with exit easing. Toasts enter over 240 ms and leave over 110 ms.

5. **Animate only `opacity` and `transform`. Never use `transition: all`. Prefer CSS over WAAPI over JS.**
   - Why: avoids layout thrash and jank on the main thread, which also carries the SSE stream.
   - Source: Vercel guidelines.
   - Miao: animate schematic pulses with transform on SVG `<g>` wrappers (Vercel's cross-browser SVG note). The 24h chart never animates its axes on update.

6. **Every animation is interruptible and never blocks input.**
   - Why: an operator must be able to act mid-transition, especially to hit the kill switch.
   - Source: Apple ("Let people cancel motion"); Vercel ("Interruptible").
   - Miao: the kill switch and palette are always reachable. Banner and drawer transitions never set `pointer-events: none` on the page, and focus moves immediately even while the visual transition is still running.

7. **Motion is never the only carrier of information.**
   - Why: accessibility, reduced-motion users, glanceability, screenshots, and audit.
   - Source: Apple ("Make motion optional"); WCAG.
   - Miao: each pulse through the guard chain also increments a per-stage counter and leaves a static "last verdict" label (PASS/BLOCK + stage name). A safe-mode change also updates the text in the readout row and the document `<title>`.

8. **Motion must be data-true. Show only real events, in real order, at a constant per-hop speed, with linear easing. Never interpolate or fabricate.**
   - Why: on an institutional console the visualization is evidence. Bloomberg defines stability partly as "protecting against displaying wrong data".
   - Source: Bloomberg; Open MCT (telemetry is rendered from datums, not synthesized).
   - Miao: pulse travel time = hop count × a constant (for example 120 ms per hop) with `linear` easing. A blocked call stops at the blocking stage and does not travel on. If the client queue backs up, collapse pulses into a count badge ("+37") instead of speeding the animation up.

9. **Show liveness honestly: a visible LIVE/STALE/PAUSED state backed by a heartbeat.**
   - Why: Open MCT separates Real-time from Fixed modes, and Grafana Live is explicitly "soft real-time".
   - Source: Open MCT Time API; Grafana Live.
   - Miao: the readout row carries a status chip: LIVE (green, ok-only), STALE (yellow, attention) once no SSE heartbeat arrives within N seconds, and PAUSED (black outline). When STALE, freeze the schematic and stamp "last event hh:mm:ss UTC".

10. **One global time conductor.**
    - Why: in mission control, every view shares the same time bounds, so panels never disagree.
    - Source: Open MCT Time API / Time Conductor (modes, bounds, clock offsets).
    - Miao: a single `{mode: realtime|fixed, start, end | offsets}` store feeds the 24h chart, audit list, schematic replay and goal ledger. Selecting a range on the chart switches to Fixed mode and the schematic replays sealed events from that window. Encode the store in the URL (Rule 17).

11. **Telemetry carries metadata and limits. Color appears only on a limit crossing.**
    - Why: it keeps the black-and-white baseline and makes color mean something.
    - Source: Open MCT limit evaluators; FPP telemetry `low/high {red, orange, yellow}`.
    - Miao: declare each readout metric with `{key, unit, format, hints, limits}`. House mapping: warning maps to **yellow** (attention). Critical maps to an **inverted black block plus a text label**, because orange is pointer-only and there is no red in the palette. Do *not* reuse orange for limits. This is a deliberate deviation from FPP and Open MCT colors and should be documented.

12. **A fixed event-severity taxonomy, with throttling.**
    - Why: it prevents alert floods and makes severity filterable and comparable.
    - Source: FPP event severities and `throttle N every {seconds}`.
    - Miao: map audit and event kinds to FATAL / WARNING_HI / WARNING_LO / COMMAND / ACTIVITY_HI / ACTIVITY_LO / DIAGNOSTIC. Default the console filter to ≥ACTIVITY_HI. Throttle identical events per source and show the throttle count.

13. **Latency budgets: acknowledge input in 100 ms or less, complete it within 1 s or show progress, and keep mutating requests under 500 ms.**
    - Why: these are the human perception limits.
    - Source: NN/g (0.1 s / 1 s / 10 s); Vercel (POST/PATCH/DELETE <500 ms).
    - Miao: press states use 70 ms. Approve/reject buttons enter the "Sending…" state within one frame. Server work longer than 1 s (for example a twin rehearsal) shows determinate progress or a stage list.

14. **Be optimistic only where an action is reversible and not guarded. Guarded actions show "pending → sealed".**
    - Why: Vercel recommends optimistic updates with rollback, but in Miao an approval or tool execution is not *done* until the audit event is sealed. Showing it as done early would make the console lie.
    - Source: Vercel (optimistic updates; confirm destructive actions or offer Undo).
    - Miao: optimistic UI is fine for UI preferences, ledger notes and filters. For approvals, the row moves to "Approved · awaiting seal", and only the sealed SSE event (with its hash prefix) turns it final. On failure, roll back with an inline reason.

15. **Use a skeleton/spinner only after a show-delay of ~150–300 ms, and keep it visible for at least ~300–500 ms.**
    - Why: prevents flicker on fast responses.
    - Source: Vercel.
    - Miao: twin bench results, audit pagination and chart range fetches.

16. **Offer Undo for reversible operator actions and require two independent actions for hazardous ones.**
    - Why: Vercel's "Confirm destructive actions or provide Undo". NPR 7150.2D SWE-134(d): "Operator overrides of software functions require at least two independent actions by an operator."
    - Source: Vercel; NPR 7150.2D §3.7.3.
    - Miao: rejecting an approval gets a 10 s Undo toast. Approving a high-risk tool, engaging or clearing a kill switch, or leaving SAFE requires two independent actions, for example selecting the action, then typing or holding a confirm with ⌘Enter. Never a single keystroke.

17. **URL as state: deep-link time bounds, filters, the selected event and open drawers.**
    - Why: shareable incident links, reload safety, and Back/Forward support.
    - Source: Vercel ("URL as state", "Deep-link everything").
    - Miao: `/console?mode=fixed&start=…&end=…&event=<hash>&drawer=twin`.

18. **Keyboard-first operation: a command palette plus a discoverable shortcut sheet** (full spec in §A.4).
    - Why: it is the common pattern across the best operator tools.
    - Source: Linear (⌘K, G-chords, ?, /); Blueprint (`?` dialog, global vs grouped hotkeys); Raycast (Enter / ⌘Enter).
    - Miao: see §A.4.

19. **Visible, unobscured focus with managed focus.**
    - Why: keyboard operators, and WCAG 2.4.7 and 2.4.11.
    - Source: Vercel ("Clear focus", "Manage focus").
    - Miao: a 2 px black outline with 2 px offset (house square corners) on `:focus-visible`. Drawers and palette trap focus and return it to the invoker. Sticky readout rows must never cover the focused row (`scroll-margin-top`).

20. **Announce async updates politely. Use assertive announcements only for safe-mode transitions.**
    - Why: screen-reader users need state changes without being spammed.
    - Source: Vercel ("Announce async updates", polite aria-live).
    - Miao: a polite live region announces "3 new approvals". An assertive region is used only for NOMINAL→DEGRADED/SAFE/HALTED and for kill-switch changes. Never announce every pulse.

21. **Reduced motion means replacing movement with instant state changes or ≤110 ms opacity changes, plus a pause control for anything continuous.**
    - Why: WCAG 2.2.2 (pause for motion lasting more than 5 s) and 2.3.3. Apple advises avoiding peripheral motion and offering a stationary frame of reference.
    - Source: Vercel; Apple; WCAG.
    - Miao: under `prefers-reduced-motion: reduce`, pulses do not travel. The affected stage flashes its counter (opacity 110 ms), and the "last verdict" text updates. Always provide a ⏸ Pause-live toggle (keyboard `Space` on the schematic) that freezes the schematic while data keeps buffering.

22. **Density with stability: high information density, tabular numerals, stable positions, incremental change.**
    - Why: Linear's redesign aims to increase hierarchy and density while reducing noise. Bloomberg says relocating a button is disruptive and rolls change out incrementally.
    - Source: Linear; Bloomberg; Vercel (tabular numbers, virtualize lists, tooltip timing).
    - Miao: use `font-variant-numeric: tabular-nums` on all readouts and counters. Check that the self-hosted Nunito Sans build includes the `tnum` feature; if not, use a mono fallback for numerals only. Readout and table rows sit on 32 px rows (an 8 px grid multiple). Virtualize the audit list. Tooltips wait 500 ms for the first one and 0 ms for its peers. Never reorder readout tiles at runtime. Ship visual changes behind a feature flag and offer opt-in first.

23. **Use a perceptually uniform neutral scale with contrast stepping built into the scale.**
    - Why: Stripe's CIELAB system (≥5 steps apart passes small text) and Linear's LCH themes.
    - Source: Stripe blog; Linear redesign.
    - Miao: Tailwind v4's default palette is already OKLCH **[from prior knowledge]**. Define the house gray ramp in OKLCH, document "≥5 steps = AA small text", and lint for violations.

## A.3 Recommended motion token set (Miao "productive-institutional")

Derived from Carbon productive. Values are Carbon's except where marked as a house choice.

```css
:root {
  /* durations */
  --motion-instant: 0ms;      /* data value changes, selection state */
  --motion-micro:   70ms;     /* hover/press, toggles, checkbox (Carbon fast-01) */
  --motion-fast:    110ms;    /* fades, tooltips, exits of toasts (Carbon fast-02) */
  --motion-base:    150ms;    /* row insert/remove, small expand, drawer exit (Carbon moderate-01) */
  --motion-panel:   240ms;    /* drawer/palette/toast enter, accordion (Carbon moderate-02) */
  --motion-system:  400ms;    /* safe-mode banner, HALTED takeover (Carbon slow-01) */
  --motion-hop:     120ms;    /* HOUSE: per-hop pulse travel on schematic, linear */

  /* easing */
  --ease-standard: cubic-bezier(0.2, 0, 0.38, 0.9);  /* on-screen moves/resizes */
  --ease-enter:    cubic-bezier(0, 0, 0.38, 0.9);    /* elements appearing */
  --ease-exit:     cubic-bezier(0.2, 0, 1, 0.9);     /* elements leaving for good */
  --ease-linear:   linear;                           /* progress, data pulses, time-true motion */
}
@media (prefers-reduced-motion: reduce) {
  :root { --motion-micro:0ms; --motion-base:0ms; --motion-panel:110ms; --motion-system:110ms; --motion-hop:0ms; }
  /* panel/system keep a 110ms opacity-only fade; transforms disabled */
}
```

Usage rules:
- Exits use the next shorter token (panel → base, base → fast).
- Expressive curves are allowed in one place only, the first-run/login hero, if at all.
- No 700 ms tokens in the console.
- 8 px grid applies to motion distance too: translate offsets are 8 px or 16 px, never arbitrary values.

## A.4 Keyboard and command-palette spec

**Global**

| Key | Action | Precedent |
|---|---|---|
| ⌘K / Ctrl+K | Open command palette | Linear |
| `/` | Focus search/filter in current view | Linear |
| `?` | Shortcut sheet (global + focused-region groups) | Blueprint, Linear |
| `G` then `O`/`A`/`L`/`T`/`U`/`S` | Go to Overview, Approvals, Ledger, Twin bench, aUdit, Settings (1.2 s chord window) | Linear |
| `J`/`K`, ↑/↓ | Next/previous row in focused list | Linear (common) |
| Enter / ⌘Enter | Primary / secondary action on the focused row | Raycast |
| `X` | Toggle row selection (bulk) | Linear (common) **[unverified official]** |
| Esc | Close the topmost layer and return focus. A second Esc clears selection. | WAI-ARIA APG |
| `Space` (schematic focused) | Pause/resume live animation | WCAG 2.2.2 |
| `T` | Toggle time conductor Real-time ↔ Fixed | Open MCT |

**Hazardous actions** (two independent actions per SWE-134d; never one keystroke):
- Approve high-risk: `A` opens a confirm sheet, then ⌘Enter.
- Reject: `R`, followed by an Undo toast.
- Kill switch: palette "Engage kill switch…" plus typed confirmation, or ⌘⇧. plus hold for 1 s.
- Leaving SAFE: palette command, a reason field (written to audit), then ⌘Enter.

**Palette behavior**
- Opens in one frame with a 110 ms opacity fade and no scale.
- Groups: *Navigate · Actions · Agents/Tools · Recent · Help*.
- Fuzzy match over both zh and en labels. Optional pinyin initials for zh.
- Shortcut hints are right-aligned in muted gray.
- Actions that the current state forbids stay listed but disabled, with the reason, for example "Unavailable in SAFE mode (flight rule FR-012)". That teaches the state machine instead of hiding it.
- Enter runs the primary action, ⌘Enter the secondary, Tab opens the action submenu.
- Every executed command writes a COMMAND-severity audit event.

**Input hygiene**
- Ignore single-key shortcuts while focus is in an editable field.
- Ignore them while `event.isComposing` is true (zh IME).
- Bind chords by `event.key` for letters and show platform glyphs (⌘ vs Ctrl), per Vercel's "locale-aware keyboard shortcuts".

**Registry**
- One source of truth, for example `shortcuts.ts`, with `{id, keys, group, scope, labelZh, labelEn, hazard}`.
- The `?` sheet and palette hints are generated from it.
- A unit test asserts no duplicate bindings within a scope.

---

# PART B — NASA alignment for the architecture

## B.1 The documents, current status (verified)

| Document | Status | URL |
|---|---|---|
| **NPR 7150.2D** NASA Software Engineering Requirements | Effective 2022-03-08, **expires 2027-03-08**. I found no "7150.2E" publication on 2026-10-25. Re-check NODIS before citing. | https://nodis3.gsfc.nasa.gov/displayDir.cfm?t=NPR&c=7150&s=2D |
| **NASA-STD-8739.8B** Software Assurance and Software Safety Standard | Rev B, 2022-09-08, active, OSMA mandatory. Next 5-year review 2027-09-08. | https://standards.nasa.gov/standard/NASA/NASA-STD-87398 |
| **NASA-HDBK-2203 / SWEHB** (Software Engineering Handbook, Ver D) | Guidance and rationale for every SWE. Includes the PAT-028 compliance matrix spreadsheet. | https://swehb.nasa.gov/display/SWEHBVD/7.02+-+Classification+and+Safety-Criticality |
| **JPL "Power of Ten"** (Holzmann) | 10 rules for safety-critical C. | https://spinroot.com/gerard/pdf/P10.pdf |
| **NASA-HDBK-1002 Fault Management Handbook** | Public copy is **Draft 2 (2012), "not approved"**. Cite only as a draft. | https://www.nasa.gov/wp-content/uploads/2015/04/636372main_NASA-HDBK-1002_Draft.pdf |
| **cFS** (core Flight System) | Open source (Apache-2.0). Apps include Health & Safety, Limit Checker, Stored Command, CheckSum, HouseKeeping. Its own README warns: "not a flight distribution… should not be flown as is". | https://github.com/nasa/cFS |
| **F Prime / FPP** | Component/port model, dictionaries, event severities, Svc::Health ping/watchdog. | https://nasa.github.io/fpp/fpp-users-guide.html ; https://github.com/nasa/fprime/blob/devel/Svc/Health/docs/sdd.md |
| **Open MCT** | Ames mission-control framework. Telemetry/time/composition model. | https://github.com/nasa/openmct |
| **Flight rules** | Pre-mission rules that "delineate responsibility and authority" and give "criteria from which real-time decisions are made". Split into general and specific rules. | https://www.nasa.gov/wp-content/uploads/static/history/alsj/a11/A11MissRules.pdf |
| **Test Like You Fly** | Engineering philosophy, not a NASA standard. The most rigorous checklist is Aerospace Corp TOR-2009(8591)-15. | https://s3vi.ndc.nasa.gov/ssri-kb/static/resources/TOR2009-8591-15.pdf |

## B.2 Classification: where Miao would map (analogically)

NPR 7150.2D §3.5.1 [SWE-020] defines classes A–F in Appendix D. Excerpts as reproduced in SWEHB 7.02:

- **Class C**: mission support. Includes "ground mission support software used for secondary mission objectives, real-time analysis, and planning".
- **Class D**: basic science / engineering design. Includes "(f) Ground software that provides decision support for non-mission critical situations". Excludes flight software and software that operates a major facility.
- **Class E**: design concept / research. "A defect… may affect the productivity of a single user or small group"; "cannot be safety-critical". Excludes "software used in technical decisions concerning operational systems".
- **Class F**: general-purpose business and IT. "A defect… likely to affect the productivity of multiple users". The CIO has authority.

**Safety-critical** (NASA-STD-8739.8B §4.2) means software that causes or contributes to a hazard, controls or mitigates one, controls safety-critical functions, mitigates damage, or detects and corrects a potentially hazardous state, "as determined by and traceable to hazard analysis". All safety-critical software must be Class D or higher.

**Recommendation**
- Adopt **Class D as the baseline profile** for the whole product (64 "X" requirements, counted from Appendix C).
- Add selected **Class C** items that are cheap and high-value (list below).
- Treat the control path (tool gateway, guard chain, safe-mode FSM, kill switches, approval gate, audit sealer) as **"mission-critical" in the analog sense**, and voluntarily implement **SWE-134 a–l**.

Why not Class E: E invokes only 12 requirements (planning, classification, mapping matrix, SA, safety determination, cybersecurity assessment). That is too thin for software that takes autonomous actions on someone's behalf. It also conflicts with E's own exclusion of software making operational decisions.

Why not safety-critical: Miao has no NASA-style hazard to life or vehicle. However, under 8739.8B the honest move is to run a **project-defined hazard analysis**: financial loss, data exfiltration, unauthorized communications sent in the owner's name, irreversible deletions. Any component traceable to those hazards then gets the SWE-134 treatment. That keeps the mapping honest without claiming "safety-critical" status.

**Class D invoked set** (from the Appendix C HTML table, parsed positionally):
033, 013, 024, 034, 036, 037, 039, 040, 042, 139, 121, 125, 027, 015, 151, 174, 016, 046, 020, 176, 022, 205, 023, 134, 219, 220, 206, 147, 148, 156, 154, 157, 159, 207, 185, 052, 050, 053, 054, 055, 061, 135, 062, 186, 063, 065, 066, 068, 071, 189, 192, 075, 077, 194, 195, 196, 079, 080, 081, 082, 083, 084, 085, 201.
SWE-023/134/219/220 are conditional on having safety-critical software.

**Class C additions worth cherry-picking**
- SWE-057 recorded architecture; SWE-058 design.
- SWE-086 risk management; SWE-087/088/089 peer reviews with checklists.
- SWE-191 regression testing including security.
- SWE-210 adversarial-action detection data.
- SWE-202 severity levels; SWE-203 OSS non-conformance assessment.
- SWE-073 validation on a high-fidelity simulation (this is the twin).
- SWE-190 coverage by test execution; SWE-211 OSS tested to the same level.
- SWE-193 acceptance tests for "loaded or uplinked data, rules, and code". This is Class A/B only in the NPR, but it is the single best fit for guardrail policies, prompts and flight rules.

## B.3 Requirement-to-practice matrix

Legend: **A** = genuinely applicable; **A\*** = applicable by analogy (voluntary); **T** = theatre for this product (do not claim).

| # | Requirement (doc §) | What it means in practice | How Miao satisfies it | Evidence artifact | Verdict |
|---|---|---|---|---|---|
| 1 | NPR 7150.2D §3.5.1 SWE-020, §3.5.2 SWE-176 Classification and records | Classify each subsystem; keep the record | `docs/assurance/classification.md`: per-subsystem analog class (control path = D + SWE-134; console UI = D; analytics = E) with rationale | Signed, versioned classification record | A |
| 2 | §3.1.13 SWE-125, §3.1.11 SWE-139 Requirements Mapping Matrix | Matrix of every invoked SWE: comply / tailor / N-A with rationale | `assurance/rmm.yaml` generated into a table. Tailored-out rows say why (e.g., SWE-032 CMMI N/A) | RMM in repo, reviewed each release | A |
| 3 | §3.1.3 SWE-013 Software plans incl. security | Lightweight SDP + security plan | One "Software Development & Assurance Plan" covering lifecycle, CM, test, security, release | SDAP doc | A |
| 4 | §3.7.3 SWE-134(a) Initialize to known safe state at first start and restart | Boot into a defined safe state | Boot in **SAFE** (tools disabled). Promote to NOMINAL only after self-test: audit chain verify, config checksum, guard chain health ping | Boot-sequence test; audit event `BOOT→SAFE→NOMINAL` with checks listed | A\* |
| 5 | SWE-134(b) Safe transitions between predefined states | Explicit FSM; no implicit states | Transition table NOMINAL/DEGRADED/SAFE/HALTED as data. Illegal transitions raise and are logged. Exhaustive transition tests (all from×to pairs) | FSM table plus generated state diagram plus 16-pair test report | A\* |
| 6 | SWE-134(c) Termination to a known safe state | Shutdown and kill leave nothing half-done | On SIGTERM/kill: stop intake, cancel in-flight tool calls with compensations, seal a final audit block, persist SAFE as the restart state | Chaos test: kill -9 during tool execution, then restart into SAFE with chain intact | A\* |
| 7 | SWE-134(d) Overrides need two independent operator actions | No single-click override | Approve high-risk, clear kill switch, exit SAFE: two-step UI (§A.4) plus server-side check of two distinct requests with a nonce | E2E test; audit shows both actions | A\* |
| 8 | SWE-134(e) Reject out-of-sequence commands | Ordering and replay protection | Approval tokens bound to `{call_id, twin_rehearsal_hash, seq}`. Monotonic sequence per goal. Idempotency keys. Stale approvals rejected | Replay/out-of-order test suite | A\* |
| 9 | SWE-134(f) Detect inadvertent memory/data modification and recover | Integrity of state | Hash-chained audit with periodic verification. Config/policy checksums (analog of the cFS CheckSum app). Mismatch triggers SAFE | Tamper test: flip a byte, expect detection and SAFE | A\* |
| 10 | SWE-134(g) Integrity checks on inputs/outputs | Validate at boundaries | Strict schema validation of tool args and tool results (pydantic strict). Output handling per OWASP LLM05 | Fuzz/property tests; rejection metrics | A\* |
| 11 | SWE-134(h) Prerequisite checks before critical commands | Preconditions gate execution | Twin rehearsal must pass; guard-chain preconditions; approval present; budget available | Precondition matrix per tool; tests | A\* |
| 12 | SWE-134(i) No single event can initiate a hazard | Defense in depth | High-risk tools require guard chain PASS **and** human approval **and** a twin match. Any single component failure fails closed | Fault-injection results per guard stage | A\* |
| 13 | SWE-134(j) Respond to off-nominal in time | Bounded detection-to-response latency | Per-stage timeouts. Guard timeout = BLOCK. Watchdog → DEGRADED within N s. SLOs published | Latency/timeout test report; SLO dashboard | A\* |
| 14 | SWE-134(k, l) Error handling; can place system in safe state | Always commandable to safe | Kill switches plus an always-available "Enter SAFE" command (console, CLI and API) that is independent of the LLM path | Drill log: SAFE entered from each interface | A\* |
| 15 | §3.7.4 SWE-219 100% MC/DC for safety-critical | Every condition independently shown to affect a decision | Apply **only** to the small pure guard-decision kernel (policy evaluator). Mature Python MC/DC tooling is scarce, so use exhaustive truth-table / property-based tests. Elsewhere use branch coverage targets | Truth-table test report for the kernel | A\* (kernel only); T if claimed product-wide |
| 16 | §3.7.5 SWE-220 Cyclomatic complexity ≤15 | Keep critical code simple | CI gate on the control-path modules (radon / ruff `C901` with max 15); waivers recorded | CI report plus waiver list | A\* |
| 17 | §4.4.4 SWE-135, §3.11.7 SWE-185 Static analysis for defects, security, coverage, complexity | Automated analysis, every build | ruff, mypy `--strict`, bandit/semgrep; tsc strict, eslint; zero-warning policy on the control path | CI logs; SARIF uploads | A |
| 18 | §4.4.3 SWE-061, §3.11.6 SWE-207 Coding standard with secure coding | Written standard | Coding standard = Power-of-10 *translated* (B.4) + OWASP ASVS controls | `CODING_STANDARD.md` + linter config | A |
| 19 | §3.12.1 SWE-052 Bi-directional traceability (Class D: reqs↔hazards, reqs↔verification, reqs↔non-conformances) | Each requirement ↔ test ↔ hazard ↔ issue | Requirement IDs in `requirements.yaml`; tests tagged `@req("MIAO-GW-012")`; CI builds the trace matrix and fails on orphans | Generated trace matrix per release | A |
| 20 | §4.1.2–4.1.7 SWE-050/053/054/055 Requirements captured, changed, validated | Managed requirements | Requirements file under CM; changes through PRs; validation through owner acceptance scenarios | Requirements change log | A |
| 21 | §4.2.3 SWE-057 (Class C) Recorded architecture incl. valid/invalid modes | Architecture doc with interfaces and modes | ADRs plus architecture doc: component/port view (B.5), mode table, interface specs | `docs/architecture/` | A (cherry-pick) |
| 22 | §4.5.2–4.5.7 SWE-065/066/068/071 Test plans, procedures, reports; test against requirements | Requirement-based testing | Test plan; pytest/playwright suites tied to requirement IDs; machine-readable reports archived per release | JUnit XML + coverage + report | A |
| 23 | §4.5.9 SWE-189 Coverage measured and reported (D); SWE-190 measured by test execution (C) | Coverage with rationale for gaps | Coverage per module. Uncovered code classified per NPR note (missing requirement / missing test / dead / deactivated) | Coverage report + uncovered-code rationale | A |
| 24 | §4.5.8 SWE-073 (Class C) Validate on target platform or high-fidelity simulation | **Test like you fly** | The digital twin must run the **same** gateway and guard-chain code and config hash as production. Only tool side effects are stubbed. Staging = production images | Twin/prod parity check (config hash, code SHA) recorded on every rehearsal | A (key) |
| 25 | §4.5.13 SWE-193 (A/B) Acceptance tests for loaded/uplinked data, rules, code | Data and rules that change behavior get tested like code | Guard policies, prompts, tool registry and flight rules are "uplinked rules": versioned, each change needs a nominal + off-nominal acceptance suite before activation | Policy test suite results attached to each policy version | A\* (strong fit) |
| 26 | §4.5.11 SWE-191 Regression incl. security | No regressions; no new vulnerabilities | Full regression plus red-team prompt-injection corpus on every release | Regression report | A |
| 27 | §4.5.12 SWE-192 Test requirements that trace to hazards | Hazard mitigations proven by test | Each hazard (financial, exfiltration, impersonation, deletion) maps to tests that show the mitigation fires | Hazard ↔ test matrix | A |
| 28 | §4.4.7 SWE-063 Version description per release | Release notes with contents | Release notes + SBOM + provenance + known issues | VDD per tag | A |
| 29 | §5.1 SWE-079–085 Configuration management | CM plan, CIs, control levels, audits | Git + protected branches; CIs include code, policies, prompts, model IDs, tool dictionary, lockfiles; release audit = rebuild from tag and compare digests | CM plan; release audit record | A |
| 30 | §5.5.1 SWE-201 non-conformances; SWE-202 severity levels (C) | Defect tracking with ≥4 severity classes | Issue tracker with severities adapted from the NPR note: S1 harm/irreversible loss · S2 mission (goal) failure · S3 user-visible with workaround · S4 other | Defect DB export | A |
| 31 | §3.1.14 SWE-027, §3.11.2 SWE-156, §5.5.3 SWE-203 OSS/COTS assessment | Know and track third-party risk | SBOM (CycloneDX/SPDX), OSV/Dependabot scanning, license review, LLM-provider risk assessment | SBOM + scan reports + vendor risk notes | A |
| 32 | §3.11.3 SWE-154 Cyber risks and mitigations | Threat model | STRIDE + OWASP LLM Top 10 (2025) + OWASP Agentic Top 10 (2026) threat model, per tool | Threat model doc | A |
| 33 | §3.11.8 SWE-210 (C) Data for detecting adversarial actions | Collect and alert on attack observables | Telemetry: failed auth, guard BLOCK rate, injection-detector hits, anomalous tool-call patterns; events at WARNING_HI | Detection rules + sample alerts | A |
| 34 | §3.11.4 SWE-157 Protections per NASA-STD-1006 | Space-system protection standard | NASA-STD-1006 targets space systems. Use ASVS 5.0 L2 for comms/auth instead and say so | — | T (substitute ASVS) |
| 35 | §3.6.1 SWE-022 + NASA-STD-8739.8B §4.3 Software assurance | SA tasks confirm and assess engineering work | A separate "assurance pass" checklist per release by someone other than the author (even in a small team): confirm traceability, test completeness, static analysis results | SA checklist per release | A (scaled) |
| 36 | NASA-STD-8739.8B §4.4 IV&V (technical, managerial, financial independence) | Independent organization does V&V | Cannot be claimed. Closest honest analog: an external third-party security assessment/pentest and an external code review of the control path | Third-party report | T as "IV&V"; A\* as "independent assessment" |
| 37 | §3.9.2 SWE-032 CMMI-DEV ML2/3 | Organizational appraisal (Class A/B only) | Not applicable | — | T |
| 38 | §3.2 SWE-015/151/174 cost models, Center repository | NASA program management | Not applicable beyond internal estimates | — | T |
| 39 | §3.10.2 SWE-148 Contribute reuse candidates to NASA | NASA internal | N/A | — | T |
| 40 | §4.4.8 SWE-136 (C) Validate/accredit dev tools | Trust the toolchain | Pinned toolchain versions, reproducible builds, SLSA provenance | Lockfiles + provenance attestation | A\* (via SLSA) |

## B.4 Power of Ten, translated (not literally applied)

| P10 rule (verbatim intent) | Literal use in Python/TS | Miao translation |
|---|---|---|
| 1 Simple control flow, no recursion | Partly | No recursion in the guard chain or planner execution. Planner depth is explicitly bounded. |
| 2 All loops have a fixed upper bound | **Highly relevant to agents** | Every agent loop has hard caps: max steps, max tool calls, wall-clock, token and cost budget. Exceeding a cap triggers an assertion, the goal fails, and an audit event is written. Never "loop until done". |
| 3 No dynamic memory allocation after init | Not applicable to GC'd runtimes | Translate as bounded resources: bounded queues (SSE buffers, event backlog), memory limits per worker, back-pressure. |
| 4 Functions ≤ ~60 lines | Applicable | Lint rule on control-path modules. |
| 5 ≥2 assertions per function, side-effect-free, explicit recovery | Applicable in spirit | Runtime invariants (pydantic validators, explicit `if not … : return Error`) on control-path functions. A failed invariant leads to fail-closed BLOCK and DEGRADED, not a crash. |
| 6 Smallest scope | Applicable | No module-level mutable state in guards; dependency injection. |
| 7 Check all return values / validate parameters | Applicable | mypy strict; no bare `except`; Result types for tool outcomes; eslint `no-floating-promises`. |
| 8 Limit preprocessor | N/A | Analog: limit feature-flag combinations on the control path (each flag doubles the test space, P10's own rationale). |
| 9 Restrict pointers / no function pointers | N/A literally | Analog: no dynamic dispatch by string to tools. Tools are resolved only through the registered dictionary (B.5). |
| 10 All warnings on, zero warnings, daily static analysis | Applicable | CI with zero warnings on the control path; scheduled daily scan. |

## B.5 Architecture patterns to borrow (cFS / F Prime / Open MCT)

1. **Component/port model (F Prime).**
   - Model each guard stage as a component with typed ports: `in: ToolCallRequest (sync, guarded)` and `out: Verdict`.
   - Active components (own queue and thread) for I/O-bound stages; passive for pure evaluators.
   - Generate the console's schematic **from the same topology definition** so the diagram cannot drift from the real chain.
2. **Command and telemetry dictionaries (F Prime/FPP).**
   - The tool registry becomes a versioned **command dictionary**: id, schema, risk class, preconditions, required approvals, compensating action, and the flight rules that apply.
   - Metrics become a **telemetry dictionary** with units, format, `domain`/`range` hints (Open MCT) and limits (FPP).
   - The console reads both dictionaries, which removes hard-coded UI.
3. **Event logging with severities and throttling (FPP).** Every audit event carries severity, component id, event id, format string and args. That gives bilingual rendering from a format string, not free text.
4. **Health monitoring (Svc::Health, cFS HS).**
   - Ping each active component every tick.
   - A missed ping within its timeout raises a FATAL event and the FSM moves to DEGRADED. Repeated misses move it to SAFE.
   - The watchdog is "stroked" only while all pings pass (Svc::Health HTH-007).
5. **Limit checker + stored command sequences (cFS LC + SC).**
   - A limit violation, for example spend rate, BLOCK rate or error rate, triggers a **pre-approved Relative Time Sequence**, such as: pause goal, enter DEGRADED, notify owner.
   - This is the code form of a flight rule.
6. **Flight rules as code.**
   - Versioned, reviewed rules in a general/specific structure, following the Apollo format: condition | phase/mode | required response | notes.
   - Each automatic transition cites its rule ID in the audit event.
   - The console shows the rule ID wherever an action is disabled.
7. **Open MCT telemetry model.** `subscribe` (SSE realtime) plus `request(start, end)` (historical) behind one provider interface, plus the `latest` and `minmax` strategies for the 24h chart's downsampling.
8. **Fault management (FDIR).**
   - Detection (limits, health, integrity), isolation (disable the single tool, connector or agent, not the whole system, where possible), recovery (pre-planned sequences).
   - Per the SWEHB/HR-37 note, when recovery isn't possible, isolation alone must prevent harm, which is fail-closed.
   - Cite NASA-HDBK-1002 only as a 2012 draft.

## B.6 Non-NASA high-assurance norms an enterprise buyer will expect

| Norm | Current version (verified where noted) | What to do |
|---|---|---|
| **NIST SP 800-218 SSDF** | v1.1 final (2022-02-03). **v1.2 (SP 800-218r1) initial public draft 2025-12-17**, comments closed 2026-01-30, final pending. SP 800-218A (generative-AI profile) final. https://csrc.nist.gov/projects/ssdf/publications | Map practices PO/PS/PW/RV to the artifacts in B.3. 800-218A mostly targets model producers; cite it for the AI-specific tasks Miao touches (prompt/policy integrity, provenance of model configs). |
| **SLSA** | **v1.2 current** (v1.1 retired). Build track L1 provenance exists → L2 hosted, signed provenance → L3 isolated builds with signing secrets kept away from build steps. v1.2 adds a Source track. https://slsa.dev/spec/v1.2/ | Target Build L2 now and L3 via a hosted CI with isolated runners plus artifact attestations. |
| **OWASP ASVS** | **5.0.0 released 2025-05-30**. https://owasp.org/www-project-application-security-verification-standard/ | Target L2 for the API and console. Publish the self-assessment. |
| **OWASP Top 10 for LLM Apps** | **2025**: LLM01 Prompt Injection … LLM06 **Excessive Agency** … LLM10 Unbounded Consumption. https://genai.owasp.org/llm-top-10/ | LLM06 mitigations (human approval for high-impact actions, authorization in downstream systems, not in the LLM) are exactly Miao's gateway and approvals. Make that mapping explicit. |
| **OWASP Top 10 for Agentic Applications** | **2026** (announced Dec 2025), ASI01 Agent Goal Hijack, ASI02 Tool Misuse & Exploitation, ASI03 Identity & Privilege Abuse … **[partially verified via secondary sources]** | Use it in the threat model; verify exact names on genai.owasp.org. |
| **SOC 2** (AICPA Trust Services Criteria) **[from prior knowledge]** | TSC 2017 with revised points of focus (2022). Security is required; Availability, Processing Integrity, Confidentiality and Privacy are optional. | For a personal product, "SOC 2-ready controls" at most. An actual Type II needs an auditor and an operating period. Processing Integrity fits the sealed audit trail. |
| **NIST AI RMF 1.0 / AI 600-1; ISO/IEC 42001:2023** **[from prior knowledge]** | AI governance frameworks. | Optional. Mention only if a governance program actually exists. |

## B.7 What to say publicly (and what never to say)

- **OK:** "Engineering practices mapped to NASA NPR 7150.2D (self-assessed against a Class D profile, with SWE-134 safe-state behaviors adopted for the control path)." "Inspired by NASA cFS/F Prime fault-protection patterns." "Requirements mapping matrix available on request."
- **Never:**
  - "NASA-certified", "NASA-compliant", "NASA-approved", "NASA-grade", "flight-qualified", or "IV&V'd".
  - Using the NASA insignia, logo or name as an endorsement. NASA emblem use is restricted under 14 CFR Part 1221 **[from prior knowledge]**.
  - Implying NASA reviewed anything.
- **Caveats to state:**
  - NPR 7150.2D is an internal NASA directive and expires 2027-03-08.
  - The class mapping is an analogy chosen by Miao, not a NASA determination. Classification authority rests with NASA Technical Authorities, per §3.5.1.

## B.8 Evidence pack (what to actually produce, smallest useful set)

1. Classification record + RMM (B.3 rows 1–2)
2. Software Development & Assurance Plan
3. Hazard analysis (project-defined hazards) ↔ requirements ↔ tests trace matrix (CI-generated)
4. FSM spec + exhaustive transition tests + boot/kill/tamper drill logs
5. Command dictionary (tools) + telemetry dictionary (metrics, limits) + flight-rules file, each versioned with acceptance tests
6. CI evidence: static analysis (zero warnings on control path), coverage with uncovered-code rationale, complexity ≤15 report, regression + injection red-team results
7. Release VDD: notes + SBOM + SLSA provenance + known issues
8. Threat model (STRIDE + OWASP LLM 2025 + Agentic 2026) + ASVS 5.0 L2 self-assessment
9. Twin/prod parity record per rehearsal (test like you fly)
10. Independent assessment report (third-party pentest/code review), explicitly *not* called IV&V

---

## Open items / could not verify
- Whether NPR 7150.2E has been issued (none found as of 2026-10-25; 7150.2D expires 2027-03-08).
- Official full list of OWASP Agentic Top 10 (2026) category names.
- Official Linear shortcut list beyond the guide (for example `X` select, `J`/`K`).
- Stripe Sessions motion talks, Arc, Datadog, and Aladdin UI specifics: no primary sources found, so none of the rules rely on them.
- Whether the self-hosted Nunito Sans files include tabular figures (`tnum`). Check the font files.
