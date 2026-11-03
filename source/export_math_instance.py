"""Supported two-stage MATH-aware export from an immutable original full VF.

This is a custom export path, not a change to generic fontTools instancing.
Both pins run in one invocation; arbitrary external partials are not accepted.
"""

from __future__ import annotations
import argparse
import copy
import hashlib
import io
import json
import sys
import math
import importlib.metadata
from dataclasses import dataclass, asdict
from fractions import Fraction as Q
from pathlib import Path
from fontTools.ttLib import TTFont
from fontTools.ttLib.tables import otTables, otBase
from fontTools.varLib.instancer import instantiateVariableFont
from fontTools.varLib.varStore import OnlineVarStoreBuilder
from fontTools.varLib.builder import buildVarDevTable

PIN = "4.68.0"
REPACKER_PIN = "0.57.0"
ITAL_MAP = {Q(-1): Q(-1), Q(0): Q(0), Q(8191, 16384): Q(0), Q(1, 2): Q(1), Q(1): Q(1)}


def require(ok, message):
    if not ok:
        raise ValueError(message)


def digest(raw):
    return hashlib.sha256(raw).hexdigest()


def load(raw):
    return TTFont(io.BytesIO(raw), recalcTimestamp=False, recalcBBoxes=False)


def serial(obj):
    if isinstance(obj, dict):
        return {k: serial(v) for k, v in obj.items()}
    if isinstance(obj, (str, int, float, bool)) or obj is None:
        return obj
    if isinstance(obj, (list, tuple)):
        return [serial(x) for x in obj]
    return {k: serial(v) for k, v in vars(obj).items() if not k.startswith("_")}


def records(obj, path="MATH"):
    if isinstance(obj, otTables.MathValueRecord):
        yield path, obj
    elif isinstance(obj, list):
        for i, x in enumerate(obj):
            yield from records(x, f"{path}[{i}]")
    elif hasattr(obj, "__dict__"):
        for k, v in vars(obj).items():
            if not k.startswith("_"):
                yield from records(v, path + "." + k)


def plain(font):
    table = copy.deepcopy(font["MATH"].table)
    for _, r in records(table):
        r.Value = 0
        r.DeviceTable = None
    return serial(table)


# Signed half-up rounding stays rational: no float conversion near a half.
def nearest(n, d=1):
    require(d > 0, "Invalid rounding denominator")
    return (2 * n + d) // (2 * d)


def exact_round(value):
    v = Q(value)
    return nearest(v.numerator, v.denominator)


def fixed(value):
    return exact_round(Q(value) * 65536)


def coordinate(value, tag):
    require(
        type(value) in (str, int, float, Q),
        "Coordinate must be decimal/rational numeric data",
    )
    if type(value) is float:
        require(math.isfinite(value), "Coordinate must be finite")
    try:
        q = Q(str(value)) if type(value) is float else Q(value)
    except (ValueError, ZeroDivisionError) as error:
        raise ValueError("Malformed coordinate") from error
    lo, hi = (300, 900) if tag == "wght" else (0, 1)
    require(lo <= q <= hi, "Coordinate outside supported source domain")
    return q


