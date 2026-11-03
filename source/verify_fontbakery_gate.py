"""Controls for fontbakery_gate.py: a real report passes, broken runs fail.

    python verify_fontbakery_gate.py build/fontbakery.json FONT.ttf [FONT.ttf ...]

The report and fonts are a real, complete run's (make fontbakery passes them). Each
negative control alters a copy of it, or fakes a run, and must fail for its own
reason; the real report must pass. Exits nonzero if any control goes the wrong way.
"""

import contextlib
import copy
import io
import json
import os
import sys
import tempfile

import fontbakery_gate as gate


def run(status, report, fonts, tmp):
    path = os.path.join(tmp, "report.json")
    if isinstance(report, str):
        text = report
    else:
        text = json.dumps(report)
    with open(path, "w") as f:
        f.write(text)
    with contextlib.redirect_stdout(io.StringIO()):
        return gate.judge(status, path, fonts)


def drop_font(report, font):
    """The report without one font's checks, its counters made consistent again."""
    r = copy.deepcopy(report)
    r["result"] = {"(not finished)": 0}
    for section in r["sections"]:
        section["checks"] = [c for c in section["checks"] if os.path.basename(c.get("filename") or "") != font]
        section["result"] = {}
        for c in section["checks"]:
            section["result"][c["result"]] = section["result"].get(c["result"], 0) + 1
            r["result"][c["result"]] = r["result"].get(c["result"], 0) + 1
    return r


def reporter_fixture(fonts, result="PASS"):
    checks = [{"key": ["fixture", "<FontBakeryCheck:reporter_fixture>"],
               "filename": os.path.basename(font), "result": result,
               "logs": [{"status": result, "message": "reporter fixture finding"}]}
              for font in fonts]
    return {"result": {"(not finished)": 0, result: len(checks)},
            "sections": [{"checks": checks, "result": {result: len(checks)}}]}


def reporter_controls(fonts):
    """Exercise JSON-only summaries, including incomplete message-prefix cases."""
    cases = []
    for result in ("PASS", "WARN", "FAIL", "FATAL", "ERROR"):
        cases.append((result + "-only summary", reporter_fixture(fonts, result),
                      int(result in gate.BAD), fonts, int(result in gate.BAD), True))
    report = reporter_fixture(fonts)
    cases += [
        ("malformed JSON", "{", 0, fonts, 1, False),
        ("status mismatch", report, 1, fonts, 1, False),
        ("missing expected font with misleading prefix", report, 0,
         fonts + ["unexpected absent.ttf"], 1, False),
    ]
    unfinished = copy.deepcopy(report)
    unfinished["result"]["(not finished)"] = 1
    cases.append(("unfinished summary", unfinished, 0, fonts, 1, False))
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for index, (name, report, status, fs, expected_exit, summary) in enumerate(cases):
            path = os.path.join(tmp, f"report-{index}.json")
            output = os.path.join(tmp, f"report-{index}.md")
            with open(path, "w") as stream:
                stream.write(report if isinstance(report, str) else json.dumps(report))
            with contextlib.redirect_stdout(io.StringIO()):
                result = gate.main([str(status), path, *fs, "--markdown", output])
            ok = result == expected_exit and os.path.exists(output) == summary
            if summary:
                with open(output) as stream:
                    text = stream.read()
                ok &= ("Gate: FAIL." if expected_exit else "Gate: PASS.") in text
                if name.startswith("WARN"):
                    ok &= "reporter fixture finding" in text
                with contextlib.redirect_stdout(io.StringIO()):
                    second = gate.main([str(status), path, *fs, "--markdown", output])
                with open(output) as stream:
                    ok &= stream.read() == text and second == result
            bad += not ok
            print(f"{'ok' if ok else 'WRONG'}: reporter: {name}")
    print(f"fontbakery reporter controls: {len(cases) - bad} of {len(cases)} right")
    return bad


def main(path, fonts):
    with open(path) as f:
        real = json.load(f)
    names = sorted(os.path.basename(f) for f in fonts)
    real_status = 1 if any(c["result"] in gate.BAD for s in real["sections"] for c in s["checks"]) else 0

    # Codex's control: fontbakery exits 2 after writing a partial report whose one
    # finding is allowed.
    partial = {"sections": [{"checks": [{"key": ["x", "<FontBakeryCheck:case_mapping>"],
                                         "filename": names[0], "result": "FAIL"}]}]}
    unfinished = copy.deepcopy(real)
    unfinished["result"]["(not finished)"] = 3
    no_end = copy.deepcopy(real)
    del no_end["sections"][-1]["result"]
    extra_fail = copy.deepcopy(real)  # one PASS turned into a FAIL of a check not in ALLOWED
    section = next(s for s in extra_fail["sections"] if any(c["result"] == "PASS" for c in s["checks"]))
    check = next(c for c in section["checks"] if c["result"] == "PASS")
    check.update(key=[check["key"][0], "<FontBakeryCheck:new_check>"] + check["key"][2:], result="FAIL")
    for counter in (section["result"], extra_fail["result"]):
        counter["PASS"] -= 1
        counter["FAIL"] = counter.get("FAIL", 0) + 1

    # (name, status, report, fonts, a phrase the failure must contain, or None to pass)
    controls = [
        ("real complete report", real_status, real, fonts, None),
        ("fake exit 2, partial allowed-only report", 2, partial, fonts, "operational error"),
        ("partial allowed-only report, exit 1", 1, partial, fonts, "malformed report"),
        ("SIGINT (exit 255) after a complete report", 255, real, fonts, "operational error"),
        (f"{names[-1]} missing from the report", real_status, drop_font(real, names[-1]), fonts, "missing from the report"),
        ("a font in the report that was not checked", real_status, real, fonts[:-1], "was not checked"),
        ("run not finished", real_status, unfinished, fonts, "did not finish"),
        ("a section without its end result", real_status, no_end, fonts, "did not end"),
        ("truncated JSON", real_status, json.dumps(real)[: 5000], fonts, "no readable report"),
        ("exit status disagrees with the report", 1 - real_status, real, fonts, "but the report"),
        ("a FAIL outside ALLOWED", 1, extra_fail, fonts, "unexpected"),
    ]
    bad = 0
    with tempfile.TemporaryDirectory() as tmp:
        for name, status, report, fs, phrase in controls:
            problems = run(status, report, fs, tmp)
            ok = not problems if phrase is None else any(phrase in p for p in problems)
            bad += not ok
            got = "passes" if not problems else problems[0]
            print(f"{'ok' if ok else 'WRONG'}: {name}: {got}")
    print(f"fontbakery gate controls: {len(controls) - bad} of {len(controls)} right")
    bad += reporter_controls(fonts)
    return 1 if bad else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1], sys.argv[2:]))
