"""Tests for standards/ivv_gate.py (issue #84). No network.

    python3 -m unittest standards/test_ivv_gate.py
"""
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import ivv_gate as g

HEAD = "dcbbbd748a3c60fac06d299400c94cafeacc1ca4"
OLD = "1111111aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"


def pr(user="HUIIIM", head=HEAD):
    return {"user": {"login": user}, "head": {"sha": head}}


def commit(email="noreply@anthropic.com", date="2026-11-02T10:00:00Z"):
    return {"commit": {"author": {"email": email, "date": date}, "committer": {"email": email, "date": date}}}


def comment(body, at="2026-11-02T12:00:00Z", assoc="OWNER", login="HUIIIM", kind="User", cid=1):
    return {"id": cid, "body": body, "created_at": at, "author_association": assoc,
            "user": {"login": login, "type": kind}}


def app_comment(body, at="2026-11-02T12:00:00Z", cid=2):
    # the Claude GitHub App's comments carry author_association NONE (#50, comment 6569617526)
    return comment(body, at=at, assoc="NONE", login="claude[bot]", kind="Bot", cid=cid)


def verdict(sha, word, extra=""):
    return f"### 独立评估 · SOTA v1.0 · {sha[:7]}\n判定：{word}{extra}\n\n| 条款 | 结论 |"


class Scope(unittest.TestCase):
    def test_human_pr_is_out_of_scope(self):
        state, desc = g.evaluate(pr(), [commit("someone@example.com")], [])
        self.assertEqual(state, "success")
        self.assertIn("outside IVV scope", desc)

    def test_claude_committer_is_in_scope(self):
        c = commit("someone@example.com")
        c["commit"]["committer"]["email"] = "noreply@anthropic.com"
        self.assertTrue(g.in_scope(pr(), [c]))

    def test_claude_app_opened_pr_is_in_scope(self):
        self.assertTrue(g.in_scope(pr(user="claude[bot]"), [commit("x@y.z")]))

    def test_claude_app_commit_identity_is_in_scope(self):
        # e.g. 781e62a in #72: authored as claude[bot] in a PR opened by HUIIIM
        bot = commit(email="209825114+claude[bot]@users.noreply.github.com")
        self.assertTrue(g.in_scope(pr(), [bot]))
        by_login = commit(email="someone@example.com")
        by_login["author"] = {"login": "claude[bot]"}
        self.assertTrue(g.in_scope(pr(), [by_login]))

    def test_bot_card_pr_is_out_of_scope(self):
        bot = "41898282+github-actions[bot]@users.noreply.github.com"
        self.assertFalse(g.in_scope(pr(user="github-actions[bot]"), [commit(bot)]))


class Gate(unittest.TestCase):
    def test_no_verdict_is_pending(self):
        self.assertEqual(g.evaluate(pr(), [commit()], [])[0], "pending")

    def test_pass_for_current_head_succeeds(self):
        self.assertEqual(g.evaluate(pr(), [commit()], [comment(verdict(HEAD, "PASS"))])[0], "success")

    def test_na_counts_as_pass(self):
        self.assertEqual(g.evaluate(pr(), [commit()], [comment(verdict(HEAD, "N/A", "（本 PR 不涉及任何条款）"))])[0], "success")

    def test_fail_blocks(self):
        # PR #21: merged at 21:29Z after "判定：FAIL（MUST 未过 1 条）" at 20:57Z
        state, desc = g.evaluate(pr(), [commit()], [comment(verdict(HEAD, "FAIL", "（MUST 未过 1 条）"))])
        self.assertEqual(state, "failure")
        self.assertIn("FAIL", desc)

    def test_verdict_for_old_head_does_not_cover_new_head(self):
        self.assertEqual(g.evaluate(pr(), [commit()], [comment(verdict(OLD, "PASS"))])[0], "pending")

    def test_verdict_posted_before_head_commit_does_not_count(self):
        c = comment(verdict(HEAD, "PASS"), at="2026-11-02T09:00:00Z")
        self.assertEqual(g.evaluate(pr(), [commit(date="2026-11-02T10:00:00Z")], [c])[0], "pending")

    def test_untrusted_commenter_cannot_pass_the_gate(self):
        c = comment(verdict(HEAD, "PASS"), assoc="NONE")
        self.assertEqual(g.evaluate(pr(), [commit()], [c])[0], "pending")

    def test_later_verdict_wins_when_no_fail_stands(self):
        cs = [comment(verdict(HEAD, "N/A"), at="2026-11-02T12:00:00Z", cid=1),
              comment(verdict(HEAD, "PASS"), at="2026-11-02T13:00:00Z", cid=2)]
        self.assertEqual(g.evaluate(pr(), [commit()], cs), ("success", f"Independent verdict for {HEAD[:7]}: PASS"))

    def test_fail_is_sticky_a_later_pass_does_not_clear_it(self):
        cs = [comment(verdict(HEAD, "FAIL"), at="2026-11-02T12:00:00Z", cid=11),
              comment(verdict(HEAD, "PASS"), at="2026-11-02T13:00:00Z", cid=12)]
        state, desc = g.evaluate(pr(), [commit()], cs)
        self.assertEqual(state, "failure")
        self.assertIn("11", desc)
        later_fail = [comment(verdict(HEAD, "PASS"), at="2026-11-02T12:00:00Z", cid=11),
                      comment(verdict(HEAD, "FAIL"), at="2026-11-02T13:00:00Z", cid=12)]
        self.assertEqual(g.evaluate(pr(), [commit()], later_fail)[0], "failure")

    def test_explicit_supersession_lifts_a_fail(self):
        for marker in ("取代：11", "Supersedes: #issuecomment-11"):
            cs = [comment(verdict(HEAD, "FAIL"), at="2026-11-02T12:00:00Z", cid=11),
                  comment(verdict(HEAD, "PASS", f"\n{marker}"), at="2026-11-02T13:00:00Z", cid=12)]
            self.assertEqual(g.evaluate(pr(), [commit()], cs)[0], "success", marker)
        wrong_id = [comment(verdict(HEAD, "FAIL"), at="2026-11-02T12:00:00Z", cid=11),
                    comment(verdict(HEAD, "PASS", "\n取代：99"), at="2026-11-02T13:00:00Z", cid=12)]
        self.assertEqual(g.evaluate(pr(), [commit()], wrong_id)[0], "failure")

    def test_supersession_from_an_untrusted_commenter_does_not_count(self):
        cs = [comment(verdict(HEAD, "FAIL"), at="2026-11-02T12:00:00Z", cid=11),
              comment(verdict(HEAD, "PASS", "\n取代：11"), at="2026-11-02T13:00:00Z", assoc="NONE", cid=12)]
        self.assertEqual(g.evaluate(pr(), [commit()], cs)[0], "failure")


