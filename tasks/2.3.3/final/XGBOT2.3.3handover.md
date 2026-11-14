# XGBOT2.3.3handover.md

**Project:** XGBOT  
**Task:** 2.3.3 — Draft edge-analysis blueprint and owner walkthrough  
**Date:** 2026-11-14  
**Status:** Documentation draft created for review only, on `docs/xgbot-2.3.3-edge-analysis-draft`. No implementation approval inferred.

## Owner request and decisions
- Asked for an edge-focused analysis assistant that presents probabilities, price comparison, statistics, reasoning and uncertainty; owner makes the final choice and may veto/skip.
- Asked for a draft walkthrough to be saved in the GitHub XGBOT repository, to later open from Windows VS Code.
- Requested a real odds comparison for Portugal 1X vs Denmark +2.5 as a paper test. No stakes or guaranteed-winner claim.
- Preserve existing Asian Handicap-first, pre-match, evidence-driven, NO EDGE and planning-only boundaries; double-chance is an analysis comparison, **not a silently approved new market**.
- Owner-reported profitability (~+20 units at 500 THB, ~70% hit rate) remains unverified.
- No automated betting, no code changes, no XG-2B numerical transfer, no deployment.

## GitHub evidence
- Repository: https://github.com/Sayrsoe/XGBOT
- Base `main` SHA at task start: `d2c9528735859fbc2850135302d5c13f5357cf82`
- Base merge tree: `6e222305b66a6e2dea360b1ec3d58ee4e1360a7c`
- README: XG-2A contract validator, standard-library Python, invented samples; existing `AGENTS.md` requires separate owner authorization for later phases.
- Draft branch: `docs/xgbot-2.3.3-edge-analysis-draft`
- Draft document: `tasks/2.3.3/final/EDGE_ANALYSIS_BLUEPRINT_DRAFT.md`

## Worked paper comparison
- FotMob screenshot: 4-played totals Portugal xG/xGA/xPTS = 7/5/7, Denmark = 5/5/6. Portugal actual points 12, Denmark actual 6.
- Online pre-match odds examples as of search 2026-11-14: Portugal 1X 1.14 (SportyTrader), Denmark +2.5 1.21 (bookmakers-rating.top). Confirm at actual bookmaker before comparing any market; no live actionable odds confirmation.
- Break even: 87.7193% and 82.6446%.
- Illustrative Poisson probabilities at expected-goals assumptions 1.50/1.25: 68.36%, 91.71%; at 2.10/1.30: 76.71%, 83.08%; at 2.50/1.00: 86.87%, 72.02%. Not calibrated or validated. **No verified edge**.
- Settlement: Portugal 1X succeeds when Portugal win/draw; Denmark +2.5 succeeds unless Portugal win by 3+.

## Work done and evidence
- Read GitHub repo README, AGENTS, layout, main branch commit and XG-2A handoff (read-only).
- Created documentation-only GitHub branch off verified main SHA.
- Authored planning blueprint, mathematical walkthrough and case-study scenario table on the branch.
- Historical tests: no local runtime tests triggered; no new code. Simple probability arithmetic independently computed for the paper example.

## Open risks and blockers
- Historical stats are only four matches; market examples come from distinct sites and may move.
- No rights-cleared systematic Opta/FotMob input, no calibrated forecast, no model validation.
- Exact computer filesystem path is unknown and cannot be inferred; GitHub branch does not mean file downloaded to the user's Windows computer.
- Main-branch merge, code, ingestion, deployment and market expansion require new explicit authorization.

## Next steps
1. Owner reviews blueprint and corrects/approves any reasoning.
2. Optional read-only Codex audit scoped to probability model, settlement, rights and validation.
3. Separately authorize any subsequent code, PR, merges, licensed data ingestion or deployment.
4. On Windows, follow the `git fetch` and `git switch` walkthrough inside the blueprint to retrieve the draft.

**Handover file path:** `tasks/2.3.3/final/XGBOT2.3.3handover.md` on documentation branch.