# OpenType coordinate steps: user/axis arithmetic and avar interpolation in
# 16.16, followed by add-two/shift-two conversion to the final F2Dot14 value.
def normalization(font, user):
    result = {}
    traces = {}
    require(set(user) == {"wght", "ital"}, "Complete original coordinate pair required")
    for a in font["fvar"].axes:
        u = fixed(user[a.axisTag])
        mi, de, ma = [fixed(v) for v in (a.minValue, a.defaultValue, a.maxValue)]
        require(mi <= u <= ma, "Coordinate outside serialized axis domain")
        default = (
            nearest((u - de) * 65536, (ma - de) if u > de else (de - mi))
            if u != de
            else 0
        )
        default = max(-65536, min(65536, default))
        maps = [
            (fixed(x), fixed(y))
            for x, y in sorted(font["avar"].segments[a.axisTag].items())
        ]
        ratio = None
        segment = None
        hit = next(((x, y) for x, y in maps if x == default), None)
        if hit:
            out = hit[1]
        else:
            right = next(j for j, (x, y) in enumerate(maps) if x > default)
            x0, y0 = maps[right - 1]
            x1, y1 = maps[right]
            ratio = nearest((default - x0) * 65536, x1 - x0)
            out = y0 + nearest(ratio * (y1 - y0), 65536)
            segment = [(x0, y0), (x1, y1)]
        out = max(-65536, min(65536, out))
        f2 = (out + 2) >> 2
        result[a.axisTag] = Q(f2, 16384)
        traces[a.axisTag] = {
            "user16_16": u,
            "axis16_16": [mi, de, ma],
            "default16_16": default,
            "avar_segment16_16": segment,
            "avar_ratio16_16": ratio,
            "avar_final16_16": out,
            "final_F2Dot14_integer": f2,
            "final_normalized": str(result[a.axisTag]),
        }
    return result, traces


def support(region, location, axes):
    require(len(region.VarRegionAxis) == len(axes), "Region axis count mismatch")
    answer = Q(1)
    for tag, r in zip(axes, region.VarRegionAxis):
        s, p, e = [Q.from_float(x) for x in (r.StartCoord, r.PeakCoord, r.EndCoord)]
        x = location[tag]
        require(-1 <= s <= p <= e <= 1, "Invalid region bounds")
        if p == 0:
            continue
        require(not s < 0 < e, "Invalid participating region crossing zero")
        if x == p:
            factor = Q(1)
        elif x <= s or x >= e:
            return Q(0)
        elif x < p:
            factor = (x - s) / (p - s)
        else:
            factor = (e - x) / (e - p)
        answer *= factor
    return answer


def math_value(font, rec, location):
    total = Q(rec.Value)
    dev = getattr(rec, "DeviceTable", None)
    if dev is None:
        return total
    require(
        dev.DeltaFormat == 0x8000, "ppem MATH devices require unsupported composition"
    )
    index = (dev.StartSize << 16) | dev.EndSize
    if index == 0xFFFFFFFF:
        return total
    store = font["GDEF"].table.VarStore
    require(0 <= dev.StartSize < len(store.VarData), "Invalid MATH outer VarIdx")
    block = store.VarData[dev.StartSize]
    require(0 <= dev.EndSize < len(block.Item), "Invalid MATH inner VarIdx")
    row = block.Item[dev.EndSize]
    require(len(row) == len(block.VarRegionIndex), "Invalid variation row cardinality")
    axes = [a.axisTag for a in font["fvar"].axes]
    for delta, ri in zip(row, block.VarRegionIndex):
        require(
            type(delta) is int and 0 <= ri < len(store.VarRegionList.Region),
            "Invalid region reference/delta",
        )
        total += delta * support(store.VarRegionList.Region[ri], location, axes)
    return total


def require_runtime():
    require(
        importlib.metadata.version("fonttools") == PIN,
        "Pinned fontTools version required",
    )
    try:
        version = importlib.metadata.version("uharfbuzz")
    except importlib.metadata.PackageNotFoundError:
        raise ValueError(
            "Pinned uharfbuzz 0.57.0 repacker required before export"
        ) from None
    require(
        version == REPACKER_PIN and otBase.have_uharfbuzz,
        "Pinned uharfbuzz 0.57.0 repacker required before export",
    )


