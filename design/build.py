#!/usr/bin/env python3
"""Build the vertciti DNA stylesheets from tokens.json.

    python3 design/build.py           # regenerate dist/
    python3 design/build.py --check   # CI: fail if dist/ is stale or a contrast pair fails

tokens.json is the single source of truth. Never hand-edit dist/.
"""
import json
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

# (foreground, background, minimum ratio, label). Body text needs 4.5, large/bold UI and focus 3.0.
CONTRAST_PAIRS = [
    ("light.fg", "light.bg", 4.5), ("light.fg-2", "light.bg", 4.5), ("light.fg-3", "light.bg", 4.5),
    ("light.fg-3", "light.soft", 4.5), ("light.ok", "light.bg", 4.5), ("light.bad", "light.bg", 4.5),
    ("light.info", "light.bg", 4.5), ("light.on-warn", "light.warn", 4.5), ("light.fg", "light.soft", 4.5),
    ("dark.fg", "dark.bg", 4.5), ("dark.fg-2", "dark.bg", 4.5), ("dark.fg-3", "dark.bg", 4.5),
    ("dark.fg-3", "dark.card", 4.5), ("dark.ok", "dark.bg", 4.5), ("dark.bad", "dark.bg", 4.5),
    ("dark.info", "dark.bg", 4.5), ("dark.on-warn", "dark.warn", 4.5), ("dark.fg", "dark.card", 4.5),
    ("brand.orange", "light.bg", 3.0), ("brand.orange", "dark.bg", 3.0),
]
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
    for fg, bg, need in CONTRAST_PAIRS:
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


def font_faces():
    # Self-hosted, same files as vertciti.com /assets/site/fonts/. URLs are relative to the CSS file,
    # so vendor dist/fonts/ next to dna.css. CJK falls through to the system stack (no CJK webfont).
    return "".join(
        f'@font-face{{font-family:"{face["family"]}";font-style:normal;font-weight:{face["weight"]};'
        f'font-display:swap;src:url({face["file"]}) format("woff2");unicode-range:{face["unicode-range"]}}}\n'
        for face in T["font"]["faces"]
    )


def tokens_css():
    f, lay, sh, mo, z = T["font"], T["layout"], T["shape"], T["motion"], T["z"]
    brand = "".join(f"--{k}:{v};" for k, v in T["color"]["brand"].items())
    static = (
        f"--font:{f['sans']};--mono:{f['mono']};"
        f"--w:{lay['max']};--gut:{lay['gutter']};--sec:{lay['section']};--tap:{lay['tap']};--btn-h:{lay['button']};"
        f"--radius:{sh['radius']};--focus-ring:{sh['focus']};--focus-offset:{sh['focus-offset']};"
        f"--lh-tight:{f['leading']['tight']};--lh-snug:{f['leading']['snug']};--lh-body:{f['leading']['body']};"
        + "".join(f"--tracking-{k}:{v};" for k, v in f["tracking"].items())
        + "".join(f"--fs-{k}:{v};" for k, v in f["size"].items())
        + f"--dur-fast:{mo['fast']};--dur-base:{mo['base']};--dur-slow:{mo['slow']};--ease:{mo['ease']};"
        f"--shadow-pop:{T['elevation']['pop']};"
        + "".join(f"--z-{k}:{v};" for k, v in z.items())
    )
    dark = theme_block("dark") + "--orange:#FF4713;--verd:" + T["color"]["brand"]["verd-dark"] + ";color-scheme:dark;"
    return (
        f":root{{{theme_block('light')}{brand}{static}color-scheme:light;}}\n"
        f"@media (prefers-color-scheme:dark){{:root:not([data-theme=\"light\"]){{{dark}}}}}\n"
        f":root[data-theme=\"dark\"]{{{dark}}}\n"
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
    semantic = ["bg", "fg", "fg-2", "fg-3", "soft", "line", "strong", "card", "ok", "warn", "on-warn", "bad", "info"]
    lines.append("  " + "".join(f"--color-dna-{k}:var(--{k});" for k in semantic))
    lines.append("  " + "".join(f"--color-dna-{k}:var(--{k});" for k in ("orange", "yellow", "green", "verd")))
    radii = ["xs", "sm", "md", "lg", "xl", "2xl", "3xl", "4xl"]
    lines.append("  " + "".join(f"--radius-{r}:0;" for r in radii))
    lines.append(f"  --font-sans:{T['font']['sans']};--font-mono:{T['font']['mono']};")
    lines.append(f"  --shadow-lg:{T['elevation']['pop']};--shadow-md:{T['elevation']['hairline']};")
    return "@theme {\n" + "\n".join(lines) + "\n}\n"


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
    return {"dist/dna.css": plain, "dist/dna-tailwind.css": tw}


def main():
    fails = contrast_failures()
    outputs = build()
    if "--check" in sys.argv:
        stale = [p for p, body in outputs.items() if not (HERE / p).exists() or (HERE / p).read_text(encoding="utf-8") != body]
        for f in fails:
            print("CONTRAST FAIL", f)
        for p in stale:
            print("STALE", p, "— run python3 design/build.py")
        sys.exit(1 if fails or stale else 0)
    if fails:
        for f in fails:
            print("CONTRAST FAIL", f)
        sys.exit(1)
    for p, body in outputs.items():
        (HERE / p).parent.mkdir(exist_ok=True)
        (HERE / p).write_text(body, encoding="utf-8")
        print("wrote", p, len(body), "bytes")


if __name__ == "__main__":
    main()
