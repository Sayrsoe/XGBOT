"""Offline validation for the checked-in ScreenshotBot v0.1 contract."""
from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from datetime import datetime
from decimal import Decimal
from functools import lru_cache
import hashlib
import json
from pathlib import Path
import re
import sys


SCHEMA_PATH = Path(__file__).resolve().parents[2] / "schemas" / "screenshot_evidence_v0_1.json"


@dataclass(frozen=True)
class Issue:
    code: str
    path: str
    message: str


@dataclass(frozen=True)
class PacketResult:
    packet_id: str | None
    status: str
    issues: tuple[Issue, ...] = ()


@dataclass(frozen=True)
class BatchResult:
    valid: bool
    records: tuple[PacketResult, ...]
    # Only a successful batch yields an importable, append-only revision list.
    history: tuple[str, ...]


@lru_cache(maxsize=1)
def _schema():
    return json.loads(SCHEMA_PATH.read_text(encoding="utf-8"))


def _unique_keys(pairs):
    result = {}
    for key, value in pairs:
        if key in result:
            raise ValueError(f"Repeated JSON key {key!r}")
        result[key] = value
    return result


def _reject_constant(value):
    raise ValueError(f"Invalid JSON numeric constant {value}")


def read_packet(path):
    return json.loads(Path(path).read_text(encoding="utf-8"), object_pairs_hook=_unique_keys,
                      parse_constant=_reject_constant)


def _resolve(rule):
    if "$ref" in rule:
        return _schema()["$defs"][rule["$ref"].removeprefix("#/$defs/")]
    return rule


_TYPES = {"string": str, "integer": int, "object": dict, "array": list, "null": type(None)}


