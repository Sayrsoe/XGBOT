import copy
from dataclasses import asdict
import json
from pathlib import Path
import subprocess
import sys
import unittest

from xgbot.contracts.validator import read_packet, validate_collection, validate_packet


ROOT = Path(__file__).resolve().parents[1]
EXAMPLES = ROOT / "examples" / "invented"


def example(name):
    return read_packet(next(EXAMPLES.glob(name + "-*.json")))


def codes(result):
    return {issue.code for issue in result.issues}


class FixtureAliasTests(unittest.TestCase):
    def setUp(self):
        self.match = example("02")
        self.correction = example("08")
        self.alias = copy.deepcopy(self.match)
        self.alias["packet_id"] = "invented-alias"
        self.alias["payload"]["fixture_id"] = "fixture-alias"

    def assert_alias_rejected(self, packets):
        before = copy.deepcopy(packets)
        result = validate_collection(packets)
        self.assertFalse(result.valid)
        self.assertEqual(result.history, ())
        self.assertIn("fixture_alias", codes(result.records[-1]))
        self.assertEqual(packets, before)

    def test_identical_statistics_alias(self):
        self.assert_alias_rejected([self.match, self.alias])

    def test_conflicting_xg_alias(self):
        self.alias["payload"]["home_xg"].update(raw_text="9.00", value="9.00")
        self.assert_alias_rejected([self.match, self.alias])

    def test_conflicting_goals_alias(self):
        self.alias["payload"]["away_goals"].update(raw_text="4", value=4)
        self.assert_alias_rejected([self.match, self.alias])

    def test_different_kickoff(self):
        self.alias["payload"]["kickoff_utc"] = "2026-01-08T16:00:00Z"
        self.assertTrue(validate_collection([self.match, self.alias]).valid)

    def test_different_competition(self):
        self.alias["competition_id"] = "other-competition"
        self.assertTrue(validate_collection([self.match, self.alias]).valid)

    def test_different_teams(self):
        self.alias["payload"]["away_team_id"] = "amber-town"
        self.assertTrue(validate_collection([self.match, self.alias]).valid)

    def test_replay_and_correction_chain(self):
        packets = [self.match, self.match, self.correction, self.correction]
        before = copy.deepcopy(packets)
        result = validate_collection(packets)
        self.assertTrue(result.valid)
        self.assertEqual([r.status for r in result.records], ["accepted", "duplicate", "accepted", "duplicate"])
        self.assertEqual(result.history, (self.match["packet_id"], self.correction["packet_id"]))
        self.assertEqual(packets, before)

    def test_alias_after_correction(self):
        self.assert_alias_rejected([self.match, self.correction, self.alias])

    def test_swapped_sides_alias(self):
        body = self.alias["payload"]
        body["home_team_id"], body["away_team_id"] = body["away_team_id"], body["home_team_id"]
        self.assert_alias_rejected([self.match, self.alias])

    def test_capture_reference_cannot_hide_alias(self):
        self.alias["source"]["reference"] = "invented:another-capture"
        self.assert_alias_rejected([self.match, self.alias])

    def test_different_methodology(self):
        self.alias["source"]["methodology_id"] = "other-methodology"
        self.assertTrue(validate_collection([self.match, self.alias]).valid)

    def test_different_season(self):
        self.alias["season_id"] = "season-beta"
        self.assertTrue(validate_collection([self.match, self.alias]).valid)

    def test_correction_cannot_move_into_another_fixture(self):
        other = copy.deepcopy(self.alias)
        other["payload"]["kickoff_utc"] = "2026-01-08T16:00:00Z"
        self.correction["payload"]["kickoff_utc"] = other["payload"]["kickoff_utc"]
        self.assert_alias_rejected([self.match, other, self.correction])

    def test_old_event_remains_reserved_after_identity_correction(self):
        self.correction["payload"]["kickoff_utc"] = "2026-01-08T16:00:00Z"
        self.assert_alias_rejected([self.match, self.correction, self.alias])

    def test_side_correction_on_same_fixture(self):
        body = self.correction["payload"]
        body["home_team_id"], body["away_team_id"] = body["away_team_id"], body["home_team_id"]
        self.assertTrue(validate_collection([self.match, self.correction]).valid)


