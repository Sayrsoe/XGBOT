# ScreenshotBot to XGBOT · evidence contract 0.1

ScreenshotBot supplies one UTF-8 JSON object per file. XGBOT validates the supplied objects locally in order. A batch provides its entire relevant history, including predecessors. The public interface is a proposal for the future ScreenshotBot exporter. It can already be exercised using the [invented packets](../../examples/invented/).

## Envelope and provenance

| Field | Meaning |
|---|---|
| schema_version, packet_id | Literal string `0.1` and an immutable revision identifier. A new revision gets a new packet ID. |
| competition_id, season_id | Scope of the record. IDs throughout use lowercase ASCII letters, digits and single inter-word hyphens, start with a letter and have at most 80 characters. |
| source | Classification must equal `invented`. Reference uses `invented:<slug>`. The methodology ID identifies the xG definition shared by both sides. All example evidence and receipts are fabricated. |
| captured_at_utc | Time of the invented capture. |
| recorded_at_utc | Time this packet revision was recorded, at or after capture and at or after its predecessor’s recorded time. |
| availability | Either `{"status":"unknown"}` or `{"status":"verified","earliest_verified_at_utc":"…","evidence_ref":"…"}`. A verified availability claim requires its own receipt reference and cannot be later than recording. |
| revision, correction | First packet uses integer 1 and null. Each successor increments by one, names the active predecessor and gives a nonblank reason. |
| payload | Tagged object containing one league snapshot or one completed match. |

Timestamps are UTC calendar instants at whole-second precision, written as `YYYY-MM-DDTHH:MM:SSZ`. The capture and any claimed availability of a completed result must be strictly after kickoff. For a table they must be on or after its as-of time. Capture can occur later than a separately evidenced availability time. Unknown availability stays unknown even when a capture timestamp exists. These checks establish chronology within a declaration. The validator cannot authenticate a clock, receipt, image, source permission or completed-match status. This phase emits no historical eligibility decision.

## Evidence on observed fields

Each numeric observation carries `raw_text`, `value`, `unit`, `verification` and `evidence_ref`. Evidence references are identifiers scoped to the invented source. Producers should use stable locators for the field and its label/column. Identity evidence has a verification decision and a reference to the team/side headers. IDs and record metadata can be assigned by the producer. A field marked pending, an absent critical locator or a contradictory transcription prevents admission.

Use `verified` for an accepted observation. Use ASCII plain decimal strings for xG/xGA/xPts, up to 32 characters including the point, with digits on both sides of an optional decimal point. Negative, non-finite, exponent and locale-specific spellings are invalid for these metrics in v0.1. Preserve the original raw precision. `"1.400"` and parsed `"1.40"` agree numerically. Goals and matches played use nonnegative JSON integers. Actual points use signed integers so a table can represent deductions. Raw and parsed amounts must agree. A zero is an observed amount. Optional xPts can be omitted or null. Required unknown quantities produce a failure rather than a partial accepted match.

## League statistics snapshot

Use kind `league_snapshot`, a stable `snapshot_id`, `table_as_of_utc`, basis `season_totals`, coverage `partial` or `complete`, and at least one team row. Each row carries team identity evidence, matches played, total xG, total xGA, optional total xPts and actual points. Each team appears at most once. Units in the numeric field objects are `matches`, `xG` or `points` as specified by the schema. Coverage describes the producer’s supplied table. Validation does not establish that a league roster is complete. Use a new snapshot ID for a new edition of a table and a successor revision for correction of the same snapshot.

## Completed match

Use kind `completed_match`, a stable `fixture_id`, kickoff, distinct home and away team IDs and verified identity evidence. Period must be `full_time_regulation`. Supply home and away regulation goals including stoppage time, and home and away match xG. The producer excludes extra time and penalty shootouts from this profile. Match xGA is derived by perspective. Home xGA equals away xG for the same fixture and provider methodology, and vice versa. Supplying an additional match xGA or market field fails structural validation.

