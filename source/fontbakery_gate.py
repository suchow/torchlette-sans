"""Judge a fontbakery run: its exit status and its JSON report.

    python fontbakery_gate.py STATUS build/fontbakery.json FONT.ttf [FONT.ttf ...]

STATUS is fontbakery's exit status and the fonts are the ones it was given. The run
passes only if fontbakery completed (STATUS 0 or 1, matching the report), the report
is complete (every font in it and no other, the run finished, every font ran the same
nonzero number of checks) and nothing FAILs, is FATAL or ERRORs outside ALLOWED.
Prints the FAIL and WARN counts of each font. A check in ALLOWED that no longer fails
is reported, so the list can shrink. verify_fontbakery_gate.py tests this script.
"""

from dataclasses import dataclass
import argparse
import hashlib
import pathlib
import collections
import json
import os
import re
import sys

# Known open FAILs, by check id. Each needs a reason and is removed once fixed.
ALLOWED = {
    # Seven pairs that stock Mulish already has only one case of: IJ without ij, the
    # small u, g, k and h with caron or stroke and the capital E with cedilla without
    # their partners, and capital Sigma without sigma (the Greek module, held out of
    # the default build, would add it).
    "case_mapping",
}

# fontbakery 1.1.0's statuses that reach its exit code (cli.py: weight >= FAIL with
# the default --error-code-on FAIL).
BAD = {"FAIL", "FATAL", "ERROR"}

# fontbakery 1.1.0's exit statuses (fontbakery/cli.py main): 0 when the checks ran
# and none is BAD, 1 when the checks ran and one is (experimental checks excepted).
# Anything else is an operational error: 2 is an argparse usage error or no
# subcommand, 255 (sys.exit(-1)) is SIGINT, and a negative status from the shell is
# a signal. cli.py also exits 1 on invalid arguments and Python exits 1 on an
# uncaught exception; those write no report (the reporters write only after the
# run), so the completeness checks below reject them.
COMPLETED = {0, 1}


@dataclass(frozen=True)
class ReportValidation:
    """Structural completeness and findings are separate from human messages."""

    complete: bool
    problems: list[str]


class Incomplete(Exception):
    pass


def check_id_of(check):
    m = re.search(r"FontBakeryCheck:([^>]+)>", str(check["key"][1]))
    if not m:
        raise Incomplete(f"check without an id: {check['key']!r}")
    return m.group(1)


def evaluate(status, path, fonts):
    """Parse once; return a complete validated report, problems and its byte hash.

    Findings can fail the gate while still producing an honest human report.
    Operational, incomplete and malformed reports cannot produce a summary.
    """
    if status not in COMPLETED:
        return None, [f"fontbakery exited {status}, an operational error (completed runs exit 0 or 1)"], None
    try:
        raw = pathlib.Path(path).read_bytes()
        report = json.loads(raw)
    except (OSError, ValueError) as error:
        return None, [f"no readable report at {path}: {error}"], None
    try:
        validation = validate_report(status, report, fonts)
    except (Incomplete, KeyError, TypeError, IndexError) as error:
        return None, [f"malformed report {path}: {error!r}"], None
    return (report if validation.complete else None,
            validation.problems, hashlib.sha256(raw).hexdigest())


def judge(status, path, fonts):
    return evaluate(status, path, fonts)[1]


def judge_report(status, report, fonts):
    """Preserve the public list-of-problems API."""
    return validate_report(status, report, fonts).problems


