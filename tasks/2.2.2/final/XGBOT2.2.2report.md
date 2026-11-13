# XGBOT task 2.2.2 — XG-2A-R1 fixture identity correction

**Completed implementation and local verification 13 November 2026, Asia/Bangkok.**

## Scope and authority

The owner approved investigation, a bounded event-identity correction, regression tests, contract documentation, a dated historical addendum, these two task reports and a normal push updating existing draft PR #1. This task uses invented evidence and Python's standard library. XG-2B, source transfer, provider intake, licensing, merge and deployment remain separate owner decisions.

## BEFORE — verified starting state

GitHub confirmed Sayrsoe/XGBOT, ID 1454557271, default branch main. PR #1 was open, draft and unmerged. Its base was e3548df291b7cf1d460516d965a055179751277a and head was d3d83b7821dc6ac58ae987362a208d0704b702be on codex/xg-2a-contract-foundation. The local head and origin URL matched. These exact refs are the expected starting checkpoint. [Existing PR](https://github.com/Sayrsoe/XGBOT/pull/1)

Read AGENTS.md, the validator, contract schema and documentation, tests, historical handoff and numbered task 2.2.1 handover, with the previously recovered review findings. Existing untracked task 2.2.1 and XG-2B-P report files were preserved and excluded from staging. Task directory 2.2.2 was unused.

## Defect reproduction and original evidence

On the starting code, read invented example 02, deep-copy it, change packet_id to invented-alias and fixture_id to fixture-alias, then set home_xg raw_text and value to 9.00. validate_collection returned valid true, two accepted statuses and both packet IDs in history. The previously reported P2 defect was reproduced before implementation.

Added 15 regression methods before the correction. Running the targeted class on the original validator yielded 15 tests in 0.021 seconds, 8 failures, 0 errors and 0 skips, exit 1. Seven boundary/preservation cases already passed. The eight failures covered identical and conflicting aliases, swapped sides, changed capture reference, aliases after corrections, movement into another fixture and retained old-event ownership.

## DURING — alternatives and selected design

| Alternative | Assessment |
|---|---|
| Secondary event index alongside primary IDs | Selected. Linear batch traversal, existing revision checks remain in place, no wire-format change |
| Replace fixture IDs with event keys | Would alter primary identity and correction semantics unnecessarily |
| Silently merge aliases | Would erase disagreement and introduce implicit reconciliation |
| External team resolution or persistent registry | Requires broader scope and data authority |

The added helper _event_identity returns a key comprising competition_id, season_id, kickoff_utc, sorted team IDs and source.methodology_id. Sorting the team pair makes a reversed home/away claim collide. Capture references do not separate the event. Different competitions, seasons, kickoffs, pairs and methodology IDs remain distinguishable.

The collection keeps event_owners alongside seen packet IDs and latest primary revisions. Existing structural, semantic and predecessor checks run first. A candidate whose event is owned by another fixture gets fixture_alias at $.payload.fixture_id. Identical aliases are rejected too. A failed batch has empty importable history.

Corrections retain their original fixture ID and canonical predecessor semantics. The same fixture can explicitly correct side or kickoff declarations. Every accepted revision reserves its event key for the owning fixture throughout the batch. Old keys are retained so a correction cannot release an earlier declaration to a new ID. A correction also cannot move into another fixture's reserved event. Replays continue to be idempotent. No packet dictionary is modified.

Methodology is part of the measurement scope. Distinct methodology records being structurally distinct does not authorize treating them as independent training evidence. Ambiguous event ownership needs manual reconciliation outside this stateless protocol.

## Changed-file inventory

| Path | Change |
|---|---|
| xgbot/contracts/validator.py | Secondary event key and ownership check, 17 added lines |
| tests/test_contract_validator.py | 15 targeted FixtureAliasTests alongside the original 18 |
| docs/contracts/SCREENSHOTBOT_XGBOT_V0_1.md | Error, identity, side, correction and methodology policies; clarifies example 07's alias status in a batch with 02 |
| tasks/XG-2A/final/HANDOFF.md | Appended dated publication and R1 correction addendum |
| tasks/2.2.2/final/XGBOT2.2.2report.md | This implementation report |
| tasks/2.2.2/final/XGBOT2.2.2handover.md | AI-readable continuation handover |

