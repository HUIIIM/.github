#!/usr/bin/env python3
"""Build the vertciti DNA stylesheets from tokens.json.

    python3 design/build.py           # regenerate dist/ and preview/surfaces.html
    python3 design/build.py --check   # CI: fail if an output is stale, a contrast pair fails, or a
                                      # size leaves the QA-gate scales (website-qa-gates A1/A2, #101)

tokens.json is the single source of truth. Never hand-edit dist/ or preview/surfaces.html.
Outputs: dist/dna.css, dist/dna-tailwind.css, dist/tokens.dtcg.json (W3C DTCG 2025.10 export),
preview/surfaces.html (every text token on every surface, for the rendered-contrast gate).
"""
import json
import re
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
T = json.loads((HERE / "tokens.json").read_text(encoding="utf-8"))
BASE = (HERE / "src" / "base.css").read_text(encoding="utf-8")
VERSION = T["version"]

# Tailwind palette families → DNA scale. Families not listed keep Tailwind defaults
# only if an app uses them on purpose; everything common is pulled into the DNA.
TW_FAMILIES = {
    "neutral": ["gray", "slate", "zinc", "neutral", "stone"],
    "orange": ["orange"],
    "yellow": ["yellow", "amber"],
    "green": ["green", "emerald", "lime"],
    "verd": ["teal", "cyan", "sky", "blue", "indigo"],
    "red": ["red", "rose", "pink"],
    # Off-DNA hues collapse to the neutral scale so stray accents read as grey, not as new brand colours.
    "neutral_alias": ["purple", "violet", "fuchsia"],
}

# Themes (light/dark = page themes; ink/accent = inverse surfaces scoped to components).
THEMES = ("light", "dark", "ink", "accent")
SURFACES = ("bg", "soft", "card")                       # every place text can sit inside a theme
TEXT = ("fg", "fg-2", "fg-3", "ok", "bad", "info")      # every token used as text colour
# Scoped inverse surfaces: these selectors re-declare the whole theme locally, so everything inside
# follows the surface (A11Y-3). Generated, so component CSS never carries a raw colour (SOTA DES-2).
SURFACE_SELECTORS = {"ink": ".dna-card--ink,.dna-utility,.dna-code", "accent": ".dna-card--accent"}


def contrast_pairs():
    """The full matrix: every text token on every surface of every theme (4.5:1, WCAG 1.4.3 -- disabled
    controls are not exempt here), on-warn on warn, and the pointer (focus ring, current-item marker)
    on every surface at 3:1 (WCAG 1.4.11). Hand-picked pairs missed dark badges on cards (#40 DES-2)."""
    pairs = []
    for t in THEMES:
        for srf in SURFACES:
            pairs += [(f"{t}.{x}", f"{t}.{srf}", 4.5) for x in TEXT]
            pairs.append((f"{t}.pointer", f"{t}.{srf}", 3.0))
        pairs.append((f"{t}.on-warn", f"{t}.warn", 4.5))
    pairs.append(("brand.on-yellow", "brand.yellow", 4.5))  # ::selection, skip link
    return pairs
SCALE_TEXT_STEPS = (600, 700, 800, 900)  # must pass 4.5 on white and on step 50
SCALE_DARK_STEPS = (200, 300)            # must pass 4.5 on neutral-900 (dark-mode text)
# neutral-400 is the most common "muted text" class in our apps (text-gray-400), so it must pass on white too.
NEUTRAL_MUTED_STEP = "400"


def lum(hex_color):
    rgb = [int(hex_color[i:i + 2], 16) / 255 for i in (1, 3, 5)]
    rgb = [c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4 for c in rgb]
    return 0.2126 * rgb[0] + 0.7152 * rgb[1] + 0.0722 * rgb[2]


def ratio(a, b):
    la, lb = lum(a), lum(b)
    return (max(la, lb) + 0.05) / (min(la, lb) + 0.05)


def color(path):
    group, key = path.split(".")
    return T["color"][group][key]


