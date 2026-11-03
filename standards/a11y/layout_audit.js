// Layout gate: catches what the contrast gate cannot see.
//   1. horizontal overflow (no sideways scroll at any width; WCAG 1.4.10 reflow)
//   2. collapsed text: a block whose text wraps about one character per line (a grid child squeezed to
//      1/12 width shipped in the DNA gallery this way, #40)
//   3. tap targets under 44 x 44 CSS px (AESTHETICS §7; WCAG 2.2 SC 2.5.8 sets 24 as the AA floor).
//      Links inside a run of text are exempt, as in 2.5.8; mark any other deliberate exception with
//      data-target-exempt="<reason>" so it stays reviewable.
// Exits non-zero on any failure.
//   node layout_audit.js <url> [--width 390] [--scheme light|dark] [--min 44]
const { chromium } = require('playwright');

const args = process.argv.slice(2);
const opt = (k, d) => { const i = args.indexOf(k); return i >= 0 ? args[i + 1] : d; };
const url = args[0];
const width = Number(opt('--width', 390));
const scheme = opt('--scheme', 'light');
const min = Number(opt('--min', 44));

(async () => {
  const b = await chromium.launch();
  const p = await b.newPage({ viewport: { width, height: 900 }, colorScheme: scheme });
  await p.goto(url, { waitUntil: 'load' });
  await p.waitForLoadState('networkidle', { timeout: 10000 }).catch(() => {});
  await p.evaluate(() => document.fonts.ready);
  const fails = await p.evaluate((minSize) => {
    const out = [];
    const de = document.documentElement;
    if (de.scrollWidth > de.clientWidth + 1) out.push({ kind: 'overflow', text: `page is ${de.scrollWidth}px wide in a ${de.clientWidth}px viewport` });
    const shown = (el) => { const r = el.getBoundingClientRect(); const s = getComputedStyle(el);
      return r.width > 0 && r.height > 0 && s.visibility !== 'hidden' && s.display !== 'none'; };

    // 2. collapsed text
    const seen = new Set();
    const w = document.createTreeWalker(document.body, NodeFilter.SHOW_TEXT);
    let n;
    while ((n = w.nextNode())) {
      const el = n.parentElement; const text = n.nodeValue.replace(/\s+/g, '');
      if (!el || seen.has(el) || text.length < 3 || ['SCRIPT', 'STYLE'].includes(el.tagName) || !shown(el)) continue;
      seen.add(el);
      const s = getComputedStyle(el); const fs = parseFloat(s.fontSize);
      const lh = s.lineHeight === 'normal' ? fs * 1.2 : parseFloat(s.lineHeight);
      const range = document.createRange(); range.selectNodeContents(n);
      const lines = new Set([...range.getClientRects()].map((r) => Math.round(r.top))).size;
      if (lines >= 3 && lines >= Math.ceil(text.length * 0.5)) {
        out.push({ kind: 'collapsed', text: `"${text.slice(0, 20)}" wraps to ${lines} lines in ${Math.round(el.getBoundingClientRect().width)}px (line-height ${Math.round(lh)}px)` });
      }
    }

    // 3. tap targets
    const inSentence = (el) => {
      if (getComputedStyle(el).display !== 'inline') return false;
      const parent = el.parentElement; if (!parent) return false;
      return [...parent.childNodes].some((c) => c !== el && c.nodeType === 3 && c.nodeValue.trim());
    };
    document.querySelectorAll('a[href], button, input, select, textarea, summary, [role="button"], [role="tab"], a[aria-disabled]').forEach((el) => {
      if (!shown(el) || el.closest('[data-target-exempt]') || inSentence(el)) return;
      const r = el.getBoundingClientRect();
      if (r.width < minSize - 0.5 || r.height < minSize - 0.5) {
        const label = (el.textContent || el.getAttribute('aria-label') || el.id || el.tagName).trim().slice(0, 20);
        out.push({ kind: 'target', text: `<${el.tagName.toLowerCase()}> "${label}" is ${Math.round(r.width)}x${Math.round(r.height)} (< ${minSize})` });
      }
    });
    return out;
  }, min);
  console.log(`${url} [${width}px ${scheme}] layout ${fails.length ? 'FAIL ' + fails.length : 'PASS'}`);
  for (const f of fails) console.log(`  ${f.kind}: ${f.text}`);
  await b.close();
  process.exit(fails.length ? 1 : 0);
})();