def validate_report(status, report, fonts):
    """Check completion explicitly; findings can fail a complete report."""
    problems = []
    summary = report["result"]
    sections = report["sections"]
    if not isinstance(summary, dict) or not isinstance(sections, list) or not sections:
        raise Incomplete("no summary or no sections")
    # The run's end: fontbakery counts unfinished checks down to 0 and gives each
    # section its result counter only when the run ends.
    if summary.get("(not finished)") != 0:
        problems.append(f"run did not finish: (not finished) = {summary.get('(not finished)')!r}")
    checks = []
    for section in sections:
        if "result" not in section:
            problems.append(f"section {section.get('key')!r} has no result: the run did not end")
            continue
        if sum(section["result"].values()) != len(section["checks"]):
            problems.append(f"section {section.get('key')!r} counts {sum(section['result'].values())} results but lists {len(section['checks'])}")
        actual_counts = collections.Counter(c["result"] for c in section["checks"])
        if collections.Counter(section["result"]) != actual_counts:
            problems.append("section result counters disagree with actual check statuses")
        checks += section["checks"]
    total = sum(v for k, v in summary.items() if k != "(not finished)")
    if total != len(checks):
        problems.append(f"summary counts {total} results but the sections list {len(checks)}")

    actual_counts = collections.Counter(c["result"] for c in checks)
    reported_counts = collections.Counter({k: v for k, v in summary.items() if k != "(not finished)"})
    if actual_counts != reported_counts:
        problems.append("summary counters disagree with actual check statuses")

    expected = {os.path.basename(f) for f in fonts}
    counts = collections.defaultdict(collections.Counter)
    unexpected, allowed_seen, worst_bad = [], set(), False
    for check in checks:
        check_id = check_id_of(check)
        font = os.path.basename(check.get("filename") or "") or "family"
        result = check["result"]
        counts[font][result] += 1
        if result in BAD:
            if not check.get("experimental"):
                worst_bad = True
            if result == "FAIL" and check_id in ALLOWED:
                allowed_seen.add(check_id)
            else:
                unexpected.append(f"{font}: {check_id}: {result}")

    seen = set(counts) - {"family"}
    for font in sorted(expected - seen):
        problems.append(f"{font} is missing from the report")
    for font in sorted(seen - expected):
        problems.append(f"{font} is in the report but was not checked")
    per_font = {font: sum(counts[font].values()) for font in expected & seen}
    if not per_font or min(per_font.values()) == 0:
        problems.append("no font ran any check")
    elif len(set(per_font.values())) > 1:
        problems.append("fonts ran different numbers of checks: " + ", ".join(f"{f} {n}" for f, n in sorted(per_font.items())))
    if status != (1 if worst_bad else 0):
        problems.append(f"fontbakery exited {status} but the report {'has' if worst_bad else 'has no'} FAIL, FATAL or ERROR")

    for font in sorted(counts):
        c = counts[font]
        print(f"fontbakery {font}: {sum(c.values())} checks, FAIL {c['FAIL']}, WARN {c['WARN']}")
    if not problems:
        for check_id in sorted(ALLOWED - allowed_seen):
            print(f"fontbakery: {check_id} is allowed to fail but passes; remove it from ALLOWED")
    return ReportValidation(
        complete=not problems,
        problems=problems + [f"unexpected {line}" for line in unexpected],
    )


def markdown(report, status, problems, source_sha256):
    """Deterministic summary of the same validated JSON, including every non-PASS."""
    checks = [check for section in report["sections"] for check in section["checks"]]
    counts = collections.defaultdict(collections.Counter)
    for check in checks:
        font = os.path.basename(check.get("filename") or "") or "family"
        counts[font][check["result"]] += 1
    statuses = sorted({result for counter in counts.values() for result in counter})
    lines = ["# FontBakery summary", "", f"Gate: {'FAIL' if problems else 'PASS'}.",
             f"FontBakery exit status: {status}.", f"JSON SHA256: `{source_sha256}`.",
             "", "The Makefile invokes `check-universal --skip-network`; JSON itself does not record those flags.",
             "This is the JSON run's recorded scope, not a full family or release sign-off.",
             "Allowed failing check IDs: " + (", ".join(f"`{x}`" for x in sorted(ALLOWED)) or "none") + ".", "",
             "| Font | Checks | " + " | ".join(statuses) + " |",
             "|---|---:|" + "---:|" * len(statuses)]
    for font, counter in sorted(counts.items()):
        lines.append(f"| {font} | {sum(counter.values())} | " + " | ".join(str(counter[s]) for s in statuses) + " |")
    lines += ["", "## Gate problems", ""]
    lines += [f"- {problem}" for problem in problems] if problems else ["None."]
    lines += ["", "## Non-PASS check results", ""]
    findings = sorted((check for check in checks if check["result"] != "PASS"),
                      key=lambda c: (os.path.basename(c.get("filename") or ""), check_id_of(c),
                                     c["result"], json.dumps(c["key"], sort_keys=True)))
    if not findings:
        lines.append("None.")
    for check in findings:
        font = os.path.basename(check.get("filename") or "") or "family"
        lines += [f"### {font}: `{check_id_of(check)}` — {check['result']}", ""]
        if check.get("experimental"):
            lines += ["Experimental check; native exit-status semantics are preserved.", ""]
        for log in check.get("logs", []):
            message = log.get("message", "")
            # Preserve structured messages losslessly; ordinary descriptions remain readable.
            if isinstance(message, dict):
                code = message.get("code")
                text = message.get("message")
                if set(message).issubset({"code", "message"}) and isinstance(text, str):
                    message = (f"`{code}`: " if code is not None else "") + text
                else:
                    message = json.dumps(message, sort_keys=True, ensure_ascii=False)
            lines += [f"{log.get('status', '')}: {message}", ""]
    return "\n".join(lines).rstrip() + "\n"


def main(argv):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("status", type=int)
    parser.add_argument("report")
    parser.add_argument("fonts", nargs="+")
    parser.add_argument("--markdown", type=pathlib.Path)
    args = parser.parse_args(argv)
    report, problems, sha256 = evaluate(args.status, args.report, args.fonts)
    if args.markdown is not None and report is not None:
        source = pathlib.Path(args.report)
        if args.markdown.resolve() == source.resolve() or (
            args.markdown.exists() and os.path.samefile(args.markdown, source)
        ):
            raise ValueError("Markdown output aliases the JSON input")
        args.markdown.write_text(markdown(report, args.status, problems, sha256))
    for line in problems:
        print(f"fontbakery: {line}")
    return 1 if problems else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
