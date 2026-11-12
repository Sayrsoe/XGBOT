# XGBOT task 2.2.2 — R1 handover

The fixture-ID alias defect is corrected. All 33 contract tests passed. The next step is independent review of the exact updated PR #1 head and eventual owner merge approval. [Technical report](XGBOT2.2.2report.md)

## Scope and repository

Task 2.2.2, XG-2A-R1, was approved for a targeted correction, tests, contract documentation, an appended historical addendum and publication to the existing feature branch. Repository is Sayrsoe/XGBOT, ID 1454557271. [PR #1](https://github.com/Sayrsoe/XGBOT/pull/1) was verified open, draft and unmerged at starting base e3548df291b7cf1d460516d965a055179751277a and head d3d83b7821dc6ac58ae987362a208d0704b702be.

## Correction and decisions

Primary fixture IDs and predecessor chains remain authoritative. A secondary key uses competition, season, kickoff, unordered teams and methodology. A different fixture ID claiming an owned event produces fixture_alias, including identical statistics and swapped sides. Capture reference changes cannot hide an alias.

Explicit same-ID corrections remain valid. Prior event keys stay reserved across revisions, preventing alias admission after an identity correction. A correction moving into another fixture's event fails. No input object is mutated. Distinct declared methodologies are separate measurement scopes. This supplies no downstream independent-evidence assumption.

## Files changed

- xgbot/contracts/validator.py
- tests/test_contract_validator.py
- docs/contracts/SCREENSHOTBOT_XGBOT_V0_1.md
- tasks/XG-2A/final/HANDOFF.md, append-only addendum
- tasks/2.2.2/final/XGBOT2.2.2report.md
- tasks/2.2.2/final/XGBOT2.2.2handover.md

Task 2.2.1 and XG-2B-P untracked reports were preserved and excluded from staging.

## Tests and evidence

On Python 3.12.10 from the XGBOT root:

```powershell
python -B -m unittest discover -s tests -p test_contract_validator.py -v
python -B -m unittest discover -s tests -p test_contract_validator.py -k FixtureAliasTests -v
```

Full suite returned 33 passed, 0 failed/errors/skips in 0.425 seconds. Targeted run returned 15 passed, 0 failed/errors/skips in 0.020 seconds. Before the fix, the targeted suite returned 8 failures among 15 tests, reproducing the defect. Both original README CLI commands behaved as documented. Combined examples 02/07 now reject with fixture_alias and empty history. The report lists exact commands and log names. Scratch logs live only in tasks/2.2.2/testing/.

## Commit checkpoint

Feature branch is codex/xg-2a-contract-foundation. Tested implementation commit is 1a76130c7118b09f9d3ddded7c184c6a34157686 and tree is 03ad7609bbae6a3a66fb027a0b9f165dc3f804e0. A following documentation-only commit adds reports and the historical addendum. Obtain its exact final publication SHA/tree from PR #1 and the task completion response. Check that its code tree matches the tested implementation files.

## Remaining limitations and next gate

The validator is stateless and relies on declared IDs/times/methodology. Cross-batch reconciliation, external identity services, evidence authenticity, real provider use, exporter parity and statistical models remain outside this phase. Example 07 is still valid alone with unknown availability. Its different ID for the same event as 02 is now explicitly rejected in a combined batch.

Ask an independent reviewer to review final code, correction-chain behaviour, scope and test evidence at the exact published head. The owner decides on merge afterward. No merge, deployment, new PR, numerical transfer, dependency installation or XG-2B work is authorized by this handover.

[Contract](../../../docs/contracts/SCREENSHOTBOT_XGBOT_V0_1.md) · [Historical handoff with addendum](../../XG-2A/final/HANDOFF.md)