def contrast_failures():
    fails = []
    for fg, bg, need in contrast_pairs():
        r = ratio(color(fg), color(bg))
        if r < need:
            fails.append(f"{fg} on {bg}: {r:.2f} < {need}")
    scales = T["color"]["scale"]
    dark_bg = scales["neutral"]["900"]
    for name, steps in scales.items():
        for step in SCALE_TEXT_STEPS:
            for bg in ("#FFFFFF", steps["50"]):
                r = ratio(steps[str(step)], bg)
                if r < 4.5:
                    fails.append(f"{name}-{step} on {bg}: {r:.2f} < 4.5")
        if name == "neutral":
            r = ratio(steps[NEUTRAL_MUTED_STEP], "#FFFFFF")
            if r < 4.5:
                fails.append(f"neutral-{NEUTRAL_MUTED_STEP} on #FFFFFF: {r:.2f} < 4.5")
        for step in SCALE_DARK_STEPS:
            r = ratio(steps[str(step)], dark_bg)
            if r < 4.5:
                fails.append(f"{name}-{step} on neutral-900: {r:.2f} < 4.5")
    return fails


def header(kind):
    return (
        f"/*! vertciti DNA v{VERSION} — {kind}\n"
        f" * GENERATED from HUIIIM/.github design/tokens.json by design/build.py. Do not edit by hand:\n"
        f" * change tokens.json upstream, rebuild, then re-vendor. Source: {T['source']}\n */\n"
    )


def theme_block(mode):
    return "".join(f"--{k}:{v};" for k, v in T["color"][mode].items())


def ms(v):
    return int(v.removesuffix("ms"))


def bezier(b):
    return "cubic-bezier(" + ",".join(f"{x:g}" for x in b) + ")"


def font_faces():
    # Self-hosted, same files as vertciti.com /assets/site/fonts/. URLs are relative to the CSS file,
    # so vendor dist/fonts/ next to dna.css. CJK falls through to the system stack (no CJK webfont).
    return "".join(
        f'@font-face{{font-family:"{face["family"]}";font-style:normal;font-weight:{face["weight"]};'
        f'font-display:swap;src:url({face["file"]}) format("woff2");unicode-range:{face["unicode-range"]}}}\n'
        for face in T["font"]["faces"]
    )


def tokens_css():
    f, lay, sh, z = T["font"], T["layout"], T["shape"], T["z"]
    dur, ease = T["motion"]["duration"], T["motion"]["easing"]
    brand = "".join(f"--{k}:{v};" for k, v in T["color"]["brand"].items())
    static = (
        f"--font:{f['sans']};--mono:{f['mono']};"
        f"--w:{lay['max']};--gut:{lay['gutter']};--sec:{lay['section']};--tap:{lay['tap']};--btn-h:{lay['button']};"
        f"--radius:{sh['radius']};--focus-ring:{sh['focus']};--focus-offset:{sh['focus-offset']};"
        f"--lh-tight:{f['leading']['tight']};--lh-snug:{f['leading']['snug']};--lh-body:{f['leading']['body']};"
        + "".join(f"--tracking-{k}:{v};" for k, v in f["tracking"].items())
        + "".join(f"--fs-{k}:{v};" for k, v in f["size"].items())
        + "".join(f"--motion-{k}:{v};" for k, v in dur.items())
        + "".join(f"--ease-{k}:{bezier(v)};" for k, v in ease.items())
        # v4.0 names kept as aliases so vendored apps keep working; values now follow Carbon productive.
        + "--dur-fast:var(--motion-fast-02);--dur-base:var(--motion-moderate-02);--dur-slow:var(--motion-slow-01);"
          "--ease:var(--ease-standard);"
        f"--shadow-pop:{T['elevation']['pop']};"
        + "".join(f"--z-{k}:{v};" for k, v in z.items())
    )
    dark = theme_block("dark") + "--orange:#FF4713;--verd:" + T["color"]["brand"]["verd-dark"] + ";color-scheme:dark;"
    surfaces = "".join(
        f"{sel}{{{theme_block(name)}{'color-scheme:dark;' if name == 'ink' else ''}}}\n"
        for name, sel in SURFACE_SELECTORS.items()
    )
    return (
        f":root{{{theme_block('light')}{brand}{static}color-scheme:light;}}\n"
        f"@media (prefers-color-scheme:dark){{:root:not([data-theme=\"light\"]){{{dark}}}}}\n"
        f":root[data-theme=\"dark\"]{{{dark}}}\n"
        + surfaces
        + f"@media print{{:root{{{theme_block('light')}}}}}\n"
    )


