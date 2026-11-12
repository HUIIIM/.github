"""Tests for the QA-gate scale check in design/build.py (#101). No network.

    python3 -m unittest design/test_build.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import build as b


def problems(css, tokens=None):
    return b.scale_problems({"x.css": css}, tokens or {})


class A1FontSizes(unittest.TestCase):
    def test_off_scale_sizes_fail(self):
        for px in (13, 15, 17, 19):
            self.assertEqual(len(problems(f".a {{ font-size: {px}px; }}")), 1, px)

    def test_scale_sizes_pass(self):
        for px in (12, 14, 16, 18, 20, 130):
            self.assertEqual(problems(f".a {{ font-size: {px}px; }}"), [], px)

    def test_font_size_token_is_checked(self):
        # a product writing font-size: var(--fs-md) renders the token value (#103 assessment)
        self.assertEqual(len(problems("", {"md": "17px"})), 1)
        self.assertEqual(len(problems("", {"xl": "clamp(15px,2vw,36px)"})), 1)
        self.assertEqual(problems("", {"md": "18px", "xl": "clamp(24px,2.6vw,36px)"}), [])


class A2Spacing(unittest.TestCase):
    def test_off_scale_padding_and_margin_fail(self):
        for decl in ("padding: 10px 12px", "padding: 0 28px", "margin-left: -2px",
                     "padding: clamp(40px, 6vw, 72px) 0", "padding-block: 14px"):
            self.assertEqual(len(problems(f".a {{ {decl}; }}")), 1, decl)

    def test_on_scale_values_pass(self):
        for decl in ("padding: 8px 12px", "margin: 0 auto", "padding: clamp(40px, 6vw, 64px) 0 clamp(24px, 4vw, 48px)",
                     "padding: 0 4px", "margin-top: 120px", "padding: .5em 1rem"):
            self.assertEqual(problems(f".a {{ {decl}; }}"), [], decl)

    def test_other_properties_are_not_spacing(self):
        self.assertEqual(problems(".a { gap: 10px; border-width: 2px; min-height: 44px; }"), [])

    def test_reports_file_and_line(self):
        out = problems(".a {}\n.b { padding: 28px; }")
        self.assertEqual(len(out), 1)
        self.assertTrue(out[0].startswith("x.css:2 A2"), out[0])


class Shipped(unittest.TestCase):
    def test_shipped_dna_is_on_the_scales(self):
        outputs = b.build()
        files = {"src/base.css": b.BASE, "dist/dna.css": outputs["dist/dna.css"],
                 "dist/dna-tailwind.css": outputs["dist/dna-tailwind.css"]}
        self.assertEqual(b.scale_problems(files, b.T["font"]["size"]), [])


if __name__ == "__main__":
    unittest.main()
