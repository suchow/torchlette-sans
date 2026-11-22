"""Hermetic tests for source/ci_check_mode.py and .github/workflows/ci.yml wiring.

    python3 source/verify_ci_check_mode.py

Builds temporary local git repositories (including bare origins and shallow
depth-1/depth-2 clones) to verify pull_request, push (P1-fetch), workflow_dispatch,
pathspec, fail-closed anomaly, and CLI output behavior with no font builds and
no network access. Exits nonzero on any failure.
"""

from __future__ import annotations

import os
from pathlib import Path
import subprocess
import sys
import tempfile

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SCRIPT = HERE / "ci_check_mode.py"
WORKFLOW = ROOT / ".github" / "workflows" / "ci.yml"

sys.path.insert(0, str(HERE))
import ci_check_mode as mode  # noqa: E402

CHECKS = 0
FAILS: list[str] = []


def check(ok: bool, name: str, detail: str = "") -> None:
    global CHECKS
    CHECKS += 1
    if not ok:
        FAILS.append(f"{name}: {detail}" if detail else name)


def _git_env() -> dict[str, str]:
    env = dict(os.environ)
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": "/dev/null",
            "GIT_AUTHOR_NAME": "Test",
            "GIT_AUTHOR_EMAIL": "test@example.com",
            "GIT_COMMITTER_NAME": "Test",
            "GIT_COMMITTER_EMAIL": "test@example.com",
            "GIT_TERMINAL_PROMPT": "0",
        }
    )
    return env


def git(cwd: Path, *args: str) -> str:
    proc = subprocess.run(
        [
            "git",
            "-c",
            "commit.gpgsign=false",
            "-c",
            "tag.gpgsign=false",
            "-c",
            "core.hooksPath=/dev/null",
            "-c",
            "init.defaultBranch=main",
            "-c",
            "protocol.file.allow=always",
            *args,
        ],
        cwd=str(cwd),
        capture_output=True,
        text=True,
        check=False,
        env=_git_env(),
    )
    if proc.returncode != 0:
        raise RuntimeError(
            f"git {' '.join(args)} in {cwd} failed ({proc.returncode}):\n"
            f"stdout: {proc.stdout}\nstderr: {proc.stderr}"
        )
    return proc.stdout.strip()


def write(root: Path, rel: str, text: str) -> Path:
    path = root / rel
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text, encoding="utf-8")
    return path


def commit_all(repo: Path, msg: str) -> str:
    git(repo, "add", "-A")
    git(repo, "commit", "-m", msg)
    return git(repo, "rev-parse", "HEAD")


def make_origin_and_work(base: Path) -> tuple[Path, str, Path, str]:
    bare = base / "origin.git"
    bare.mkdir(parents=True, exist_ok=True)
    git(bare, "init", "--bare")
    git(bare, "symbolic-ref", "HEAD", "refs/heads/main")
    git(bare, "config", "--local", "uploadpack.allowReachableSHA1InWant", "true")
    bare_uri = bare.resolve().as_uri()

    work = base / "work"
    work.mkdir(parents=True, exist_ok=True)
    git(work, "init")
    git(work, "checkout", "-b", "main")
    git(work, "remote", "add", "origin", bare_uri)
    write(work, "fonts/ttf/Regular.ttf", "font-v1\n")
    write(work, "source/build.py", "build-v1\n")
    write(work, "source/VERSION", "0.513\n")
    write(work, "CHANGELOG.md", "v0.5.13\n")
    b0 = commit_all(work, "Initial release")
    git(work, "push", "origin", "main")
    return bare, bare_uri, work, b0


def shallow_checkout(
    bare_uri: str,
    dst: Path,
    refspec: str,
    checkout_target: str,
    depth: int,
) -> Path:
    dst.mkdir(parents=True, exist_ok=True)
    git(dst, "init")
    git(dst, "remote", "add", "origin", bare_uri)
    git(dst, "fetch", "--no-tags", f"--depth={depth}", "origin", refspec)
    git(dst, "checkout", "--detach", checkout_target)
    return dst