def split_base():
    base, components = BASE.split("/* @section components")
    return base.strip() + "\n", "/* @section components" + components.rstrip() + "\n"


def tailwind_theme():
    scales = T["color"]["scale"]
    lines = []
    for family, aliases in TW_FAMILIES.items():
        steps = scales["neutral" if family == "neutral_alias" else family]
        for alias in aliases:
            lines.append("  " + "".join(f"--color-{alias}-{s}:{v};" for s, v in steps.items()))
    semantic = ["bg", "fg", "fg-2", "fg-3", "soft", "line", "strong", "card", "ok", "warn", "on-warn", "bad", "info", "pointer"]
    lines.append("  " + "".join(f"--color-dna-{k}:var(--{k});" for k in semantic))
    lines.append("  " + "".join(f"--color-dna-{k}:var(--{k});" for k in ("orange", "yellow", "green", "verd")))
    radii = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"]
    lines.append("  " + "".join(f"--radius-{r}:0;" for r in radii))
    lines.append(f"  --font-sans:{T['font']['sans']};--font-mono:{T['font']['mono']};")
    lines.append(f"  --shadow-lg:{T['elevation']['pop']};--shadow-md:{T['elevation']['hairline']};")
    return "@theme {\n" + "\n".join(lines) + "\n}\n"


def hex_srgb(h):
    return {"colorSpace": "srgb", "components": [round(int(h[i:i + 2], 16) / 255, 4) for i in (1, 3, 5)], "hex": h.lower()}


def dtcg():
    """W3C DTCG 2025.10 export (https://www.designtokens.org/TR/2025.10/) of every token the format can
    represent: colours as srgb objects, px dimensions, ms durations, cubicBezier arrays, font weights and
    families. Fluid clamp() sizes have no DTCG type; they ride in $extensions with their CSS string."""
    ext = "com.vertciti.dna"
    color = {"$type": "color"}
    for group, vals in T["color"].items():
        if group == "scale":
            color["scale"] = {fam: {step: {"$value": hex_srgb(v)} for step, v in steps.items()} for fam, steps in vals.items()}
        else:
            color[group] = {k: {"$value": hex_srgb(v)} for k, v in vals.items()}

    def size(v):
        if v.endswith("px") and v[:-2].replace(".", "").isdigit():
            return {"$type": "dimension", "$value": {"value": float(v[:-2]), "unit": "px"}}
        return {"$extensions": {ext: {"css": v, "note": "fluid CSS value; no DTCG type"}}}

    f = T["font"]
    return {
        "$description": f"vertciti DNA v{VERSION} -- generated from design/tokens.json by design/build.py. Do not edit.",
        "$extensions": {ext: {"version": VERSION, "source": T["source"]}},
        "color": color,
        "font": {
            "family": {"$type": "fontFamily",
                       "sans": {"$value": [x.strip().strip('"') for x in f["sans"].split(",")]},
                       "mono": {"$value": [x.strip().strip('"') for x in f["mono"].split(",")]}},
            "weight": {"$type": "fontWeight", **{k: {"$value": v} for k, v in f["weight"].items()}},
            "size": {k: size(v) for k, v in f["size"].items()},
        },
        "layout": {k: size(v) for k, v in T["layout"].items()},
        "motion": {
            "duration": {"$type": "duration", **{k: {"$value": {"value": ms(v), "unit": "ms"}} for k, v in T["motion"]["duration"].items()}},
            "easing": {"$type": "cubicBezier", **{k: {"$value": v} for k, v in T["motion"]["easing"].items()}},
        },
    }


