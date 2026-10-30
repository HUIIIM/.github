"""Tests for standards/check_messaging_dns.py with stubbed DNS (no network).

    python3 -m unittest standards/test_messaging_dns.py
"""
import sys
import unittest
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parent))
import check_messaging_dns as dns

GOOD = {
    "example.com": ["v=spf1 include:_spf.example.net -all"],
    "_dmarc.example.com": ["v=DMARC1; p=reject; rua=mailto:d@example.com"],
    "_mta-sts.example.com": ["v=STSv1; id=1"],
    "_smtp._tls.example.com": ["v=TLSRPTv1; rua=mailto:t@example.com"],
}


def run(records, selector=None, caa=("0 issue \"letsencrypt.org\"",)):
    def txt(name):
        return list(records.get(name, []))

    def resolve(name, rtype):
        return list(caa) if rtype == "CAA" else txt(name)

    with mock.patch.object(dns, "resolve_txt", txt), mock.patch.object(dns, "_resolve", resolve), \
            mock.patch.object(dns, "https_get", lambda url: "version: STSv1\nmode: enforce\n"):
        return dns.check("example.com", selector)


class UnevaluatedMustFails(unittest.TestCase):
    def status(self, rep, rule):
        return next(st for r, _lvl, st, _d in rep.rows if r == rule)

    def test_missing_selector_is_unmet_and_fails(self):
        rep = run(GOOD)
        self.assertEqual(self.status(rep, "AUTH-2 DKIM"), "UNMET")
        self.assertTrue(rep.fail)

    def test_dmarc_quarantine_is_unmet_and_fails(self):
        recs = dict(GOOD, **{"_dmarc.example.com": ["v=DMARC1; p=quarantine; rua=mailto:d@example.com"]})
        rep = run(recs)
        self.assertEqual(self.status(rep, "AUTH-3 DMARC"), "UNMET")
        self.assertTrue(rep.fail)

    def test_should_without_evidence_is_only_a_warning(self):
        rep = dns.Report()
        rep.add("AUTH-6 BIMI", "SHOULD", None, "none")
        self.assertEqual(rep.rows[0][2], "WARN")
        self.assertFalse(rep.fail)


if __name__ == "__main__":
    unittest.main()