class ClaudeAppVerdicts(unittest.TestCase):
    """中枢裁决 on #90 (2026-11-03): claude[bot] verdicts must count, and one FAIL must block."""

    def test_app_fail_alone_blocks(self):
        cs = [app_comment(verdict(HEAD, "FAIL", "（MUST 未过 1 条）"))]
        self.assertEqual(g.evaluate(pr(), [commit()], cs)[0], "failure")

    def test_app_pass_counts(self):
        self.assertEqual(g.evaluate(pr(), [commit()], [app_comment(verdict(HEAD, "PASS"))])[0], "success")

    def test_owner_pass_after_app_fail_does_not_clear_it(self):
        cs = [app_comment(verdict(HEAD, "FAIL"), at="2026-11-02T12:00:00Z", cid=21),
              comment(verdict(HEAD, "PASS"), at="2026-11-02T13:00:00Z", cid=22)]
        self.assertEqual(g.evaluate(pr(), [commit()], cs)[0], "failure")

    def test_bot_named_claude_but_not_a_bot_account_is_untrusted(self):
        c = comment(verdict(HEAD, "PASS"), assoc="NONE", login="claude[bot]", kind="User")
        self.assertEqual(g.evaluate(pr(), [commit()], [c])[0], "pending")

    def test_other_bots_are_untrusted(self):
        c = comment(verdict(HEAD, "PASS"), assoc="NONE", login="github-actions[bot]", kind="Bot")
        self.assertEqual(g.evaluate(pr(), [commit()], [c])[0], "pending")


class RealFormats(unittest.TestCase):
    """Formats verdicts are actually posted in on this repo (assessment of 0ba4b17)."""

    def test_bold_verdict_word(self):
        body = f"### 独立评估 · SOTA v1.0 · {HEAD[:7]}\n判定：**FAIL**（MUST 未过 1 条）"  # #50 @ c3a89d1
        self.assertEqual(g.parse_verdict(body, HEAD), "FAIL")

    def test_bold_fail_after_plain_pass_is_failure(self):
        cs = [comment(verdict(HEAD, "PASS"), at="2026-11-02T12:00:00Z", cid=1),
              comment(f"### 独立评估 · SOTA v1.0 · {HEAD[:7]}\n判定：**FAIL**", at="2026-11-02T13:00:00Z", cid=2)]
        self.assertEqual(g.evaluate(pr(), [commit()], cs)[0], "failure")

    def test_verdict_as_heading(self):
        body = f"### 独立评估 · SOTA v1.0 · {HEAD[:7]}\n## 判定：**PASS**"  # #50 @ 951a448
        self.assertEqual(g.parse_verdict(body, HEAD), "PASS")

    def test_underscore_emphasis_and_ascii_colon(self):
        body = f"### 独立评估 · SOTA v1.0 · {HEAD[:7]}\n判定: __N/A__"
        self.assertEqual(g.parse_verdict(body, HEAD), "N/A")

    def test_quoted_header_in_other_text_is_not_a_verdict(self):
        body = "see the template: `### 独立评估 · SOTA v1.0 · <sha7>` and 判定：PASS somewhere"
        self.assertEqual(g.evaluate(pr(), [commit()], [comment(body)])[0], "pending")

    def test_header_without_verdict_line_is_not_a_verdict(self):
        body = f"### 独立评估 · SOTA v1.0 · {HEAD[:7]}\n(in progress)"
        self.assertIsNone(g.parse_verdict(body, HEAD))


if __name__ == "__main__":
    unittest.main()