def source_profile(font):
    require_runtime()
    require(
        font.cfg["fontTools.ttLib.tables.otBase:USE_HARFBUZZ_REPACKER"] is not False,
        "HarfBuzz repacker must not be disabled",
    )
    for tag in ("GPOS", "GSUB"):
        if tag in font:
            version = int.from_bytes(font.reader[tag][:4], "big")
            require(
                version in (0x10000, 0x10001),
                "Unsupported layout version for pinned repacker",
            )
    require(
        importlib.metadata.version("fonttools") == PIN,
        "Pinned fontTools version required",
    )
    require(
        "MATH" in font
        and "GDEF" in font
        and getattr(font["GDEF"].table, "VarStore", None) is not None,
        "Complete source MATH/GDEF store required",
    )
    require(
        "fvar" in font
        and [
            (a.axisTag, a.minValue, a.defaultValue, a.maxValue)
            for a in font["fvar"].axes
        ]
        == [("wght", 300, 400, 900), ("ital", 0, 0, 1)],
        "Unsupported fvar axes/ranges/defaults",
    )
    require(
        "avar" in font and getattr(font["avar"], "majorVersion", 1) == 1,
        "Unsupported avar version",
    )
    require(set(font["avar"].segments) == {"wght", "ital"}, "Unsupported avar axis set")
    for tag, mapping in font["avar"].segments.items():
        pairs = sorted((Q.from_float(x), Q.from_float(y)) for x, y in mapping.items())
        require(
            len(pairs) >= 3 and all(-1 <= x <= 1 and -1 <= y <= 1 for x, y in pairs),
            "Invalid avar range",
        )
        require(
            all(
                pairs[i][0] < pairs[i + 1][0] and pairs[i][1] <= pairs[i + 1][1]
                for i in range(len(pairs) - 1)
            ),
            "Invalid avar monotonicity",
        )
        require(
            all(mapping.get(x) == x for x in (-1, 0, 1)),
            "Required avar identity anchors missing",
        )
    require(
        {
            Q.from_float(x): Q.from_float(y)
            for x, y in font["avar"].segments["ital"].items()
        }
        == ITAL_MAP,
        "Unsupported canonical italic avar shape",
    )
    store = font["GDEF"].table.VarStore
    require(store.VarRegionList.RegionAxisCount == 2, "Source store axis count differs")
    require(len(dict(records(font["MATH"].table))) > 0, "No source MATH records")
    for _, rec in records(font["MATH"].table):
        dev = rec.DeviceTable
        require(
            dev is None or dev.DeltaFormat == 0x8000,
            "Source ppem MATH device unsupported",
        )


def values(font, pins):
    loc, traces = normalization(font, pins)
    return (
        {p: math_value(font, r, loc) for p, r in records(font["MATH"].table)},
        loc,
        traces,
    )


# The exact fvar/avar profile validated above maps public 16.16 italic inputs
# to only 0, 1/4, 1/2, 3/4, or 1. Its transition spans four input ticks:
# 32764..32768 of 65536. These samples are exhaustive for this profile only.
def discrete_branch_values(font, weight):
    branch = []
    for i in (0, 1):
        branch.append(values(font, {"wght": weight, "ital": Q(i)})[0])
    wloc = normalization(font, {"wght": weight, "ital": Q(0)})[0]["wght"]
    for style in (0, Q(1, 4), Q(1, 2), Q(3, 4), 1):
        for p, r in records(font["MATH"].table):
            require(
                math_value(font, r, {"wght": wloc, "ital": Q(style)})
                == branch[int(style >= Q(1, 2))][p],
                f"Unsupported MATH discrete source branch: {p}, normalized ital {style}",
            )
    return branch