def make_pr_merge_checkout(
    tmp: Path,
    name: str,
    *,
    pr_fn,
    main_advance_fn=None,
    depth: int = 2,
    pr_num: int = 54,
) -> tuple[Path, str, str, str]:
    case_dir = tmp / name
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)

    git(work, "checkout", "-b", "pr", b0)
    pr_fn(work)
    pr_head = git(work, "rev-parse", "HEAD")

    git(work, "checkout", "main")
    if main_advance_fn is not None:
        main_advance_fn(work)
        git(work, "push", "origin", "main")
    merge_base_parent = git(work, "rev-parse", "HEAD")

    git(work, "merge", "--no-ff", "-m", f"Merge PR #{pr_num}", "pr")
    git(work, "push", "origin", f"HEAD:refs/pull/{pr_num}/merge")

    checkout = shallow_checkout(
        bare_uri,
        case_dir / "checkout",
        f"+refs/pull/{pr_num}/merge:refs/remotes/pull/{pr_num}/merge",
        f"refs/remotes/pull/{pr_num}/merge",
        depth=depth,
    )
    return checkout, b0, pr_head, merge_base_parent


def test_pull_requests(tmp: Path) -> None:
    # 1. Source-only PR
    def edit_source(w: Path) -> None:
        write(w, "source/build.py", "build-v2\n")
        commit_all(w, "Edit source")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_source_only", pr_fn=edit_source)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(not d.compare, "pr source-only skips compare", str(d))

    # 2. VERSION + CHANGELOG only PR
    def edit_version(w: Path) -> None:
        write(w, "source/VERSION", "0.514\n")
        write(w, "CHANGELOG.md", "v0.5.14\n")
        commit_all(w, "Bump version")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_version_only", pr_fn=edit_version)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(not d.compare, "pr VERSION-only skips compare", str(d))

    # 3. Release PR: modify, add, delete, rename out, rename in, mode change under fonts/
    def modify_font(w: Path) -> None:
        write(w, "fonts/ttf/Regular.ttf", "font-v2\n")
        commit_all(w, "Release fonts")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_modify", pr_fn=modify_font)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "pr fonts modified compares", str(d))

    def add_font(w: Path) -> None:
        write(w, "fonts/ttf/New.ttf", "font-new\n")
        commit_all(w, "Add font")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_add", pr_fn=add_font)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.changed_fonts == ("fonts/ttf/New.ttf",), "pr fonts added compares", str(d))

    def delete_font(w: Path) -> None:
        (w / "fonts/ttf/Regular.ttf").unlink()
        commit_all(w, "Delete font")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_delete", pr_fn=delete_font)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "pr fonts deleted compares", str(d))

    def rename_out(w: Path) -> None:
        git(w, "mv", "fonts/ttf/Regular.ttf", "moved.ttf")
        commit_all(w, "Move font out")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_rename_out", pr_fn=rename_out)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "pr fonts renamed out compares", str(d))

    def rename_in(w: Path) -> None:
        git(w, "mv", "source/build.py", "fonts/build.py")
        commit_all(w, "Move file into fonts")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_rename_in", pr_fn=rename_in)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.changed_fonts == ("fonts/build.py",), "pr fonts renamed in compares", str(d))

    def chmod_font(w: Path) -> None:
        os.chmod(w / "fonts/ttf/Regular.ttf", 0o755)
        git(w, "update-index", "--chmod=+x", "fonts/ttf/Regular.ttf")
        git(w, "commit", "-m", "Chmod font")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_chmod", pr_fn=chmod_font)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "pr fonts mode change compares", str(d))

    # 4. Pathspec boundary: similar prefixes/nested names do not match top-level fonts/
    def nonmatching_paths(w: Path) -> None:
        write(w, "fonts-notes.txt", "notes\n")
        write(w, "source/fonts/nested.ttf", "nested\n")
        commit_all(w, "Non-matching font-like paths")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_nonmatching", pr_fn=nonmatching_paths)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(not d.compare, "pathspec ignores fonts-notes.txt and source/fonts/*", str(d))

    # 5. PR re-run after main advances (HEAD^1 != event base SHA)
    def main_releases_fonts(w: Path) -> None:
        write(w, "fonts/ttf/Regular.ttf", "font-main-v2\n")
        commit_all(w, "Main release")

    co, b0, h, b1 = make_pr_merge_checkout(
        tmp,
        "pr_rerun_main_advanced_source",
        pr_fn=edit_source,
        main_advance_fn=main_releases_fonts,
    )
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(not d.compare and d.base_ref == b1, "pr rerun after main release stays source-only", str(d))

    def main_changelog(w: Path) -> None:
        write(w, "CHANGELOG.md", "v0.5.13 note\n")
        commit_all(w, "Main changelog")

    co, b0, h, b1 = make_pr_merge_checkout(
        tmp,
        "pr_rerun_main_advanced_fonts",
        pr_fn=modify_font,
        main_advance_fn=main_changelog,
    )
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare and d.base_ref == b1, "pr rerun with fonts change compares", str(d))

    # 6. PR touching fonts/ then reverting it (empty net diff)
    def touch_then_revert(w: Path) -> None:
        write(w, "fonts/ttf/Regular.ttf", "temp\n")
        commit_all(w, "Temp font edit")
        write(w, "fonts/ttf/Regular.ttf", "font-v1\n")
        write(w, "source/build.py", "build-v2\n")
        commit_all(w, "Revert font edit")

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_fonts_reverted", pr_fn=touch_then_revert)
    d = mode.decide(str(co), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(not d.compare, "pr reverted fonts has empty net diff", str(d))

    # 7. Fail-closed PR anomalies
    co_d1, b0, h, _ = make_pr_merge_checkout(tmp, "pr_depth1", pr_fn=edit_source, depth=1)
    d = mode.decide(str(co_d1), event_name="pull_request", checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=h)
    check(d.compare, "pr depth-1 missing parents fails closed", str(d))

    co, b0, h, _ = make_pr_merge_checkout(tmp, "pr_anomalies", pr_fn=edit_source)
    for label, kwargs in (
        ("missing base sha", dict(checkout_ref="refs/pull/54/merge", pr_base_sha="", pr_head_sha=h)),
        ("missing head sha", dict(checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha="")),
        ("zero base sha", dict(checkout_ref="refs/pull/54/merge", pr_base_sha=mode.ZERO_SHA, pr_head_sha=h)),
        ("malformed sha", dict(checkout_ref="refs/pull/54/merge", pr_base_sha="abc123", pr_head_sha=h)),
        ("mismatched head sha", dict(checkout_ref="refs/pull/54/merge", pr_base_sha=b0, pr_head_sha=b0)),
    ):
        d = mode.decide(str(co), event_name="pull_request", **kwargs)
        check(d.compare, f"pr {label} fails closed", str(d))

    # 8. Octopus merge (3 parents) fails closed
    octo_dir = tmp / "pr_octopus"
    _, _, work, b0 = make_origin_and_work(octo_dir)
    git(work, "checkout", "-b", "p2", b0)
    write(work, "source/p2.txt", "2\n")
    p2 = commit_all(work, "p2")
    git(work, "checkout", "-b", "p3", b0)
    write(work, "source/p3.txt", "3\n")
    p3 = commit_all(work, "p3")
    git(work, "checkout", "main")
    write(work, "source/p1.txt", "1\n")
    p1 = commit_all(work, "p1")
    git(work, "merge", "--no-ff", "-m", "Octopus", "p2", "p3")
    check(len(git(work, "rev-list", "--parents", "-n", "1", "HEAD").split()) == 4, "pr octopus fixture has 3 parents")
    d = mode.decide(str(work), event_name="pull_request", checkout_ref="refs/pull/99/merge", pr_base_sha=p1, pr_head_sha=p3)
    check(d.compare, "pr octopus merge fails closed", str(d))
    _ = p2

    # 9. Non-merge PR checkout: single merge-base, missing base, criss-cross (2 merge-bases), unrelated (0 merge-bases)
    nm_dir = tmp / "pr_non_merge"
    _, bare_uri, work, b0 = make_origin_and_work(nm_dir)
    git(work, "checkout", "-b", "pr-src", b0)
    write(work, "source/build.py", "build-v2\n")
    h_src = commit_all(work, "PR source edit")
    git(work, "push", "origin", "pr-src")
    d = mode.decide(str(work), event_name="pull_request", checkout_ref="refs/heads/pr-src", pr_base_sha=b0, pr_head_sha=h_src)
    check(not d.compare and d.base_ref == b0, "non-merge pr single merge-base source-only", str(d))

    # Shallow depth-1 of pr-src misses b0 -> fails closed
    co_nm_d1 = shallow_checkout(bare_uri, nm_dir / "shallow_pr", "+refs/heads/pr-src:refs/remotes/origin/pr-src", "refs/remotes/origin/pr-src", depth=1)
    d = mode.decide(str(co_nm_d1), event_name="pull_request", checkout_ref="refs/heads/pr-src", pr_base_sha=b0, pr_head_sha=h_src)
    check(d.compare, "non-merge pr missing base fails closed", str(d))

    git(work, "checkout", "-b", "pr-font", b0)
    write(work, "fonts/ttf/Regular.ttf", "font-v2\n")
    h_font = commit_all(work, "PR font edit")
    d = mode.decide(str(work), event_name="pull_request", checkout_ref="refs/heads/pr-font", pr_base_sha=b0, pr_head_sha=h_font)
    check(d.compare, "non-merge pr fonts changed compares", str(d))

    # Criss-cross merge -> 2 merge-bases -> fails closed
    cc_dir = tmp / "pr_crisscross"
    _, _, work, b0 = make_origin_and_work(cc_dir)
    git(work, "checkout", "-b", "b1", b0)
    write(work, "source/b1.txt", "1\n")
    c_b1 = commit_all(work, "b1")
    git(work, "checkout", "-b", "b2", b0)
    write(work, "source/b2.txt", "2\n")
    c_b2 = commit_all(work, "b2")
    git(work, "checkout", "b1")
    git(work, "merge", "--no-ff", "-m", "m1", c_b2)
    m1 = git(work, "rev-parse", "HEAD")
    git(work, "checkout", "b2")
    git(work, "merge", "--no-ff", "-m", "m2", c_b1)
    m2 = git(work, "rev-parse", "HEAD")
    d = mode.decide(str(work), event_name="pull_request", checkout_ref="refs/heads/b2", pr_base_sha=m1, pr_head_sha=m2)
    check(d.compare and "ambiguous merge-bases (2 found)" in d.reason, "pr criss-cross merge fails closed", str(d))

    # Unrelated orphan history -> 0 merge-bases -> fails closed
    git(work, "checkout", "--orphan", "unrelated")
    git(work, "rm", "-rf", ".")
    write(work, "source/orphan.txt", "orphan\n")
    o_sha = commit_all(work, "Orphan commit")
    d = mode.decide(str(work), event_name="pull_request", checkout_ref="refs/heads/unrelated", pr_base_sha=b0, pr_head_sha=o_sha)
    check(d.compare, "pr unrelated history fails closed", str(d))


def test_pushes(tmp: Path) -> None:
    # 1. Single-commit source-only push (depth 2, HEAD^1 == before, no fetch needed)
    case_dir = tmp / "push_single_source"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    write(work, "source/build.py", "build-v2\n")
    c1 = commit_all(work, "Source fix")
    git(work, "push", "origin", "main")
    co = shallow_checkout(bare_uri, case_dir / "co", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co), event_name="push", push_before_sha=b0, push_after_sha=c1, push_forced="false", allow_fetch=False)
    check(not d.compare and d.base_ref == b0, "push single-commit source-only skips compare without fetch", str(d))

    # 2. Merge-commit merge of a multi-commit source-only PR (depth 2, HEAD^1 == before)
    case_dir = tmp / "push_merge_source"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    git(work, "checkout", "-b", "feat", b0)
    write(work, "source/a.py", "1\n")
    commit_all(work, "feat 1")
    write(work, "source/b.py", "2\n")
    commit_all(work, "feat 2")
    write(work, "source/c.py", "3\n")
    commit_all(work, "feat 3")
    git(work, "checkout", "main")
    git(work, "merge", "--no-ff", "-m", "Merge PR", "feat")
    m_sha = git(work, "rev-parse", "HEAD")
    git(work, "push", "origin", "main")
    co = shallow_checkout(bare_uri, case_dir / "co", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co), event_name="push", push_before_sha=b0, push_after_sha=m_sha, push_forced="false", allow_fetch=False)
    check(not d.compare and d.base_ref == b0, "push merge-commit source-only PR skips compare without fetch", str(d))

    # 3. Single-commit and merge-commit release pushes touching fonts/
    case_dir = tmp / "push_release"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    write(work, "fonts/ttf/Regular.ttf", "font-v2\n")
    rel = commit_all(work, "Release fonts")
    git(work, "push", "origin", "main")
    co = shallow_checkout(bare_uri, case_dir / "co", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co), event_name="push", push_before_sha=b0, push_after_sha=rel, push_forced="false")
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "push single release compares", str(d))

    case_dir = tmp / "push_merge_release"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    git(work, "checkout", "-b", "relpr", b0)
    write(work, "source/VERSION", "0.514\n")
    commit_all(work, "Bump version")
    write(work, "fonts/ttf/Regular.ttf", "font-v2\n")
    commit_all(work, "Commit rebuilt fonts")
    git(work, "checkout", "main")
    git(work, "merge", "--no-ff", "-m", "Merge release PR", "relpr")
    m_rel = git(work, "rev-parse", "HEAD")
    git(work, "push", "origin", "main")
    co = shallow_checkout(bare_uri, case_dir / "co", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co), event_name="push", push_before_sha=b0, push_after_sha=m_rel, push_forced="false")
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "push merge release PR compares", str(d))

    # 4. Multi-commit source-only push (before 3 commits behind HEAD -> needs P1-fetch)
    case_dir = tmp / "push_multi_source"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    write(work, "source/1.py", "1\n")
    commit_all(work, "c1")
    write(work, "source/2.py", "2\n")
    commit_all(work, "c2")
    write(work, "source/3.py", "3\n")
    c3 = commit_all(work, "c3")
    git(work, "push", "origin", "main")

    co_nofetch = shallow_checkout(bare_uri, case_dir / "co_nofetch", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_nofetch), event_name="push", push_before_sha=b0, push_after_sha=c3, push_forced="false", allow_fetch=False)
    check(d.compare, "push multi-commit without fetch fails closed", str(d))

    co_fetch = shallow_checkout(bare_uri, case_dir / "co_fetch", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_fetch), event_name="push", push_before_sha=b0, push_after_sha=c3, push_forced="false", allow_fetch=True)
    check(not d.compare and d.base_ref == b0, "push multi-commit source-only fetches before and skips compare", str(d))

    # 5. Multi-commit push containing a fonts/ commit in the middle
    case_dir = tmp / "push_multi_fonts"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    write(work, "source/1.py", "1\n")
    commit_all(work, "c1")
    write(work, "fonts/ttf/Regular.ttf", "font-v2\n")
    commit_all(work, "c2 release")
    write(work, "CHANGELOG.md", "notes\n")
    c3 = commit_all(work, "c3 changelog")
    git(work, "push", "origin", "main")
    co = shallow_checkout(bare_uri, case_dir / "co", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co), event_name="push", push_before_sha=b0, push_after_sha=c3, push_forced="false", allow_fetch=True)
    check(d.compare and d.changed_fonts == ("fonts/ttf/Regular.ttf",), "push multi-commit with fonts change compares", str(d))

    # 6. Multi-commit push where deepen fetch fails (broken remote or nonexistent SHA) -> fails closed
    co_broken = shallow_checkout(bare_uri, case_dir / "co_broken", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    git(co_broken, "remote", "set-url", "origin", (case_dir / "missing.git").resolve().as_uri())
    d = mode.decide(str(co_broken), event_name="push", push_before_sha=b0, push_after_sha=c3, push_forced="false", allow_fetch=True)
    check(d.compare and "failed to deepen" in d.reason, "push deepen failure fails closed", str(d))

    co_badsha = shallow_checkout(bare_uri, case_dir / "co_badsha", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_badsha), event_name="push", push_before_sha="a" * 40, push_after_sha=c3, push_forced="false", allow_fetch=True)
    check(d.compare, "push nonexistent before SHA fails closed", str(d))

    # 7. Shallow push ancestry proof: fetchable non-ancestor fails closed, deepen budget fails closed,
    #    and real multi-commit ancestor succeeds while keeping older history shallow
    case_dir = tmp / "push_shallow_ancestry"
    _, bare_uri, work, _ = make_origin_and_work(case_dir)
    for i in range(6):
        write(work, f"source/hist_{i}.py", f"{i}\n")
        commit_all(work, f"hist {i}")
    b_anc = git(work, "rev-parse", "HEAD")
    # Unrelated sibling commit with identical fonts/, reachable on origin (fetchable by SHA)
    git(work, "checkout", "-b", "side_same_fonts", b_anc)
    write(work, "source/side_same.py", "side\n")
    side_same = commit_all(work, "Side branch with identical fonts")
    git(work, "push", "origin", "side_same_fonts")

    git(work, "checkout", "main")
    write(work, "source/m1.py", "1\n")
    commit_all(work, "m1")
    write(work, "source/m2.py", "2\n")
    commit_all(work, "m2")
    write(work, "source/m3.py", "3\n")
    m3 = commit_all(work, "m3")
    git(work, "push", "origin", "main")

    # Fetchable non-ancestor with identical fonts/ on a shallow checkout -> must fail closed
    co_nonanc = shallow_checkout(bare_uri, case_dir / "co_nonanc", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_nonanc), event_name="push", push_before_sha=side_same, push_after_sha=m3, push_forced="false", allow_fetch=True)
    check(d.compare and "not an ancestor" in d.reason, "push shallow fetchable non-ancestor fails closed", str(d))

    # Non-ancestor when repo stays shallow after bounded deepen -> fails closed
    co_nonanc_sh = shallow_checkout(bare_uri, case_dir / "co_nonanc_sh", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_nonanc_sh), event_name="push", push_before_sha=side_same, push_after_sha=m3, push_forced="false", allow_fetch=True, deepen_steps=(2,))
    check(
        d.compare and "could not be proven an ancestor" in d.reason and git(co_nonanc_sh, "rev-parse", "--is-shallow-repository") == "true",
        "push shallow non-ancestor within deepen budget fails closed",
        str(d),
    )

    # Real ancestor when deepen budget is too small to reach it -> fails closed
    co_budget = shallow_checkout(bare_uri, case_dir / "co_budget", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_budget), event_name="push", push_before_sha=b_anc, push_after_sha=m3, push_forced="false", allow_fetch=True, deepen_steps=(1,))
    check(d.compare and "could not be proven an ancestor" in d.reason, "push deepen budget exhausted fails closed", str(d))

    # Real ancestor 3 commits back proven via --deepen=4 while keeping older history shallow
    co_proven = shallow_checkout(bare_uri, case_dir / "co_proven", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    d = mode.decide(str(co_proven), event_name="push", push_before_sha=b_anc, push_after_sha=m3, push_forced="false", allow_fetch=True, deepen_steps=(4,))
    check(
        not d.compare and d.base_ref == b_anc and git(co_proven, "rev-parse", "--is-shallow-repository") == "true",
        "push real ancestor proven while remaining shallow",
        str(d),
    )

    # 8. Fail-closed push anomalies
    case_dir = tmp / "push_anomalies"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    write(work, "source/build.py", "build-v2\n")
    c1 = commit_all(work, "c1")
    git(work, "push", "origin", "main")
    # Create an unmerged sibling branch commit in work (non-ancestor of c1)
    git(work, "checkout", "-b", "side", b0)
    write(work, "source/side.py", "side\n")
    side = commit_all(work, "side")
    git(work, "checkout", "main")

    for label, repo_path, kwargs in (
        ("forced push", work, dict(push_before_sha=b0, push_after_sha=c1, push_forced="true")),
        ("missing forced flag", work, dict(push_before_sha=b0, push_after_sha=c1, push_forced="")),
        ("all-zero before", work, dict(push_before_sha=mode.ZERO_SHA, push_after_sha=c1, push_forced="false")),
        ("before equals after", work, dict(push_before_sha=c1, push_after_sha=c1, push_forced="false")),
        ("missing before", work, dict(push_before_sha="", push_after_sha=c1, push_forced="false")),
        ("missing after", work, dict(push_before_sha=b0, push_after_sha="", push_forced="false")),
        ("HEAD != after", work, dict(push_before_sha=b0, push_after_sha=side, push_forced="false")),
        ("non-ancestor before in full repo", work, dict(push_before_sha=side, push_after_sha=c1, push_forced="false")),
    ):
        d = mode.decide(str(repo_path), event_name="push", **kwargs)
        check(d.compare, f"push {label} fails closed", str(d))
        if label == "HEAD != after":
            check("HEAD does not match" in d.reason, "push HEAD != after reason", str(d))

    # Shallow clone with an unrelated local commit passed as before -> fails closed
    co_side = shallow_checkout(bare_uri, case_dir / "co_side", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)
    git(work, "push", "origin", "side")
    git(co_side, "fetch", "--no-tags", "--depth=1", "origin", side)
    d = mode.decide(str(co_side), event_name="push", push_before_sha=side, push_after_sha=c1, push_forced="false")
    check(d.compare, "push unrelated local before in shallow repo fails closed", str(d))


def test_other_events_and_cli(tmp: Path) -> None:
    case_dir = tmp / "cli_and_events"
    _, bare_uri, work, b0 = make_origin_and_work(case_dir)
    write(work, "source/build.py", "build-v2\n")
    c1 = commit_all(work, "Source edit")
    git(work, "push", "origin", "main")
    co = shallow_checkout(bare_uri, case_dir / "co", "+refs/heads/main:refs/remotes/origin/main", "refs/remotes/origin/main", depth=2)

    for ev in ("workflow_dispatch", "schedule", "merge_group", ""):
        d = mode.decide(str(co), event_name=ev)
        check(d.compare, f"event {ev!r} defaults to full compare", str(d))

    # CLI end-to-end test: false then true written to GITHUB_OUTPUT
    out_false = case_dir / "gh_out_false.txt"
    env_false = _git_env()
    env_false.update(
        {
            "EVENT_NAME": "push",
            "CHECKOUT_REF": "refs/heads/main",
            "PUSH_BEFORE_SHA": b0,
            "PUSH_AFTER_SHA": c1,
            "PUSH_FORCED": "false",
        }
    )
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(co), "--github-output", str(out_false)],
        capture_output=True,
        text=True,
        check=False,
        env=env_false,
    )
    check(
        proc.returncode == 0 and out_false.exists() and out_false.read_text(encoding="utf-8") == "compare=false\n",
        "cli writes compare=false",
        f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}",
    )

    out_true = case_dir / "gh_out_true.txt"
    env_true = _git_env()
    env_true["EVENT_NAME"] = "workflow_dispatch"
    proc = subprocess.run(
        [sys.executable, str(SCRIPT), "--repo", str(co), "--github-output", str(out_true)],
        capture_output=True,
        text=True,
        check=False,
        env=env_true,
    )
    check(
        proc.returncode == 0 and out_true.exists() and out_true.read_text(encoding="utf-8") == "compare=true\n",
        "cli writes compare=true on workflow_dispatch",
        f"rc={proc.returncode} stdout={proc.stdout!r} stderr={proc.stderr!r}",
    )


def test_workflow_wiring() -> None:
    text = WORKFLOW.read_text(encoding="utf-8")
    for needle in (
        "fetch-depth: ${{ (github.event_name == 'pull_request' || github.event_name == 'push') && 2 || 1 }}",
        "python3 source/ci_check_mode.py --github-output \"$GITHUB_OUTPUT\"",
        "EVENT_NAME: ${{ github.event_name }}",
        "CHECKOUT_REF: ${{ github.ref }}",
        "PR_BASE_SHA: ${{ github.event.pull_request.base.sha }}",
        "PR_HEAD_SHA: ${{ github.event.pull_request.head.sha }}",
        "PUSH_BEFORE_SHA: ${{ github.event.before }}",
        "PUSH_AFTER_SHA: ${{ github.event.after }}",
        "PUSH_FORCED: ${{ github.event.forced }}",
        'make -j"$(sysctl -n hw.ncpu)" release-rebuild',
        'make -j"$(sysctl -n hw.ncpu)" check',
        "name: release-rebuild",
        "python3 source/verify_ci_check_mode.py",
    ):
        check(needle in text, f"workflow contains {needle}")


def main() -> int:
    with tempfile.TemporaryDirectory(prefix="ts-ci-check-mode-") as td:
        tmp = Path(td)
        test_pull_requests(tmp)
        test_pushes(tmp)
        test_other_events_and_cli(tmp)
    test_workflow_wiring()
    print(f"ci_check_mode: {CHECKS - len(FAILS)}/{CHECKS} checks passed")
    for item in FAILS:
        print(f"  FAIL {item}")
    return 1 if FAILS else 0


if __name__ == "__main__":
    sys.exit(main())