def _structure(value, rule, path):
    """Interpret only the fixed schema vocabulary used in v0.1."""
    rule = _resolve(rule)
    if "oneOf" in rule:
        # Both tagged unions use mutually exclusive required string constants.
        tag = "kind" if path == "$.payload" else "status"
        for candidate in rule["oneOf"]:
            branch = _resolve(candidate)
            if isinstance(value, dict) and value.get(tag) == branch["properties"][tag]["const"]:
                yield from _structure(value, branch, path)
                return
        yield Issue("invalid_tag", path, f"Missing or unsupported {tag}")
        return
    if "anyOf" in rule:
        # The two alternatives in v0.1 are always null and a typed object.
        if value is not None:
            yield from _structure(value, rule["anyOf"][1], path)
        return
    if "const" in rule and value != rule["const"]:
        code = {"$.schema_version": "unsupported_version",
                "$.source.classification": "unsupported_source"}.get(path, "unexpected_value")
        yield Issue(code, path, f"Expected {rule['const']!r}")
    if "enum" in rule and value not in rule["enum"]:
        yield Issue("unexpected_value", path, "Unsupported choice")
    kind = rule.get("type")
    if kind and type(value) is not _TYPES[kind]:
        yield Issue("invalid_type", path, f"Expected {kind}")
        return
    if kind == "object":
        for name in rule["required"]:
            if name not in value:
                yield Issue("missing_field", f"{path}.{name}", "Required field is absent")
        for name in sorted(value):
            if name not in rule["properties"]:
                yield Issue("unknown_field", f"{path}.{name}", "Field is outside contract v0.1")
            else:
                yield from _structure(value[name], rule["properties"][name], f"{path}.{name}")
    elif kind == "array":
        if len(value) < rule["minItems"]:
            yield Issue("empty_rows", path, "At least one team row is required")
        for index, item in enumerate(value):
            yield from _structure(item, rule["items"], f"{path}[{index}]")
    elif kind == "string":
        if not rule.get("minLength", 0) <= len(value) <= rule.get("maxLength", len(value)):
            yield Issue("invalid_length", path, "String length outside contract bounds")
        elif "pattern" in rule and not re.fullmatch(rule["pattern"], value):
            yield Issue("invalid_format", path, "Text does not match the required format")
        elif rule.get("format") == "date-time":
            try:
                datetime.strptime(value, "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                yield Issue("invalid_timestamp", path, "Invalid UTC calendar date or time")
    elif kind == "integer" and "minimum" in rule and value < rule["minimum"]:
        yield Issue("below_minimum", path, f"Minimum is {rule['minimum']}")


def _semantics(packet):
    revision = packet["revision"]
    correction = packet["correction"]
    if (revision == 1) != (correction is None):
        yield Issue("invalid_revision", "$.correction", "Only revision 1 has a null correction")
    if correction and (not correction["reason"].strip() or
                       correction["predecessor_id"] == packet["packet_id"]):
        yield Issue("invalid_correction", "$.correction", "Supply a reason and a distinct predecessor")

    payload = packet["payload"]
    is_match = payload["kind"] == "completed_match"
    if is_match:
        if payload["home_team_id"] == payload["away_team_id"]:
            yield Issue("identical_teams", "$.payload.away_team_id", "Teams must differ")
        groups = [("$.payload", payload)]
        event = payload["kickoff_utc"]
    else:
        groups = [(f"$.payload.rows[{i}]", row) for i, row in enumerate(payload["rows"])]
        teams = [row["team_id"] for _, row in groups]
        if len(set(teams)) != len(teams):
            yield Issue("duplicate_team", "$.payload.rows", "One row per team per table")
        event = payload["table_as_of_utc"]

    for path, record in groups:
        for key, field in record.items():
            if isinstance(field, dict) and "raw_text" in field:
                if Decimal(field["raw_text"]) != Decimal(field["value"]):
                    yield Issue("transcription_mismatch", f"{path}.{key}", "Raw and parsed values differ")

    captured, recorded = packet["captured_at_utc"], packet["recorded_at_utc"]
    if captured > recorded:
        yield Issue("time_order", "$.recorded_at_utc", "Revision recorded before capture")
    available = packet["availability"].get("earliest_verified_at_utc")
    for path, timestamp in [("$.captured_at_utc", captured),
                            ("$.availability.earliest_verified_at_utc", available)]:
        if timestamp is not None and (timestamp < event or (is_match and timestamp == event)):
            yield Issue("time_order", path, "Time precedes table scope or is at/before match kickoff")
    if available is not None and available > recorded:
        yield Issue("time_order", "$.availability", "Availability claim is later than revision recording")


def validate_packet(packet):
    """Check a decoded JSON packet. Revision linkage is a collection-level check."""
    issues = tuple(_structure(packet, _schema(), "$"))
    if not issues:
        issues = tuple(_semantics(packet))
    identifier = packet.get("packet_id") if isinstance(packet, dict) else None
    return PacketResult(identifier if isinstance(identifier, str) else None,
                        "rejected" if issues else "valid", issues)


def _identity(packet):
    body = packet["payload"]
    key = "fixture_id" if body["kind"] == "completed_match" else "snapshot_id"
    return body["kind"], body[key]


def _fingerprint(packet):
    canonical = json.dumps(packet, sort_keys=True, separators=(",", ":"), ensure_ascii=True)
    return hashlib.sha256(canonical.encode("ascii")).hexdigest()


def _event_identity(packet):
    body = packet["payload"]
    if body["kind"] != "completed_match":
        return None
    teams = tuple(sorted((body["home_team_id"], body["away_team_id"])))
    return (packet["competition_id"], packet["season_id"], body["kickoff_utc"],
            teams, packet["source"]["methodology_id"])


def validate_collection(packets):
    """Validate an ordered batch, with each predecessor supplied before its successor."""
    records, history = [], []
    seen, latest = {}, {}
    event_owners = {}
    valid = True
    for packet in packets:
        result = validate_packet(packet)
        if result.issues:
            records.append(result)
            valid = False
            continue
        identifier = packet["packet_id"]
        digest = _fingerprint(packet)
        key = _identity(packet)
        previous = latest.get(key)
        issue = None
        if identifier in seen:
            if seen[identifier] == digest:
                records.append(PacketResult(identifier, "duplicate"))
                continue
            issue = Issue("conflicting_packet", "$.packet_id", "Packet ID reused with changed content")
        elif packet["revision"] == 1 and previous:
            if previous["revision"] == 1 and all(packet[k] == previous[k] for k in packet if k != "packet_id"):
                seen[identifier] = digest
                records.append(PacketResult(identifier, "duplicate"))
                continue
            issue = Issue("conflicting_record", "$.payload", "Existing identity requires an explicit correction")
        elif packet["revision"] > 1:
            parent = packet["correction"]["predecessor_id"]
            if previous is None or parent != previous["packet_id"]:
                issue = Issue("invalid_predecessor", "$.correction.predecessor_id",
                              "Correction must reference the current revision of this identity")
            elif packet["revision"] != previous["revision"] + 1:
                issue = Issue("revision_gap", "$.revision", "Revision must increase by one")
            elif packet["recorded_at_utc"] < previous["recorded_at_utc"]:
                issue = Issue("time_order", "$.recorded_at_utc", "Correction predates its predecessor")
            elif any(packet[k] != previous[k] for k in ("competition_id", "season_id", "source")):
                issue = Issue("changed_scope", "$.correction", "Correction changed the record scope")
        event = _event_identity(packet)
        if issue is None and event_owners.get(event, key) != key:
            issue = Issue("fixture_alias", "$.payload.fixture_id",
                          "Event already belongs to another fixture ID; reconcile the declarations")
        if issue:
            records.append(PacketResult(identifier, "rejected", (issue,)))
            valid = False
        else:
            seen[identifier] = digest
            latest[key] = packet
            if event is not None:
                # Retain earlier event declarations so corrections cannot release aliases.
                event_owners[event] = key
            history.append(identifier)
            records.append(PacketResult(identifier, "accepted"))
    if not records:
        records.append(PacketResult(None, "rejected", (Issue("empty_batch", "$", "Supply at least one packet"),)))
        valid = False
    return BatchResult(valid, tuple(records), tuple(history) if valid else ())


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate invented ScreenshotBot v0.1 JSON packets in revision order")
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args(argv)
    packets = []
    for path in args.paths:
        try:
            packets.append(read_packet(path))
        except (OSError, ValueError, RecursionError) as exc:
            issue = Issue("read_error", str(path), str(exc))
            print(json.dumps(asdict(BatchResult(False, (PacketResult(None, "rejected", (issue,)),), ()))))
            return 1
    result = validate_collection(packets)
    print(json.dumps(asdict(result), indent=2))
    return 0 if result.valid else 1


if __name__ == "__main__":
    sys.exit(main())