def weight_partial(font, weight):
    branch = discrete_branch_values(font, weight)
    out = instantiateVariableFont(
        font,
        {"wght": float(weight)},
        inplace=False,
        optimize=False,
        updateFontNames=False,
    )
    require(
        [a.axisTag for a in out["fvar"].axes] == ["ital"],
        "Wrong remaining partial axis",
    )
    require(plain(out) == plain(font), "Partial MATH plain structure/coverage differs")
    # Capture the ordinary *serialized* partial: glyf compilation refreshes
    # loca offsets. Comparing a precompile loca table would conflate ordinary
    # instancer serialization with changes caused by the MATH repair.
    baseline = serialize(out)
    baseline_font = load(baseline)
    out = load(baseline)
    oldstore = copy.deepcopy(getattr(out["GDEF"].table, "VarStore", None))
    original = dict(records(font["MATH"].table))
    target = dict(records(out["MATH"].table))
    require(original.keys() == target.keys(), "MATH record identity changed")
    # Two supports sum to the original discrete branch at every reachable
    # style coordinate. Store round(I)-round(R), avoiding independent
    # rounding of a base and an unrounded style difference.
    builder = OnlineVarStoreBuilder(["ital"])
    builder.setSupports([{"ital": (8191 / 16384, 0.5, 1)}, {"ital": (0.5, 1, 1)}])
    devices = []
    for p, r in target.items():
        require(
            r.DeviceTable is None or r.DeviceTable.DeltaFormat == 0x8000,
            "Target ppem MATH device unsupported",
        )
        R, I = exact_round(branch[0][p]), exact_round(branch[1][p])
        r.Value = R
        r.DeviceTable = None
        delta = I - R
        if delta:
            r.DeviceTable = buildVarDevTable(builder.storeDeltas([delta, delta]))
            devices.append(r.DeviceTable)
    if devices:
        extra = builder.finish()
        gdef = out["GDEF"].table
        old = getattr(gdef, "VarStore", None)
        if old is None:
            gdef.VarStore = extra
        else:
            require(
                old.VarRegionList.RegionAxisCount == 1,
                "Wrong remaining store dimension",
            )
            offset = len(old.VarData)
            regions = len(old.VarRegionList.Region)
            old.VarRegionList.Region.extend(extra.VarRegionList.Region)
            old.VarRegionList.RegionCount = len(old.VarRegionList.Region)
            for b in extra.VarData:
                b.VarRegionIndex = [x + regions for x in b.VarRegionIndex]
            old.VarData.extend(extra.VarData)
            old.VarDataCount = len(old.VarData)
            for d in devices:
                d.StartSize += offset
        gdef.Version = max(gdef.Version, 0x10003)
    out = load(serialize(out))
    same_other_tables(baseline_font, out, {"MATH", "GDEF"})
    require(plain(out) == plain(font), "Partial MATH plain structure/coverage differs")
    if oldstore is not None:
        new = out["GDEF"].table.VarStore
        require(
            serial(oldstore.VarData) == serial(new.VarData[: len(oldstore.VarData)])
            and serial(oldstore.VarRegionList.Region)
            == serial(new.VarRegionList.Region[: len(oldstore.VarRegionList.Region)]),
            "Partial repair changed existing store prefix",
        )
    out._ordinary_partial_bytes = baseline
    out._partial_preservation = {
        "ordinary_partial_sha256": digest(baseline),
        "non_math_gdef_raw_tables_equal": True,
        "loca_included": True,
        "head_exception": "checksumAdjustment only",
    }
    return out


def serialize(font):
    buffer = io.BytesIO()
    font.recalcTimestamp = False
    font.recalcBBoxes = False
    font.save(buffer)
    return buffer.getvalue()


def write_new(font, path):
    require(
        not path.exists() and not path.is_symlink(), "Generated path already exists"
    )
    font.recalcTimestamp = False
    font.recalcBBoxes = False
    font.save(path)
    raw = path.read_bytes()
    return raw, load(raw)


def head_without_checksum(font):
    raw = bytearray(font.reader["head"])
    raw[8:12] = b"\0" * 4
    return bytes(raw)


def same_other_tables(a, b, allowed):
    require(set(a.reader.keys()) == set(b.reader.keys()), "Table repertoire changed")
    for tag in a.reader.keys():
        if tag not in allowed and tag != "head":
            require(
                a.reader[tag] == b.reader[tag], f"Non-MATH target bytes changed: {tag}"
            )
    require(
        head_without_checksum(a) == head_without_checksum(b),
        "head changed beyond checksumAdjustment",
    )


