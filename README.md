# XGBOT

XGBOT validates invented football evidence exported under the proposed ScreenshotBot JSON contract v0.1. It accepts season-total league tables and completed regulation-match records. A successful batch identifies the ordered packet revisions a consumer could retain. Phase XG-2A covers local validation only.

## Run locally

Use Python 3.10 or newer and run from the repository root. The validator uses the Python standard library and the checked-in schema.

```powershell
python -B -m xgbot.contracts.validator examples/invented/01-league.json examples/invented/02-match.json examples/invented/08-correction.json
```

The valid example returns exit code 0 and three packet IDs in history. Supply the predecessor before its correction. To exercise a conflict, use the following pair.

```powershell
python -B -m xgbot.contracts.validator examples/invented/02-match.json examples/invented/06-conflicting-fixture.json
```

A rejected batch returns exit code 1, a reason and field path, and an empty history. An exact replay is a successful duplicate and contributes no additional revision.

## Run the bounded tests

```powershell
python -B -m unittest discover -s tests -p test_contract_validator.py -v
```

Read the [v0.1 producer and consumer contract](docs/contracts/SCREENSHOTBOT_XGBOT_V0_1.md), [schema](schemas/screenshot_evidence_v0_1.json) and [XG-2A handoff](tasks/XG-2A/final/HANDOFF.md). The producer and consumer can use the invented examples for future interoperability checks.