## Collection and replay

The identity key is the pair of payload kind and fixture/snapshot ID. IDs are stable across revisions and must be unique within each kind across the submitted history. Competition, season and source including methodology remain fixed for a correction.

R1 additionally indexes completed-match events by competition, season, UTC kickoff, unordered team pair and source methodology ID. A different fixture ID claiming the same event yields `fixture_alias` and rejects the batch even if statistics agree. Swapped home/away declarations share this secondary key and require reconciliation. Capture references and packet IDs cannot distinguish events. Different competitions, seasons, kickoffs, team pairs or methodologies have distinct event keys. Methodology separation describes measurement scope and supplies no permission to combine observations as independent model evidence.

The existing fixture ID and predecessor chain remain authoritative for explicit corrections, including a reviewed side or kickoff correction. Every accepted revision reserves its declared event key for that fixture throughout the batch. A correction cannot move into an event already owned by another fixture, and an earlier event declaration stays reserved after a correction. Reconcile ambiguous ownership outside this v0.1 batch rather than silently merge or reassign it. Exact accepted packet replays remain idempotent. League snapshot identity is unchanged. The JSON wire format remains version 0.1.

- Replaying a known packet ID with the same canonical content returns `duplicate`. JSON whitespace and key order do not change that content. Changing the content under that ID yields `conflicting_packet`.
- A second initial packet for the same active initial record is a duplicate if every field except packet ID agrees. Its alias contributes no history entry. Reference the accepted canonical packet ID for a correction.
- Other parallel initial records for that identity yield `conflicting_record`, including competing captures. Resolve disagreement explicitly before submitting the accepted correction chain.
- A successor must reference the current canonical revision of the same identity. A missing parent, fork, skipped revision or scope change fails. Successful history includes both the predecessor and successor IDs in input order. Retain the original packet files to replay the values.
- The result has `valid`, per-input `records` with status and issues, and `history`. An issue names its category, path and reason. On any failure, history is empty and no part of the batch is eligible for import. Individual accepted statuses on a failed batch are diagnostic. The validator is stateless and writes no records. A future store would need transactional cross-batch guarantees.
- The CLI stops on an unreadable or invalid JSON file with a file-specific `read_error`. It rejects repeated JSON keys and nonstandard numeric constants before semantic validation.

## Interface and schema

Structural requirements live in the [Draft 2020-12 schema](../../schemas/screenshot_evidence_v0_1.json). The standard-library validator reads that specific file using its fixed v0.1 vocabulary. Its additional application checks cover strict integer representation, real calendar dates, transcriptions, chronology, identity, duplicates and revision chains. Generic schema validation alone cannot establish collection validity. Treat unsupported versions, extra properties and unknown kinds as failures.

Use `validate_packet(decoded_object)` for a single JSON-shaped object and `validate_collection(iterable)` for a batch. A standalone correction may be structurally and semantically valid while its batch still needs its predecessor. Use `read_packet(path)` or the documented CLI when decoding untrusted JSON so duplicate keys remain detectable.

## Invented reference cases

| File in examples/invented | Expected result |
|---|---|
| 01-league.json | Accepted partial season table with null xPts. |
| 02-match.json | Accepted initial completed match. |
| 03-negative-xg.json | Rejected at home xG. |
| 04-incomplete.json | Rejected for missing away goals. |
| 05-invalid-team.json | Rejected for malformed home ID. |
| 06-conflicting-fixture.json | Valid in isolation. After 02 it conflicts with an existing fixture. |
| 07-late-unknown.json | Accepted alone with later capture and explicitly unknown availability. In a batch with 02, R1 rejects its different fixture ID for the same event as `fixture_alias`. |
| 08-correction.json | Accepted after 02, preserving both packet IDs. Rejected as a singleton batch. |

Only the local invented protocol has been exercised. Actual producer compatibility, storage, rights clearance and independent historical evidence require later work.
