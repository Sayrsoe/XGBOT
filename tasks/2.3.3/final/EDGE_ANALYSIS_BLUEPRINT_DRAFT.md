# XGBOT 2.3.3 — Edge-analysis assistant blueprint (DRAFT)

**Status:** Proposal only; not an approved implementation phase. **Date:** 2026-11-14.
**Parent branch at drafting:** `main` commit `d2c9528735859fbc2850135302d5c13f5357cf82`.
**Scope:** Documentation and offline paper-model design only. No live odds ingestion, deployment, numerical transfer from PremFootballBot, scraping, stake sizing, or automated wagering.

## 1. Owner intent

Produce a human-in-the-loop Asian Handicap analysis assistant. The bot **computes and explains**, while the owner **decides, overrides, or skips**. Optimize for **probability calibration, positive expected value (EV), and auditable decision quality**, not raw hit rate or guaranteeing wins. A conservative "NO EDGE" is an acceptable and important result. Owner-reported 70% recent win rate and ~+20 units at THB 500/unit are unverified; do not calibrate the model using these claims without complete bet records.

### Owner's scenario heuristic (hypothesis, not hard-coded edge)
- Ask *how many goals* a favored team might win by, not just *who* wins.
- Consider a set of scorelines, including draws and unexpected reversals.
- Compare higher-cushion Asian Handicap positions against mainstream lines; a high cover rate **alone does not** prove value.
- Use xG, xGA, xPTS, home/away, group incentives and opponent strength as input signals, not automatic conclusions.
- Seek explicit reasons to say NO EDGE when estimated probability does not clear the book's break-even after uncertainty.

## 2. Existing state and constraints

As verified on GitHub on 2026-11-14, `Sayrsoe/XGBOT` `main` contains the merged **XG-2A evidence-contract validator** (v0.1), invented local evidence examples and contract tests. The repo README does *not* claim a predictive model or live provider connection. `AGENTS.md` reserves implementation, publication, merges, real-money actions and new phases for owner authorization. Prior XG-2B-P was read-only technical audit/planning. This document does not override those boundaries.

## 3. Proposed pipeline (not executable)

1. **Evidence ingestion / licensing gate:** Use authorized historical inputs; verify FotMob/Opta attribution, reuse rights, allowed retention and permitted automation before any provider integration. Never assume visual access implies scraping or republication rights. Keep source timestamps, match identity, source labels and corrections.
2. **Data quality gate:** Validate fixture status, completed 90-minute regulation record, xG/xGA units, xPTS definition and provenance, nulls, duplicates, consistency, season and match coverage. For small samples, show uncertainty rather than confidence.
3. **Strength estimation:** Derive attack/defense factors relative to league/competition baseline and opponent strength; handle home advantage, current lineups/injuries, schedule, match incentives, formation changes and regression to mean. Compare simple Poisson baseline against hierarchical/shrunk Poisson, Dixon-Coles for low scores, and alternatives using out-of-sample evidence.
4. **Scoreline distribution:** For illustrative independent Poisson: `P(H=h,A=a)=Pois(h;lambda_home)*Pois(a;lambda_away)`. Sum a sufficiently large probability grid (e.g. 0..15, confirm residual < 0.0001) and compute outcome probabilities. Never compare only one 1-1 scoreline with one 4-0 scoreline.
5. **Asian Handicap settlement:** Enumerate line outcomes correctly, including quarter-goal split, half win/loss, push and refunds. For +2.5, cover iff `home_goals-away_goals <= 2`. For double chance 1X, win iff `home_goals >= away_goals` in 90 minutes.
6. **Fair price and EV:** For two-way all-or-nothing positions, break even at `p=1/decimal_odds`. `EV_per_unit=p*(odds-1)-(1-p)=p*odds-1`. For push/quarter lines use full expected settlement formula; do not apply a binary break-even shortcut. Account for bookmaker margin, stale prices, spread/limits, and model-uncertainty bands.
7. **Decision guardrails:** `NO EDGE` if history/data rights/provenance are unverified, sample too weak, input stale, probability/price unavailable, or robust lower-confidence EV does not clear a predeclared threshold. Selection suggestions are hypotheses for **paper testing only**.
8. **Human review and logging:** Short summary (suggested line, odds, break-even, estimated cover, uncertainty, xG and xGA, most consequential assumptions, reason to skip); owner may accept, veto, change line or skip. Log predictions **before kickoff**, odds snapshot and reason; later score/result, forecast vs outcome, calibration, scoring and owner-veto performance.
9. **Validation:** Use a chronologically split holdout / walk-forward setup to prevent leakage; measure Brier/log-loss, calibration, edge-band stability, decision coverage, EV/ROI with CIs, subgroup performance and differences between model-only versus human-veto outcomes. Beware selective memory, cherry picking, parlays and small-sample swings.