@dataclass(frozen=True)
class Receipt:
    source_sha256: str
    partial_path: str
    partial_sha256: str
    first_axis: str
    first_value: str
    remaining_axis: str
    order: tuple


class Exporter:
    def __init__(self, raw, expected_sha):
        require(
            type(raw) is bytes
            and isinstance(expected_sha, str)
            and len(expected_sha) == 64
            and all(x in "0123456789abcdef" for x in expected_sha)
            and digest(raw) == expected_sha,
            "Original complete source hash mismatch",
        )
        self.raw = raw
        self.sha = expected_sha
        source_profile(load(raw))
        self.receipts = {}
        self.audit = []
        self.partial_audit = []

    def source(self):
        require(
            type(self.raw) is bytes and digest(self.raw) == self.sha,
            "Bound original source bytes changed",
        )
        return load(self.raw)

    def partial(self, axis, value, path, order):
        require(
            tuple(order) in (("wght", "ital"), ("ital", "wght")) and order[0] == axis,
            "Wrong explicit first axis/order",
        )
        value = coordinate(value, axis)
        font = self.source()
        out = (
            weight_partial(font, value)
            if axis == "wght"
            else instantiateVariableFont(
                font,
                {axis: float(value)},
                inplace=False,
                optimize=False,
                updateFontNames=False,
            )
        )
        if hasattr(out, "_ordinary_partial_bytes"):
            baseline_path = Path(path).with_name("ordinary-" + Path(path).name)
            require(
                not baseline_path.exists() and not baseline_path.is_symlink(),
                "Ordinary partial path already exists",
            )
            baseline_path.write_bytes(out._ordinary_partial_bytes)
            self.partial_audit.append(
                {
                    "path": str(baseline_path.resolve()),
                    **out._partial_preservation,
                }
            )
        require(
            plain(out) == plain(font), "Partial MATH plain structure/coverage differs"
        )
        raw, out = write_new(out, Path(path))
        require(
            "fvar" in out and [a.axisTag for a in out["fvar"].axes] == [order[1]],
            "Saved partial has wrong axes",
        )
        token = Receipt(
            self.sha,
            str(Path(path).resolve()),
            digest(raw),
            axis,
            str(value),
            order[1],
            tuple(order),
        )
        self.receipts[token.partial_sha256] = token
        return token, out

    def complete(self, receipt, second_axis, value, path):
        require(
            isinstance(receipt, Receipt)
            and self.receipts.get(receipt.partial_sha256) == receipt,
            "Unbound/changed partial receipt",
        )
        require(
            receipt.source_sha256 == self.sha
            and receipt.remaining_axis == second_axis
            and receipt.order == (receipt.first_axis, second_axis),
            "Wrong saved pin state/order",
        )
        value = coordinate(value, second_axis)
        raw = Path(receipt.partial_path).read_bytes()
        require(digest(raw) == receipt.partial_sha256, "Saved partial bytes changed")
        partial = load(raw)
        require(
            "fvar" in partial
            and [a.axisTag for a in partial["fvar"].axes] == [second_axis],
            "Saved partial axis state differs",
        )
        pins = {receipt.first_axis: Q(receipt.first_value), second_axis: value}
        full = self.source()
        discrete_branch_values(full, pins["wght"])
        original, loc, traces = values(full, pins)
        # Preserve the real chained ordinary target. MATH alone is repaired
        # from the untouched full source, not from rounded partial records.
        ordinary = instantiateVariableFont(
            partial,
            {second_axis: float(value)},
            inplace=False,
            optimize=False,
            updateFontNames=False,
        )
        path = Path(path)
        op = path.with_name("ordinary-" + path.name)
        ob, out = write_new(ordinary, op)
        require("fvar" not in out, "MATH repair requires a fully pinned target")
        require(plain(out) == plain(full), "MATH plain structure/coverage differs")
        target = dict(records(out["MATH"].table))
        require(target.keys() == original.keys(), "MATH record identity changed")
        for p, r in target.items():
            require(
                r.DeviceTable is None or r.DeviceTable.DeltaFormat == 0x8000,
                "Target ppem MATH device unsupported",
            )
            r.Value = exact_round(original[p])
            r.DeviceTable = None
        rb, reopened = write_new(out, path)
        same_other_tables(load(ob), reopened, {"MATH"})
        self.audit.append(
            {
                "pins": {k: str(v) for k, v in pins.items()},
                "order": receipt.order,
                "actual_partial": receipt.partial_path,
                "partial_sha256": receipt.partial_sha256,
                "ordinary_target": str(op),
                "ordinary_sha256": digest(ob),
                "repaired_target": str(path),
                "repaired_sha256": digest(rb),
                "canonical": {k: str(v) for k, v in loc.items()},
                "normalization_traces": traces,
                "only_MATH_and_head_checksum_changed": True,
                "GDEF_GPOS_raw_bytes_unchanged": True,
                "MATH_records": len(original),
            }
        )
        return reopened


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--source", type=Path, required=True)
    p.add_argument("--source-sha256", required=True)
    p.add_argument("--wght", required=True)
    p.add_argument("--ital", required=True)
    p.add_argument("--order", choices=["wght,ital", "ital,wght"], required=True)
    p.add_argument("--out-dir", type=Path, required=True)
    a = p.parse_args()
    source = a.source.resolve()
    require(source.is_file(), "Missing original full source")
    raw = source.read_bytes()
    runner = Exporter(raw, a.source_sha256)
    pins = {"wght": coordinate(a.wght, "wght"), "ital": coordinate(a.ital, "ital")}
    order = tuple(a.order.split(","))
    root = a.out_dir.resolve()
    require(
        not a.out_dir.is_symlink() and not root.exists(),
        "Output root must be a new non-symlink directory",
    )
    require(not source.is_relative_to(root), "Output root aliases source")
    root.mkdir(parents=True, exist_ok=False)
    receipt, _ = runner.partial(order[0], pins[order[0]], root / "partial.ttf", order)
    data = asdict(receipt)
    data["schema"] = "torchlette-math-export-partial"
    data["version"] = 1
    data["fonttools"] = PIN
    (root / "receipt.json").write_text(json.dumps(data, indent=2) + "\n")
    readback = json.loads((root / "receipt.json").read_text())
    require(
        readback == json.loads(json.dumps(data)),
        "Receipt serialization changed bound state",
    )
    runner.complete(receipt, order[1], pins[order[1]], root / "final.ttf")
    require(
        digest(source.read_bytes()) == a.source_sha256,
        "Original source changed during export",
    )
    require(
        digest(Path(receipt.partial_path).read_bytes()) == receipt.partial_sha256,
        "Partial changed during export",
    )
    proof = {
        "scope": "Supported custom two-stage MATH export; generic fontTools chains unchanged. No source-family or glyph acceptance.",
        "source": str(source),
        "source_sha256": a.source_sha256,
        "source_unchanged": True,
        "receipt": data,
        "audit": runner.audit,
        "ordinary_partial_baselines": runner.partial_audit,
        "tool_versions": {
            "fonttools": PIN,
            "uharfbuzz": REPACKER_PIN,
            "python": sys.version,
        },
        "exporter_sha256": digest(Path(__file__).read_bytes()),
        "axes": {k: str(v) for k, v in pins.items()},
        "source_record_count": len(dict(records(runner.source()["MATH"].table))),
    }
    (root / "proof.json").write_text(json.dumps(proof, indent=2) + "\n")
    print(
        json.dumps(
            {
                "output": str(root),
                "records": proof["source_record_count"],
                "final_sha256": digest((root / "final.ttf").read_bytes()),
            }
        )
    )


if __name__ == "__main__":
    main()