def dtcg_problems(node, path="", inherited=None):
    """Structural check of the export against the 2025.10 rules this file relies on."""
    out = []
    typ = node.get("$type", inherited) if isinstance(node, dict) else inherited
    if isinstance(node, dict) and "$value" in node:
        v = node["$value"]
        ok = {
            "color": lambda: isinstance(v, dict) and v.get("colorSpace") == "srgb" and len(v.get("components", [])) == 3
            and all(0 <= c <= 1 for c in v["components"]),
            "dimension": lambda: isinstance(v, dict) and isinstance(v.get("value"), (int, float)) and v.get("unit") in ("px", "rem"),
            "duration": lambda: isinstance(v, dict) and isinstance(v.get("value"), (int, float)) and v.get("unit") in ("ms", "s"),
            "cubicBezier": lambda: isinstance(v, list) and len(v) == 4 and all(isinstance(x, (int, float)) for x in v)
            and 0 <= v[0] <= 1 and 0 <= v[2] <= 1,
            "fontWeight": lambda: isinstance(v, (int, float)) and 1 <= v <= 1000,
            "fontFamily": lambda: isinstance(v, (str, list)),
        }.get(typ, lambda: False)()
        if not ok:
            out.append(f"{path or '/'}: invalid {typ} value {v!r}")
    elif isinstance(node, dict):
        for k, child in node.items():
            if not k.startswith("$"):
                out += dtcg_problems(child, f"{path}/{k}", typ)
    return out


def surfaces_page():
    """Every text-bearing token and component on every surface, both themes -- rendered by the contrast
    gate (standards/a11y/contrast_audit.js) so a colour that only fails on a card cannot ship again."""
    sample = ('<p>正文 fg <span style="color:var(--fg-2)">次要 fg-2</span> <span style="color:var(--fg-3)">辅助 fg-3</span> '
              '<a href="#">链接 link</a></p>'
              '<p><span class="dna-badge dna-badge--ok">已验证</span> <span class="dna-badge dna-badge--bad">否决</span> '
              '<span class="dna-badge dna-badge--info">信息</span> <span class="dna-badge dna-badge--warn">注意</span> '
              '<span class="dna-badge">徽章</span></p>'
              '<p><span class="dna-ev dna-ev--verified">已核实 · 2026-10-30</span> <span class="dna-ev dna-ev--estimate">估算</span> '
              '<span class="dna-ev dna-ev--demo">演示</span> <span class="dna-ev dna-ev--missing">缺失</span></p>'
              '<p class="dna-status"><span class="dna-dot dna-dot--ok"></span>正常 <span class="dna-dot dna-dot--bad"></span>故障</p>')
    soft = f'<div style="background:var(--soft);padding:12px">{sample}<button class="dna-btn dna-btn--sm" disabled>禁用</button></div>'
    blocks = [
        ("页面 bg", f'<div style="background:var(--bg);padding:12px">{sample}</div>'),
        ("软底 soft", soft),
        ("卡片 card", f'<div class="dna-card">{sample}</div>'),
        ("墨色卡 ink", f'<div class="dna-card dna-card--ink">{sample}<div style="background:var(--soft);padding:12px">{sample}</div></div>'),
        ("强调卡 accent", f'<div class="dna-card dna-card--accent">{sample}<div style="background:var(--soft);padding:12px">{sample}</div></div>'),
        ("提示 alert", '<div class="dna-alert dna-alert--bad"><strong>出错</strong> ' + sample + "</div>"),
    ]
    body = "\n".join(f'<section class="dna-section"><h2 class="dna-h2">{title}</h2>{html}</section>' for title, html in blocks)
    return ("<!doctype html>\n<!-- GENERATED by design/build.py from tokens.json. Do not edit. -->\n"
            '<html lang="zh"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            '<title>vertciti DNA · 表面矩阵</title><link rel="stylesheet" href="../dist/dna.css"></head>\n'
            f'<body><main class="dna-wrap"><h1 class="dna-h1">表面 × 文字 矩阵</h1>\n{body}\n</main></body></html>\n')


