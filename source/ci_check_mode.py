"""Decide whether CI's check job must compare rebuilt fonts against committed fonts/.

Used by .github/workflows/ci.yml before running either `make release-rebuild`
(source-only PRs and non-forced pushes that leave fonts/ unchanged) or
`make check` (release PRs/pushes touching fonts/, manual workflow_dispatch runs,
and any missing, unfetchable, or ambiguous base ref). Always fails closed to
`compare=true`.

Stdlib only; no font builds or third-party packages required.
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
import os
import re
import subprocess
import sys

SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ZERO_SHA = "0" * 40
PR_MERGE_REF_RE = re.compile(r"^refs/pull/[0-9]+/merge$")


@dataclass(frozen=True)
class Decision:
    compare: bool
    reason: str
    base_ref: str | None = None
    changed_fonts: tuple[str, ...] = ()


def is_sha(value: str | None) -> bool:
    return bool(value and SHA_RE.fullmatch(value))


def is_nonzero_sha(value: str | None) -> bool:
    return is_sha(value) and value != ZERO_SHA


def _git(repo: str, *args: str) -> subprocess.CompletedProcess[str]:
    env = dict(os.environ)
    env["GIT_TERMINAL_PROMPT"] = "0"
    return subprocess.run(
        ["git", "-C", repo, *args],
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


def _has_commit_and_tree(repo: str, sha: str) -> bool:
    if not is_nonzero_sha(sha):
        return False
    return (
        _git(repo, "cat-file", "-e", f"{sha}^{{commit}}").returncode == 0
        and _git(repo, "cat-file", "-e", f"{sha}^{{tree}}").returncode == 0
    )


def _head_with_parents(repo: str) -> list[str] | None:
    proc = _git(repo, "rev-list", "--parents", "-n", "1", "HEAD")
    if proc.returncode != 0:
        return None
    parts = proc.stdout.strip().split()
    if not parts or not all(is_nonzero_sha(p) for p in parts):
        return None
    return parts


def _diff_fonts(repo: str, base_ref: str, skip_label: str, note: str = "") -> Decision:
    proc = _git(repo, "diff", "--no-renames", "--name-only", base_ref, "HEAD", "--", "fonts")
    if proc.returncode != 0:
        return Decision(True, f"git diff against {base_ref} failed", base_ref=base_ref)
    changed = tuple(line for line in proc.stdout.splitlines() if line)
    if changed:
        return Decision(
            True,
            f"fonts/ changed relative to {base_ref}{note}",
            base_ref=base_ref,
            changed_fonts=changed,
        )
    return Decision(
        False,
        f"{skip_label} (fonts/ unchanged relative to {base_ref}){note}",
        base_ref=base_ref,
    )


def _decide_pull_request(
    repo: str,
    *,
    checkout_ref: str,
    pr_base_sha: str,
    pr_head_sha: str,
) -> Decision:
    if not is_nonzero_sha(pr_base_sha) or not is_nonzero_sha(pr_head_sha):
        return Decision(True, "missing or invalid pull_request base/head SHA")

    parts = _head_with_parents(repo)
    if parts is None:
        return Decision(True, "unable to read HEAD commit or parents")
    head_sha, parents = parts[0], parts[1:]

    note = ""
    if PR_MERGE_REF_RE.fullmatch(checkout_ref):
        if (
            len(parents) != 2
            or head_sha == pr_head_sha
            or parents[1] != pr_head_sha
            or not _has_commit_and_tree(repo, parents[0])
        ):
            return Decision(True, "PR merge commit parents are missing or ambiguous")
        base_ref = parents[0]
        if base_ref != pr_base_sha:
            note = f" (merge parent differs from event base {pr_base_sha})"
    else:
        if head_sha != pr_head_sha or not _has_commit_and_tree(repo, pr_base_sha):
            return Decision(
                True,
                f"checked-out ref {checkout_ref or 'unknown'} has missing or ambiguous base ref",
            )
        mb = _git(repo, "merge-base", "--all", pr_base_sha, "HEAD")
        if mb.returncode != 0:
            return Decision(True, f"base ref {pr_base_sha} has no local merge-base")
        bases = mb.stdout.strip().split()
        if len(bases) != 1 or not _has_commit_and_tree(repo, bases[0]):
            return Decision(
                True,
                f"base ref {pr_base_sha} has ambiguous merge-bases ({len(bases)} found)",
            )
        base_ref = bases[0]

    return _diff_fonts(repo, base_ref, "source-only PR", note=note)


def _decide_push(
    repo: str,
    *,
    push_before_sha: str,
    push_after_sha: str,
    push_forced: str,
    remote: str,
    allow_fetch: bool,
) -> Decision:
    if push_forced.strip().lower() != "false":
        return Decision(
            True,
            f"push forced flag is {push_forced!r}; defaulting to full comparison",
        )
    if push_before_sha == ZERO_SHA:
        return Decision(True, "branch creation push (all-zero before SHA)")
    if not is_nonzero_sha(push_before_sha) or not is_nonzero_sha(push_after_sha):
        return Decision(True, "missing or invalid push before/after SHA")
    if push_before_sha == push_after_sha:
        return Decision(True, "degenerate push (before SHA equals after SHA)")

    parts = _head_with_parents(repo)
    if parts is None or parts[0] != push_after_sha:
        return Decision(True, "checked-out HEAD does not match push after SHA")
    parents = parts[1:]

    shallow_proc = _git(repo, "rev-parse", "--is-shallow-repository")
    if shallow_proc.returncode != 0:
        return Decision(True, "unable to determine repository shallow status")
    is_shallow = shallow_proc.stdout.strip() == "true"

    fetched_before = False
    if not _has_commit_and_tree(repo, push_before_sha):
        if not allow_fetch or not remote:
            return Decision(True, f"previous push commit {push_before_sha} is not present locally")
        fetch = _git(repo, "fetch", "--no-tags", "--depth=1", remote, push_before_sha)
        if fetch.returncode != 0:
            return Decision(True, f"failed to fetch previous push commit {push_before_sha}")
        fh = _git(repo, "rev-parse", "--verify", "--quiet", "FETCH_HEAD^{commit}")
        if fh.returncode != 0 or fh.stdout.strip() != push_before_sha:
            return Decision(
                True,
                f"fetched commit did not match previous push commit {push_before_sha}",
            )
        if not _has_commit_and_tree(repo, push_before_sha):
            return Decision(
                True,
                f"fetched previous push commit {push_before_sha} failed object validation",
            )
        fetched_before = True

    if not is_shallow:
        anc = _git(repo, "merge-base", "--is-ancestor", push_before_sha, "HEAD")
        if anc.returncode != 0:
            return Decision(True, f"previous push commit {push_before_sha} is not an ancestor of HEAD")
    elif not fetched_before:
        is_first_parent = bool(parents and parents[0] == push_before_sha)
        if not is_first_parent:
            anc = _git(repo, "merge-base", "--is-ancestor", push_before_sha, "HEAD")
            if anc.returncode != 0:
                return Decision(
                    True,
                    f"local previous push commit {push_before_sha} could not be validated as an ancestor of HEAD",
                )

    return _diff_fonts(repo, push_before_sha, "source-only push")


def decide(
    repo: str,
    *,
    event_name: str,
    checkout_ref: str = "",
    pr_base_sha: str = "",
    pr_head_sha: str = "",
    push_before_sha: str = "",
    push_after_sha: str = "",
    push_forced: str = "",
    remote: str = "origin",
    allow_fetch: bool = True,
) -> Decision:
    if event_name == "pull_request":
        return _decide_pull_request(
            repo,
            checkout_ref=checkout_ref,
            pr_base_sha=pr_base_sha,
            pr_head_sha=pr_head_sha,
        )
    if event_name == "push":
        return _decide_push(
            repo,
            push_before_sha=push_before_sha,
            push_after_sha=push_after_sha,
            push_forced=push_forced,
            remote=remote,
            allow_fetch=allow_fetch,
        )
    return Decision(True, f"event {event_name or 'unknown'} defaults to full comparison")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo", default=".", help="Path to git checkout (default: .)")
    parser.add_argument("--github-output", default="", help="Optional GITHUB_OUTPUT file to append compare=<bool>")
    parser.add_argument("--remote", default="origin", help="Git remote name for push before-SHA fetch")
    parser.add_argument("--no-fetch", action="store_true", help="Disable fetching missing push before SHA")
    args = parser.parse_args(argv)

    decision = decide(
        args.repo,
        event_name=os.environ.get("EVENT_NAME", ""),
        checkout_ref=os.environ.get("CHECKOUT_REF", ""),
        pr_base_sha=os.environ.get("PR_BASE_SHA", ""),
        pr_head_sha=os.environ.get("PR_HEAD_SHA", ""),
        push_before_sha=os.environ.get("PUSH_BEFORE_SHA", ""),
        push_after_sha=os.environ.get("PUSH_AFTER_SHA", ""),
        push_forced=os.environ.get("PUSH_FORCED", ""),
        remote=args.remote,
        allow_fetch=not args.no_fetch,
    )

    if decision.changed_fonts:
        print("Changed files under fonts/:")
        for path in decision.changed_fonts:
            print(f"  {path}")
    flag = "true" if decision.compare else "false"
    print(f"compare={flag} ({decision.reason})")
    if args.github_output:
        with open(args.github_output, "a", encoding="utf-8") as fh:
            fh.write(f"compare={flag}\n")
    return 0


if __name__ == "__main__":
    sys.exit(main())