class ContractTests(unittest.TestCase):
    def setUp(self):
        self.match = example("02")
        self.table = example("01")
        self.correction = example("08")

    def test_reference_examples(self):
        for name in ("01", "02", "07", "08"):
            with self.subTest(name=name):
                self.assertEqual(validate_packet(example(name)).status, "valid")
        for name, path in [("03", "home_xg"), ("04", "away_goals"), ("05", "home_team_id")]:
            with self.subTest(name=name):
                self.assertTrue(any(path in issue.path for issue in validate_packet(example(name)).issues))

    def test_source_and_version(self):
        self.match["source"]["classification"] = "real_provider"
        self.match["schema_version"] = "0.2"
        self.assertEqual(codes(validate_packet(self.match)), {"unsupported_source", "unsupported_version"})

    def test_required_evidence(self):
        for name in ("verification", "evidence_ref", "raw_text", "value"):
            packet = copy.deepcopy(self.match)
            del packet["payload"]["home_xg"][name]
            with self.subTest(name=name):
                self.assertIn("missing_field", codes(validate_packet(packet)))
        self.match["payload"]["identity_evidence"]["verification"] = "pending"
        self.assertIn("unexpected_value", codes(validate_packet(self.match)))

    def test_numeric_formats(self):
        for value in ("-0.01", "Infinity", "NaN", "2e0", ".5", "", -1, 1.5, True, None):
            self.match["payload"]["home_xg"]["value"] = value
            with self.subTest(value=value):
                self.assertEqual(validate_packet(self.match).status, "rejected")
        self.table["payload"]["rows"][0]["matches_played"]["value"] = True
        self.assertIn("invalid_type", codes(validate_packet(self.table)))

    def test_raw_and_parsed(self):
        observation = self.match["payload"]["home_xg"]
        observation["raw_text"] = "1.400"
        self.assertEqual(validate_packet(self.match).status, "valid")
        observation["raw_text"] = "14.0"
        self.assertIn("transcription_mismatch", codes(validate_packet(self.match)))

    def test_xpts_absent_null_and_zero(self):
        row = self.table["payload"]["rows"][0]
        for state in ("null", "absent", "zero"):
            if state == "absent":
                del row["total_xpts"]
            elif state == "zero":
                row["total_xpts"] = dict(row["total_xg"], raw_text="0.00", value="0", unit="points")
            original = copy.deepcopy(row)
            with self.subTest(state=state):
                self.assertEqual(validate_packet(self.table).status, "valid")
                self.assertEqual(row, original)

    def test_team_and_packet_ids(self):
        for team in (" space", "", "INVALID", "a--b", "copper-vale\n", self.match["payload"]["away_team_id"]):
            self.match["payload"]["home_team_id"] = team
            with self.subTest(team=team):
                self.assertEqual(validate_packet(self.match).status, "rejected")
        self.table["packet_id"] = "???"
        self.assertIn("invalid_format", codes(validate_packet(self.table)))

    def test_table_scope(self):
        row = self.table["payload"]["rows"][0]
        self.table["payload"]["rows"].append(copy.deepcopy(row))
        self.assertIn("duplicate_team", codes(validate_packet(self.table)))
        self.table["payload"]["basis"] = "per_match"
        row["total_xga"]["unit"] = "goals"
        self.assertIn("unexpected_value", codes(validate_packet(self.table)))

    def test_forbidden_fields_and_tags(self):
        for name in ("home_xga", "odds"):
            packet = copy.deepcopy(self.match)
            packet["payload"][name] = 0
            self.assertIn("unknown_field", codes(validate_packet(packet)))
        self.match["payload"]["kind"] = "unknown"
        self.assertIn("invalid_tag", codes(validate_packet(self.match)))

    def test_timestamps(self):
        for value in ("2026-02-29T12:00:00Z", "2026-01-08", "2026-01-08T15:00:00+00:00",
                      "2026-01-08T25:00:00Z", self.match["payload"]["kickoff_utc"]):
            self.match["captured_at_utc"] = value
            with self.subTest(value=value):
                self.assertEqual(validate_packet(self.match).status, "rejected")

    def test_availability(self):
        late = example("07")
        self.assertTrue(validate_collection([late]).valid)
        self.assertEqual(late["availability"], {"status": "unknown"})
        late["availability"]["earliest_verified_at_utc"] = late["captured_at_utc"]
        self.assertIn("unknown_field", codes(validate_packet(late)))
        self.match["availability"]["earliest_verified_at_utc"] = "2026-01-08T14:00:00Z"
        self.assertIn("time_order", codes(validate_packet(self.match)))
        self.match["availability"]["earliest_verified_at_utc"] = "2026-01-10T14:00:00Z"
        self.assertIn("time_order", codes(validate_packet(self.match)))

    def test_duplicates_and_id_collision(self):
        alias = dict(self.match, packet_id="invented-alias")
        result = validate_collection([self.match, self.match, alias])
        self.assertEqual([r.status for r in result.records], ["accepted", "duplicate", "duplicate"])
        self.assertEqual(result.history, (self.match["packet_id"],))
        conflict = example("06")
        conflict["packet_id"] = self.match["packet_id"]
        result = validate_collection([self.match, conflict])
        self.assertIn("conflicting_packet", codes(result.records[-1]))
        self.assertFalse(result.valid)
        self.assertEqual(result.history, ())

    def test_fixture_and_table_conflict(self):
        for original, conflict in [(self.match, example("06")), (self.table, copy.deepcopy(self.table))]:
            if original is self.table:
                conflict["packet_id"] = "different-table-packet"
                conflict["payload"]["coverage"] = "complete"
            result = validate_collection([original, conflict])
            self.assertIn("conflicting_record", codes(result.records[-1]))
            self.assertEqual(result.history, ())

    def test_correction_history_and_replay(self):
        originals = copy.deepcopy([self.match, self.correction])
        result = validate_collection([self.match, self.correction, self.match, self.correction])
        self.assertEqual(result.history, (self.match["packet_id"], self.correction["packet_id"]))
        self.assertEqual([r.status for r in result.records], ["accepted", "accepted", "duplicate", "duplicate"])
        self.assertEqual(originals, [self.match, self.correction])

    def test_missing_stale_or_wrong_predecessor(self):
        fork = dict(self.correction, packet_id="fork")
        wrong_key = copy.deepcopy(self.correction)
        wrong_key["payload"]["fixture_id"] = "another-fixture"
        for batch in [[self.correction], [self.match, self.correction, fork], [self.match, wrong_key]]:
            self.assertIn("invalid_predecessor", codes(validate_collection(batch).records[-1]))

    def test_revision_sequence_and_scope(self):
        for changes, expected in [({"revision": 3}, "revision_gap"),
                                  ({"competition_id": "other-league"}, "changed_scope"),
                                  ({"recorded_at_utc": self.match["captured_at_utc"]}, "time_order"),
                                  ({"correction": None}, "invalid_revision")]:
            packet = dict(self.correction, **changes)
            self.assertIn(expected, codes(validate_collection([self.match, packet]).records[-1]))

    def test_empty_batch(self):
        self.assertFalse(validate_collection([]).valid)

    def test_cli_and_strict_json(self):
        command = [sys.executable, "-B", "-m", "xgbot.contracts.validator"]
        paths = [str(next(EXAMPLES.glob(n + "-*.json"))) for n in ("02", "08")]
        run = subprocess.run(command + paths, cwd=ROOT, capture_output=True, text=True)
        self.assertEqual(run.returncode, 0, run.stderr)
        self.assertEqual(json.loads(run.stdout), json.loads(json.dumps(asdict(validate_collection(
            [self.match, self.correction])))))
        scratch = ROOT / "tasks" / "XG-2A" / "testing"
        scratch.mkdir(parents=True, exist_ok=True)
        from tempfile import TemporaryDirectory
        with TemporaryDirectory(dir=scratch) as temp:
            path = Path(temp) / "invalid.json"
            for raw in ('{"a":1,"a":2}', '{"value":NaN}', '{"value":Infinity}', '{'):
                path.write_text(raw, encoding="utf-8")
                run = subprocess.run(command + [str(path)], cwd=ROOT, capture_output=True, text=True)
                self.assertEqual(run.returncode, 1)
                self.assertEqual(json.loads(run.stdout)["records"][0]["issues"][0]["code"], "read_error")
