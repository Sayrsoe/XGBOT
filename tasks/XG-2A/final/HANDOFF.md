# XG-2A implementation handoff

## A. Verified repository state

The GitHub repository is [Sayrsoe/XGBOT](https://github.com/Sayrsoe/XGBOT), ID 1454557271, public, with main configured as the default branch name. GitHub returned HTTP 409 “Git Repository is empty” on both the initial and publication-time main commit lookup. Branch search returned an empty list. Local origin points to that repository.

The implementation occupies a new XGBOT subdirectory under the existing XG Bot workspace. The earlier XG-1 report remains in the parent directory. This stage used standard-library Python and Git. Work was confined to the new local project.

## B. Changed-file manifest

All paths below are new in the local XGBOT project.

| Files | Purpose |
|---|---|
| README.md, AGENTS.md, .gitignore | Running instructions, project scope and ignored temporary output |
| xgbot/__init__.py, xgbot/contracts/__init__.py | Importable package |
| xgbot/contracts/validator.py | Single-packet checks, ordered collection validation, strict JSON reader and CLI |
| schemas/screenshot_evidence_v0_1.json | Versioned structural contract |
| docs/contracts/SCREENSHOTBOT_XGBOT_V0_1.md | Producer/consumer field semantics, time, evidence, identity and correction rules |
| examples/invented/01-league.json, examples/invented/02-match.json | Valid initial packets |
| examples/invented/03-negative-xg.json, examples/invented/04-incomplete.json, examples/invented/05-invalid-team.json | Invalid independent packets |
| examples/invented/06-conflicting-fixture.json, examples/invented/07-late-unknown.json, examples/invented/08-correction.json | Conflict against 02, unknown prior availability, correction of 02 |
| tests/test_contract_validator.py | 18 bounded tests including CLI and parser exercises |
| tasks/XG-2A/final/HANDOFF.md | Review evidence, inventory, limitations and publication decision |

The local test transcript is in tasks/XG-2A/testing/contract-tests.log. Git’s ignore check identified the testing-directory rule. No archive or additional dependencies are required for review.

## C. Contract decisions

Only declared invented evidence is eligible. Critical numeric fields require original text, a separately typed value, correct unit, verified disposition and evidence locator. Totals are explicit. Unknown xPts may be null or absent. Match xGA is derived from opposite-side xG. Read the [contract](../../../docs/contracts/SCREENSHOTBOT_XGBOT_V0_1.md) for the complete wire format and limits.

A correction uses a new packet ID, incremented revision, reason and canonical predecessor. An ordered batch may contain repeat deliveries. Identical deliveries contribute one revision. Changed content under the same ID or a second conflicting initial observation fails the batch. Input objects remain intact. A failed batch returns reasons and an empty importable history.

## D. Test execution evidence

Environment: Windows, Python 3.12.10. Working directory: XGBOT repository root.

```powershell
python -B -m unittest discover -s tests -p test_contract_validator.py -v
```

Result: 18 tests ran in 0.390 seconds, all passed, exit 0, no failures, errors or skips. Coverage includes both packet types, versions and origins, field evidence and units, decimal mismatch, negative/non-finite values, identity and time, nullable/absent/zero xPts, late capture, duplicates, corrections, conflicts and strict CLI decoding.

The two README commands were independently executed:

```powershell
python -B -m xgbot.contracts.validator examples/invented/01-league.json examples/invented/02-match.json examples/invented/08-correction.json
python -B -m xgbot.contracts.validator examples/invented/02-match.json examples/invented/06-conflicting-fixture.json
```

The first returned exit 0 and three accepted revision IDs in input order. The second returned the expected exit 1, issue code `conflicting_record` at `$.payload`, and empty history. This rejection is the expected result for the invented conflict case.

## E. Remaining issues and risks

The validator identifies declarations and their internal consistency. Evidence locators are symbolic in these examples. Real provenance, provider permission, source publication time and exporter compatibility remain unverified. Ordering and coverage checks apply only to the submitted batch. Durable storage, cross-process deduplication and automated conflict adjudication require a separately authorized stage. The suite exercised the bundled schema on Python 3.12.10. Other Python versions and external JSON Schema implementations were not tested.

## F. Branch and PR status

Local feature branch: `codex/xg-2a-contract-foundation`. The publication-time lookup found no base commit or branch. No remote branch was written, and there is no draft PR. A commit-scoped Codex identity is used for local preparation because the new checkout has no configured Git author. The root implementation commit can be identified with `git rev-parse HEAD` in this checkout.

## G. Acceptance checklist

- [x] Verified the target repository ID, preserved the existing workspace file and restricted work to the new local directory.
- [x] No main push, dependency installation, license selection or changes to either reference project.
- [x] Accepted valid invented league and match packets. Rejected unsupported versions, missing critical fields, invalid numbers, dates and identities.
- [x] Preserved missing/null xPts and observed zero as distinct inputs.
- [x] Required invented origin and verified field references. Rejected unsupported provider classifications.
- [x] Detected duplicates and conflicts, retained valid correction chains and kept unknown availability unknown.
- [x] README and contract document local interfaces, exact commands and XG-2A capabilities.
- [x] Executed the bounded suite using invented data. The file manifest includes only foundation, contract, examples, tests and handoff.
- [ ] Remote main bootstrap and draft PR, pending the owner’s publication decision.

## H. Next owner decision

Recommended bootstrap: authorize one empty initial commit on remote main. Once that base exists, replay the local XG-2A implementation commit on top of it, verify the resulting feature tree and bounded tests, push only the feature branch and open a draft PR targeting main. An independent initial commit requires replay onto the common base so GitHub can compare the branches. The owner can also establish the initial base themselves. XG-2B remains a separate future decision.