The JSON schema, examples, original test expectations and previous research reports were preserved. Existing example 07 remains valid alone with unknown availability. Combined with 02 it now intentionally fails because it declares the same event under a different fixture ID.

## AFTER — test evidence

Environment was Windows and Python 3.12.10. Commands ran from the XGBOT repository root. Tests and scratch outputs reside under tasks/2.2.2/testing/ and are excluded from the committed file list.

Full suite:

```powershell
python -B -m unittest discover -s tests -p test_contract_validator.py -v
```

Result was **33 passed**, 0 failures, 0 errors, 0 skips, 0.425 seconds, exit 0. The original 18 methods and all 15 new methods passed.

Targeted suite, executed before and after the fix:

```powershell
python -B -m unittest discover -s tests -p test_contract_validator.py -k FixtureAliasTests -v
```

After correction, **15 passed**, 0 failures/errors/skips, 0.020 seconds, exit 0. Before correction, 8 failures were expected evidence of the defect. Logs are before-fix.log, contract-suite.log and alias-tests.log.

CLI checks:

```powershell
python -B -m xgbot.contracts.validator examples/invented/01-league.json examples/invented/02-match.json examples/invented/08-correction.json
python -B -m xgbot.contracts.validator examples/invented/02-match.json examples/invented/06-conflicting-fixture.json
python -B -m xgbot.contracts.validator examples/invented/02-match.json examples/invented/07-late-unknown.json
```

The first returned exit 0 with three accepted revisions. The second returned expected exit 1 with conflicting_record and empty history. The third returned expected exit 1 with fixture_alias and empty history. Logs are cli-valid.log, cli-conflict.log and cli-alias.log. Git diff --check passed after code and contract changes.

## Regression coverage

The targeted tests cover identical aliases, contradictory xG, contradictory goals, different kickoffs, different competition, distinct teams, exact replay and correction/replay, alias after correction, side reversal, changed capture reference, different methodology, different season, correction collision, retained prior event identity and same-ID side correction. Rejection helpers assert empty history and unchanged input dictionaries. Successful replay/correction checks also assert input immutability.

## Publication checkpoint and reproducibility

Branch is codex/xg-2a-contract-foundation. Starting head is d3d83b7821dc6ac58ae987362a208d0704b702be. The exact R1 implementation commit is **1a76130c7118b09f9d3ddded7c184c6a34157686**, tree **03ad7609bbae6a3a66fb027a0b9f165dc3f804e0**. It contains only validator, tests and contract changes. A following documentation-only commit records the addendum and reports, preserving this tested implementation commit as an ancestor.

The final publication head and tree are reported in the task completion response and are available through PR #1's head and Git history. This file records the exact code commit without attempting to embed the hash of the documentation commit that contains it. Verify the final head's diff from the code commit consists only of these two reports and the historical handoff addendum.

## Safety and limitations

Staging is restricted to the six named paths. Scratch logs and unrelated untracked reports remain local. The source changes introduce no dependency, provider data, credentials, licensing choice or mathematical module. No earlier historical handoff content was erased.

The protection applies only to a submitted batch and exact declared team IDs, kickoff and methodology. Inaccurately declared context can evade a purely local comparison. This phase has no external alias service, persistent cross-batch identity registry or trusted-time system. Actual ScreenshotBot exports, external schema-engine parity and other Python versions remain untested. Evidence verification is declarative.

## Final recommendation

The demonstrated alias gap is addressed by a bounded correction and targeted passing evidence. Recommend independent review of the exact final PR head, especially retained event ownership, same-ID identity corrections and methodology scope. Owner merge approval follows that review. PR #1 must remain draft and unmerged until separately authorized.

## Completion checklist

- [x] Repository and expected starting refs verified.
- [x] Original alias defect reproduced and pre-fix regressions recorded.
- [x] Secondary event identity, replay and revision semantics verified.
- [x] Original 18 and targeted 15 tests passed.
- [x] README CLI examples and alias CLI checked.
- [x] Contract policy and publication addendum documented.
- [x] Numbered report and handover prepared with final/testing separation.
- [x] Existing untracked reports excluded from the staged inventory.
- [x] XG-2B and real-provider work remain outside this implementation.

The publication step must independently verify remote refs, final head/tree and draft state before declaring the task published.
