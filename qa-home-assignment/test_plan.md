# Test Plan — Single Bet Placement

**Feature:** Single Bet Placement
**Application:** https://qae-assignment-tau.vercel.app/
**Scope:** Pre-match single bets, football only (per Feature Specification).

## Approach & prioritisation

This is a money-handling flow, so scenarios are prioritised by **financial and
trust risk** rather than feature breadth. The highest risk sits where the user
commits money and where the figures shown must match reality: placing the bet,
the receipt, balance accounting, and stake validation. Filters and cosmetic UI
rank lower because an error there does not directly cost the user money.

Priorities: **Critical** (money / core journey) · **High** (a money rule could be
bypassed) · **Medium** (validation & protocol correctness) · **Low** (cosmetic).

The top 3 (TC-01 to TC-03) were executed, results are in `bug_reports.md`.

---

### TC-01 — Place a valid single bet (happy path) · **Critical**
**Risk rationale:** The core revenue journey. If a user cannot place a bet, or the
balance is not charged correctly, the product fails at its primary purpose.

**Steps**
1. Open the app with a valid `user-id` and note the balance (spec: starts at €125.50).
2. Click the **1** (home) odds on *Manchester Utd vs Chelsea* (odds 2.45).
3. Enter a stake of **€5.00**.
4. Click **Place Bet**.
5. Close the receipt.

**Expected result**
- The bet slip shows one selection, stake €5.00 and potential payout €12.25.
- The button shows **Placing...** and then resolves to a success receipt with a bet ID.
- The balance drops by exactly €5.00 in the header and the slip.
- After closing the receipt there is no active selection.

---

### TC-02 — Receipt matches what the user selected · **Critical**
**Risk rationale:** The receipt is the user's record of the wager. If payout,
odds, teams or stake differ from what was shown before placement, the customer
was shown one contract and given another - a dispute and compliance risk.

**Steps**
1. Place a bet where `stake × odds` is not a round number (e.g. €5.00 at 2.45).
2. Compare each receipt field with the bet slip just before placement and with
   `GET /api/matches`.
3. Repeat on a second match and a different outcome (e.g. Draw).

**Expected result**
- Receipt payout = bet-slip payout = `stake × odds`.
- Receipt odds = odds at selection, receipt stake = entered stake.
- Match line lists the **home team first** ("Manchester Utd vs Chelsea").
- Receipt shows a bet ID and a placement timestamp.

---

### TC-03 — Reset balance restores funds consistently · **Critical**
**Risk rationale:** Spec 5.3 requires the reset response and the persisted balance
to agree. If they differ, balance accounting cannot be trusted, and every
test that relies on a known starting balance is unreliable.

**Steps**
1. Place one or more bets so the balance is below its initial value.
2. `POST /api/reset-balance` and note `balance` in the response.
3. `GET /api/balance`, then reload the UI.

**Expected result**
- The reset response returns the initial balance (€125.50) in EUR.
- `GET /api/balance` and the UI header show the **same** value as the response.

---

### TC-04 — Stake above available balance is rejected · **High**
**Risk rationale:** A user must never stake more than they hold. If either layer
allows it, balances can go negative — the business takes on liability with no
funds behind it.

**Steps**
1. The per-bet maximum (€100) is below the starting balance, so first bring the
   balance under €100 (place bets until it is, e.g., €79.50).
2. In the UI, enter a stake €1 above the remaining balance.
3. Send the same stake directly with `POST /api/place-bet`.

**Expected result**
- UI shows "Insufficient balance" and **Place Bet** is disabled.
- API rejects the request; the balance is unchanged and never negative.

---

### TC-05 — Stake validation boundaries · **Medium**
**Risk rationale:** Boundaries and types are classic defect hot-spots around a
money input; the spec requires both UI and API to enforce them.

**Steps**
1. Via API, place bets with stakes `0.99`, `1.00`, `100.00`, `100.01`, `10.123`, `"abc"`,
   and with selection `"WIN"` and an unknown `matchId`.
2. In the UI, type the same values into the stake field.

**Expected result**
- API: `1.00` and `100.00` accepted; otherwise `422` with `invalid_stake_min`,
  `invalid_stake_max`, `invalid_stake_precision`, `invalid_stake_type`,
  `invalid_selection`, `invalid_match` respectively.
- UI: shows "Minimum stake is €1.00" / "Maximum stake is €100.00" and disables
  **Place Bet**; rejects non-numeric input and more than 2 decimal places.
- *Spec note:* section 3 says the minimum is €1.00 and table 4.1 says €1.01 (logged
  as BUG-12). Tested against €1.00, which matches the UI copy.

---

### TC-06 — API protocol and authentication · **Medium**
**Risk rationale:** Wrong status codes hide real failures from clients and
monitoring; auth must reject requests without a user context.

**Steps**
1. Call `/api/balance` and `/api/place-bet` with no `x-user-id` and with an invalid one.
2. `GET /api/place-bet` (POST-only endpoint).
3. `POST /api/place-bet` with malformed JSON (`{bad json`) and with a non-object
   body (`"a string"`).
4. Send two `place-bet` requests for the same user at the same time.

**Expected result**
- Missing / invalid id → `401` (`missing_user_id` / `invalid_user_id`).
- Wrong method → `405`.
- Malformed or non-object body → `400`, never `500`.
- Concurrent request → `409` for the second one; only one bet is placed.

---

## Out of scope (per spec)
Live betting, accumulators, other sports, mobile-specific UX.

## Summary

| ID | Title | Priority | Layer | Executed |
|----|-------|----------|-------|----------|
| TC-01 | Place a valid single bet | Critical | UI + API | Yes — Fail |
| TC-02 | Receipt matches selection | Critical | UI | Yes — Fail |
| TC-03 | Reset balance consistency | Critical | API + UI | Yes — Fail |
| TC-04 | Stake above balance rejected | High | UI + API | Exploratory — Fail (API) |
| TC-05 | Stake validation boundaries | Medium | API + UI | Exploratory — Pass |
| TC-06 | API protocol & auth | Medium | API | Exploratory — Fail |
