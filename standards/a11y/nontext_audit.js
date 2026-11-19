// Non-text contrast gate (WCAG 2.2 SC 1.4.11; SOTA DS-1, #125). The text gate (contrast_audit.js)
// cannot see these: what tells a user "this is a control" and "this is where focus is".
//   1. component boundary: a control that is drawn as a shape (filled or outlined) must stand out from
//      what is painted around it by >= 3:1, through its fill or through its border. A control drawn as
//      text alone (no fill, no border: text buttons, links) is identified by its text, which 1.4.3 and
//      the text gate already cover, so it is skipped -- as the Understanding document allows.
//   2. focus indicator: Tab through the page like a keyboard user; every element that takes focus must
//      draw an outline or box-shadow whose colour reaches >= 3:1 against what is painted behind it.
// Colours are the rendered ones (any CSS colour via canvas, composited background stack). Mark a
// deliberate exception with data-nontext-exempt="<reason>" so it stays reviewable. Exits 1 on any failure.
//   node nontext_audit.js <url> [--width 390] [--scheme light|dark] [--min 3]
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const url = args[0];
const width = Number(opt('--width', 390));
const scheme = opt('--scheme', 'light');
const min = Number(opt('--min', 3));

const HELPERS = () => {
  const cv = document.createElement('canvas'); cv.width = cv.height = 1;
  const cx = cv.getContext('2d', { willReadFrequently: true });
  const memo = new Map();
  const parse = (c) => { if (!c) return null; if (memo.has(c)) return memo.get(c);
    cx.clearRect(0, 0, 1, 1); cx.fillStyle = 'rgba(0,0,0,0)'; cx.fillStyle = c; cx.fillRect(0, 0, 1, 1);
    const d = cx.getImageData(0, 0, 1, 1).data; const v = { r: d[0], g: d[1], b: d[2], a: d[3] / 255 }; memo.set(c, v); return v; };
  const over = (t, u) => ({ r: t.r * t.a + u.r * (1 - t.a), g: t.g * t.a + u.g * (1 - t.a), b: t.b * t.a + u.b * (1 - t.a), a: 1 });
  const lum = (c) => { const f = (x) => { x /= 255; return x <= 0.03928 ? x / 12.92 : ((x + 0.055) / 1.055) ** 2.4; };
    return 0.2126 * f(c.r) + 0.7152 * f(c.g) + 0.0722 * f(c.b); };
  const ratio = (a, b) => { const x = lum(a), y = lum(b); return (Math.max(x, y) + 0.05) / (Math.min(x, y) + 0.05); };
  // composited background painted behind `el` (el's own background included when self is true)
  const bgOf = (el, self) => {
    const chain = []; for (let e = self ? el : el.parentElement; e && e.nodeType === 1; e = e.parentElement) chain.push(e);
    let acc = { r: 255, g: 255, b: 255, a: 1 };
    for (const e of chain.reverse()) { const c = parse(getComputedStyle(e).backgroundColor); if (c && c.a > 0) acc = over(c, acc); }
    return acc;
  };
  const opac = (el) => { let o = 1; for (let e = el; e && e.nodeType === 1; e = e.parentElement) o *= Number(getComputedStyle(e).opacity); return o; };
  const shown = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
    return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };
  const label = (el) => `<${el.tagName.toLowerCase()}${el.className && typeof el.className === 'string' ? '.' + el.className.trim().split(/\s+/)[0] : ''}> "${(el.textContent || el.getAttribute('aria-label') || el.placeholder || el.id || '').trim().slice(0, 24)}"`;
  const firstShadowColour = (bs) => { if (!bs || bs === 'none') return null;
    const m = bs.match(/(rgba?\([^)]*\)|#[0-9a-f]{3,8}|[a-z]+\([^)]*\))/i); return m ? m[1] : null; };
  return { parse, over, ratio, bgOf, opac, shown, label, firstShadowColour };
};

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
  await p.goto(url, { waitUntil: 'load' });
  await p.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await p.evaluate(() => document.fonts.ready);
  await p.evaluate(`window.__nt = (${HELPERS.toString()})()`);

  // 1. component boundaries
  const fails = await p.evaluate((need) => {
    const { parse, over, ratio, bgOf, opac, shown, label } = window.__nt; const out = [];
    const sel = 'input:not([type=hidden]):not([type=checkbox]):not([type=radio]), select, textarea, button, [role="button"], a.dna-btn, [role="tab"]';
    for (const el of document.querySelectorAll(sel)) {
      if (!shown(el) || el.closest('[data-nontext-exempt]')) continue;
      const s = getComputedStyle(el); const around = bgOf(el, false); const o = opac(el);
      const fill = parse(s.backgroundColor);
      const sides = ['Top', 'Right', 'Bottom', 'Left'].filter((d) => parseFloat(s[`border${d}Width`]) > 0 && s[`border${d}Style`] !== 'none');
      const border = sides.length ? parse(s[`border${sides[0]}Color`]) : null;
      const hasFill = fill && fill.a > 0; const hasBorder = border && border.a > 0;
      if (!hasFill && !hasBorder) continue; // drawn as text only: identified by its text (1.4.3)
      const fillR = hasFill ? ratio(over({ ...fill, a: fill.a * o }, around), around) : 0;
      const borderR = hasBorder ? ratio(over({ ...border, a: border.a * o }, around), around) : 0;
      const best = Math.max(fillR, borderR);
      if (best < need - 0.005) {
        out.push({ kind: 'boundary', text: `${label(el)} fill ${fillR.toFixed(2)}:1, border ${borderR.toFixed(2)}:1 against its surround (< ${need})` });
      }
    }
    return out;
  }, min);

  // 2. focus indicators, reached by keyboard (focus-visible applies)
  const total = await p.evaluate(() => document.querySelectorAll('a[href], button, input, select, textarea, summary, [tabindex]:not([tabindex="-1"])').length);
  const seen = new Set();
  for (let i = 0; i < Math.min(total + 5, 400); i++) {
    await p.keyboard.press('Tab');
    const r = await p.evaluate((need) => {
      const { parse, over, ratio, bgOf, shown, label, firstShadowColour } = window.__nt;
      const el = document.activeElement;
      if (!el || el === document.body || !shown(el)) return null;
      const id = label(el) + '@' + Math.round(el.getBoundingClientRect().top + scrollY);
      if (el.closest('[data-nontext-exempt]')) return { id };
      const s = getComputedStyle(el); const behind = bgOf(el, false);
      const cand = [];
      if (s.outlineStyle !== 'none' && parseFloat(s.outlineWidth) > 0) cand.push(['outline', s.outlineColor]);
      const sh = firstShadowColour(s.boxShadow); if (sh) cand.push(['box-shadow', sh]);
      if (!cand.length) return { id, fail: `${label(el)} shows no focus indicator (no outline, no box-shadow)` };
      const scored = cand.map(([k, c]) => { const col = parse(c); return [k, col && col.a > 0 ? ratio(over(col, behind), behind) : 0]; });
      const best = scored.reduce((a, x) => (x[1] > a[1] ? x : a));
      return best[1] < need - 0.005 ? { id, fail: `${label(el)} focus ${best[0]} ${best[1].toFixed(2)}:1 against what is behind it (< ${need})` } : { id };
    }, min);
    if (!r) continue;
    if (seen.has(r.id)) break; // wrapped around
    seen.add(r.id);
    if (r.fail) fails.push({ kind: 'focus', text: r.fail });
  }

  console.log(`${url} [${width}px ${scheme}] non-text ${fails.length ? 'FAIL ' + fails.length : 'PASS'} (${seen.size} focus stops)`);
  for (const f of fails) console.log(`  ${f.kind}: ${f.text}`);
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