## 4. Case study — Portugal vs Denmark, 14 Nov 2026

Screenshot evidence: FotMob Nations League A Group 4 xG table after four completed matches:
- Portugal: 4 played, 7 xG, 5 xGA, 7 xPTS; actual 12 points (five above xPTS).
- Denmark: 4 played, 5 xG, 5 xGA, 6 xPTS; actual 6 points.
These are **four-match historical totals**, **not predicted xG for this fixture**.

External pre-match price examples observed 2026-11-14, not the owner's bookmaker, subject to change:
- Portugal 1X / double chance: 1.14 (SportyTrader); break-even **87.7193%**.
- Denmark +2.5 AH: 1.21 (bookmakers-rating.top); break-even **82.6446%**.
- Sources: https://www.sportytrader.com/en/odds/portugal-denmark-8318352/ and https://bookmakers-rating.top/matches/fd84a1a8-portugal-vs-denmark/ .
Different sites and updates are not synchronized; verify a same-time, executable quote before any realistic market analysis.

Illustrative independent-Poisson sensitivity test (**not trained forecasts**, deliberately hand-set lambda values):

| Assumed Portugal / Denmark expected goals | P(Portugal 1X) | P(Denmark +2.5) |
|---|---:|---:|
| 1.50 / 1.25 — simple mean of xG attack and opponent xGA over four matches, ignoring home/opponent strength | 68.36% | 91.71% |
| 2.10 / 1.30 — stronger-home attack sensitivity | 76.71% | 83.08% |
| 2.50 / 1.00 — strong-Portugal sensitivity | 86.87% | 72.02% |

**Takeaway:** A high-cushion handicap may survive many scorelines, but estimated value flips when reasonable unvalidated assumptions change. At quoted prices, the crude Poisson baseline *appears* to favor Denmark +2.5, while stronger-home scenario does not. These outputs cannot justify an actionable edge. The 1X market's low payout requires very high success probability. A model that ignores home, injury, opponent and group context is not reliable enough for selection.

## 5. Example owner-facing report

```text
Portugal vs Denmark | paper case, 14 Nov 2026
Data: 4 matches only; provenance and recency require review
Candidate 1: Portugal 1X | quoted odds 1.14 | breakeven 87.72%
Candidate 2: Denmark +2.5 | quoted odds 1.21 | breakeven 82.64%
Model: illustrative scenario table only, not validated
Uncertainty: HIGH — output changes across reasonable assumptions
Recommendation: NO VERIFIED EDGE / PAPER TEST ONLY
Owner choice: accept hypothesis / veto / skip (not entered)
```

## 6. Windows / GitHub walkthrough (documentation only)

1. On the Windows computer, open VS Code and open the **existing local XGBOT repository**. If not cloned yet, in VS Code Terminal / PowerShell run `git clone https://github.com/Sayrsoe/XGBOT.git`, then `cd XGBOT`.
2. Run `git fetch origin` to obtain the documentation branch. This does not edit main.
3. Review without losing local uncommitted changes: first run `git status`. If clean, `git switch --track origin/docs/xgbot-2.3.3-edge-analysis-draft` (or `git switch docs/xgbot-2.3.3-edge-analysis-draft` if already configured).
4. Open `tasks/2.3.3/final/EDGE_ANALYSIS_BLUEPRINT_DRAFT.md` and `XGBOT2.3.3handover.md`; edit proposals only in an independently approved future task.
5. To return to the stable branch, run `git switch main`. Do not merge or deploy by reading the draft.

If the branch is not found, do not guess a replacement; verify it on GitHub and refresh. GitHub branches are remote; saving documentation there does **not** automatically copy it onto the Windows laptop.

## 7. Decisions that remain unapproved

- Whether to promote this planning draft into the XG-2B design requirements.
- Source-rights/provider choice for Opta/FotMob, authorized historical datasets and coverage.
- Feature prioritization, production architecture, model/threshold/validation approach.
- Any new code, numeric migration, external odds collection, PR merge, deployment or betting use.

## 8. Next research task proposal

Conduct read-only Codex architecture and statistical audit of this draft; specifically check the probability math, scoreline-tail truncation, quarter-line settlement, xPTS comparability, bookmaker margin, rights and leakage. Produce numbered evidence and seek separate owner approval before implementation.
