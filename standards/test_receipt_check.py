"""Tests for standards/receipt_check.py with a fake gh (no network).

    python3 -m unittest standards/test_receipt_check.py
"""
import json
import sys
import unittest
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import receipt_check as rc

REPO = "HUIIIM/.github"
MERGE = "f31f0c5a1b2c3d4e5f60718293a4b5c6d7e8f901"
TIP = "0af4f9bef6a4cbf9ee5e34bca64d0e592284b465"
HEAD = "a982e6c68e29753b3280df906e73644ca49e3d64"

WORLD = {
    f"repos/{REPO}/pulls/146": {"state": "closed", "merged": True, "merge_commit_sha": MERGE},
    f"repos/{REPO}/pulls/127": {"state": "open", "merged": False, "merge_commit_sha": None},
    f"repos/{REPO}/commits/{MERGE[:7]}": {"sha": MERGE},
    f"repos/{REPO}/commits/{MERGE}": {"sha": MERGE},
    f"repos/{REPO}/commits/{TIP[:7]}": {"sha": TIP},
    f"repos/{REPO}/commits/{HEAD}": {"sha": HEAD},
    f"repos/{REPO}/issues/comments/6627689384": {"issue_url": f"https://api.github.com/repos/{REPO}/issues/127", "body": "x"},
}


class FakeGh:
    def __init__(self, world=None, down=()):
        self.world, self.down, self.paths = WORLD if world is None else world, set(down), []

    def __call__(self, args):
        path = args[1]
        self.paths.append(path)
        if path in self.down:
            return 1, "", "gh: connection reset"
        if path in self.world:
            return 0, json.dumps(self.world[path]), ""
        return 1, "", "gh: Not Found (HTTP 404)"


def check(text, done=False, gh=None):
    return rc.check(text, REPO, rc.Reader(gh or FakeGh()), done=done)


def by_kind(rows):
    return {(k, r) for k, _, r, _ in rows}


GOOD_DONE = f"""完成回执
1. PR：https://github.com/{REPO}/pull/146
2. 已合并 PR #146，合并 SHA {MERGE[:7]}
3. 新的 main 顶端 SHA {TIP[:7]}
4. 验收：逐条通过
"""


class TrueReceipts(unittest.TestCase):
    def test_true_done_receipt_verifies(self):
        rows, verdict = check(GOOD_DONE, done=True)
        self.assertEqual(verdict, rc.OK, rows)
        self.assertIn(("done", rc.OK), by_kind(rows))

    def test_verdict_pointer_with_comment_link_verifies(self):
        text = f"verdict 已回写 PR #127，绑定 head `{HEAD}`：https://github.com/{REPO}/pull/127#issuecomment-6627689384"
        rows, verdict = check(text)
        self.assertEqual(verdict, rc.OK, rows)
        self.assertEqual(by_kind(rows), {("pr", rc.OK), ("sha", rc.OK), ("comment", rc.OK)})

    def test_each_pointer_is_read_once(self):
        gh = FakeGh()
        check(GOOD_DONE + GOOD_DONE, gh=gh)
        self.assertEqual(len(gh.paths), len(set(gh.paths)))


class FabricatedReceipts(unittest.TestCase):
    """样本 B: a merge that never happened, with a merge SHA and a comment id to match."""

    def test_invented_merge_sha_comment_and_merge_are_all_refuted(self):
        text = ("已合并 PR #127，merge sha deadbeef1234567\n"
                f"评论：https://github.com/{REPO}/pull/127#issuecomment-9999999999\nCI 12/12 全绿")
        rows, verdict = check(text)
        self.assertEqual(verdict, rc.BAD)
        refuted = {k for k, _, r, _ in rows if r == rc.BAD}
        self.assertEqual(refuted, {"merged", "sha", "comment"})

    def test_real_merge_with_the_wrong_sha_is_refuted(self):
        rows, verdict = check(f"已合并 PR #146，合并 SHA {TIP[:7]}")
        self.assertEqual(verdict, rc.BAD)
        self.assertIn(("merged", rc.BAD), by_kind(rows))

    def test_pull_request_that_does_not_exist_is_refuted(self):
        rows, verdict = check("见 PR #4040")
        self.assertEqual((verdict, by_kind(rows)), (rc.BAD, {("pr", rc.BAD)}))

    def test_comment_on_a_different_thread_is_refuted(self):
        rows, verdict = check(f"https://github.com/{REPO}/pull/146#issuecomment-6627689384")
        self.assertEqual(verdict, rc.BAD)
        self.assertTrue(any(k == "comment" and "not on #146" in e for k, _, _, e in rows))

    def test_receipt_without_any_pointer_cannot_be_booked(self):
        rows, verdict = check("已完成，全部通过，CI 全绿。")
        self.assertEqual(verdict, rc.BAD)
        self.assertEqual(rows[0][0], "pointers")

    def test_done_receipt_needs_a_merged_pr_its_sha_and_a_tip(self):
        _, v1 = check(f"PR #127 已开，head {HEAD}", done=True)
        _, v2 = check(f"已合并 PR #146\n另见 {TIP[:7]}", done=True)
        _, v3 = check(f"已合并 PR #146，合并 SHA {MERGE[:7]}", done=True)
        self.assertEqual((v1, v2, v3), (rc.BAD, rc.BAD, rc.BAD))


class Unknown(unittest.TestCase):
    def test_a_read_that_fails_is_unknown_not_a_pass(self):
        gh = FakeGh(down={f"repos/{REPO}/pulls/146"})
        rows, verdict = check("见 PR #146", gh=gh)
        self.assertEqual(verdict, rc.UNKNOWN)

    def test_refuted_outranks_unknown(self):
        gh = FakeGh(down={f"repos/{REPO}/pulls/146"})
        _, verdict = check("见 PR #146 与 PR #4040", gh=gh)
        self.assertEqual(verdict, rc.BAD)

    def test_exit_codes(self):
        self.assertEqual(rc.main(["--repo", REPO, "--comment", "6627689384"], gh=FakeGh()), 1)  # body "x": no pointer
        self.assertEqual(rc.main(["--repo", REPO, "--comment", "1"], gh=FakeGh()), 3)


class Extraction(unittest.TestCase):
    def test_numbers_are_not_mistaken_for_shas(self):
        prs, comments, shas, _ = rc.extract("run 41809454714，评论 6627689384，PR #127", REPO)
        self.assertEqual((prs, shas), ([(REPO, 127)], []))

    def test_cross_repo_pr_url_keeps_its_repo(self):
        prs, _, _, _ = rc.extract("https://github.com/HUIIIM/fama/pull/40", REPO)
        self.assertEqual(prs, [("HUIIIM/fama", 40)])


if __name__ == "__main__":
    unittest.main()