# Scales the fleet's website QA gates enforce on every product that vendors the DNA (#101).
# A1: no 13/15/17/19px font sizes. A2: margin/padding px values on the 4px scale below.
# Same patterns as website-qa-gates, so a DNA value that passes here passes there.
A1_SIZES = {13, 15, 17, 19}
A1 = re.compile(r"font-size:\s*(?:13|15|17|19)px\b")
A2_DECL = re.compile(r"(?:margin|padding)[^;{}\"'<>]*:[^;{}\"'<>]*")
A2_PX = re.compile(r"(?<![\w.])([0-9]+)px")
A2_SCALE = {0, 4, 8, 12, 16, 20, 24, 32, 40, 48, 56, 64, 80, 96, 120}


def scale_problems(files, font_tokens):
    """website-qa-gates A1/A2 violations in the given {name: css} files and font-size tokens."""
    out = []
    for name, css in files.items():
        for n, line in enumerate(css.splitlines(), 1):
            for m in A1.finditer(line):
                out.append(f"{name}:{n} A1 {m.group(0)}")
            for d in A2_DECL.finditer(line):
                bad = sorted({int(v) for v in A2_PX.findall(d.group(0))} - A2_SCALE)
                if bad:
                    out.append(f"{name}:{n} A2 {d.group(0).strip()} (off-scale: {', '.join(f'{b}px' for b in bad)})")
    for key, value in font_tokens.items():
        bad = sorted({int(v) for v in re.findall(r"(?<![\w.])([0-9]+)px", str(value))} & A1_SIZES)
        if bad:
            out.append(f"tokens.json font.size.{key} A1 {value} (a product using var(--fs-{key}) fails A1)")
    return out


def build():
    base, components = split_base()
    toks = tokens_css()
    plain = header("plain CSS (tokens + base + components)") + font_faces() + toks + base + components
    tw = (
        header("Tailwind v4 layer — import AFTER @import \"tailwindcss\"")
        + font_faces()
        + tailwind_theme()
        + toks
        + "@layer base {\n" + base + "}\n"
        + "@layer components {\n" + components + "}\n"
        # Tailwind hard-codes `rounded`, `rounded-t`, … to 0.25rem (no theme var). DNA corners are square,
        # so flatten every rounded-* except rounded-full (dots, avatars). Unlayered → beats the utilities layer.
        + '[class*="rounded"]:not([class*="rounded-full"]){border-radius:0}\n'
    )
    return {
        "dist/dna.css": plain,
        "dist/dna-tailwind.css": tw,
        "dist/tokens.dtcg.json": json.dumps(dtcg(), ensure_ascii=False, indent=1) + "\n",
        "preview/surfaces.html": surfaces_page(),
    }


def main():
    outputs = build()
    fails = contrast_failures() + dtcg_problems(json.loads(outputs["dist/tokens.dtcg.json"]))
    fails += scale_problems({"src/base.css": BASE, "dist/dna.css": outputs["dist/dna.css"],
                             "dist/dna-tailwind.css": outputs["dist/dna-tailwind.css"]},
                            T["font"]["size"])
    if "--check" in sys.argv:
        stale = [p for p, body in outputs.items() if not (HERE / p).exists() or (HERE / p).read_text(encoding="utf-8") != body]
        for f in fails:
            print("FAIL", f)
        for p in stale:
            print("STALE", p, "— run python3 design/build.py")
        sys.exit(1 if fails or stale else 0)
    if fails:
        for f in fails:
            print("FAIL", f)
        sys.exit(1)
    for p, body in outputs.items():
        (HERE / p).parent.mkdir(exist_ok=True)
        (HERE / p).write_text(body, encoding="utf-8")
        print("wrote", p, len(body), "bytes")


if __name__ == "__main__":
    main()
