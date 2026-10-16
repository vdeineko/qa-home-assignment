# Execution Results & Bug Reports — Single Bet Placement

**Environment:** https://qae-assignment-tau.vercel.app/, 
**Data:** screenshots are in `evidence/`

## 1. Execution results (top 3 scenarios)

| ID | Scenario | Result | Notes |
|----|----------|--------|-------|
| TC-01 | Place a valid single bet | **Fail** | Bet is placed and charged correctly (API 120 → 115), but the header balance is not updated (BUG-08), and the bet was accepted on a match marked PAST (BUG-03). |
| TC-02 | Receipt matches selection | **Fail** | Payout shown is wrong (BUG-01), and home/away are swapped (BUG-05). Stake, odds, bet ID and timestamp are correct. Reproduced on 3 matches. |
| TC-03 | Reset balance consistency | **Fail** | Reset response says €125.50; the saved balance is €120.00 (BUG-06). |

**Exploratory checks** (around the bet placement flow):

| Area | Result |
|------|--------|
| UI stake input: `0.5`, `1`, `100`, `100.01`, `10.123`, `abc`, `-5`, `1e2`, empty | Pass — correct min/max messages, Place Bet disabled when invalid, input limited to 2 decimals, letters/sign stripped. |
| Selection replacement (other outcome / other match) | Pass — slip keeps one selection. |
| Remove (x) and Remove All | Pass — slip is cleared. |
| Insufficient balance | UI pass; **API fail** (BUG-02). |
| Double-click Place Bet | **Fail** — intermittent duplicate bet (BUG-04). |
| API validation (422 cases) and 401 auth | Pass. |
| API protocol (405, 400, 409) | **Fail** — BUG-09, BUG-10; 409 only partly enforced (see BUG-04). |
| Error modal / Rebet | Not executed — the error state could not be triggered without fault injection. |

## 2. Bug summary

| ID | Title | Severity | Layer |
|----|-------|----------|-------|
| BUG-01 | Receipt payout is stake × 2 instead of stake × odds | Critical | UI |
| BUG-02 | API accepts a stake above the balance (balance goes negative) | Critical | API |
| BUG-03 | Past matches are listed and can be bet on | Critical | UI + API |
| BUG-04 | Double-clicking Place Bet can place the bet twice | High | UI + API |
| BUG-05 | Receipt lists the away team first | High | UI |
| BUG-06 | Reset balance response differs from the saved balance | High | API |
| BUG-07 | place-bet response returns currency "USD" | High | API |
| BUG-08 | Header balance is not updated after a bet | Medium | UI |
| BUG-09 | Malformed JSON returns 500 instead of 400 | Medium | API |
| BUG-10 | GET on place-bet returns 200 instead of 405 | Medium | API |
| BUG-11 | Bet slip hides the available balance while a selection is active | Low | UI |
| BUG-12 | Spec contradiction: minimum stake €1.00 vs €1.01 | Low | Spec |

---

## 3. Bug reports

### BUG-01 — Receipt payout is stake × 2 instead of stake × odds · **Critical**
**Reproduction**
1. Open the app, click **1** on *Manchester Utd vs Chelsea* (odds 2.45).
2. Enter stake €5.00 — the slip shows potential payout **€12.25**.
3. Click **Place Bet** and read the receipt.

**Expected:** Receipt payout = stake × odds = €12.25 (same as the slip).
**Actual:** Receipt payout = **€10.00**. Every case tried matches stake × 2:

| Match / outcome | Stake | Odds | Slip payout | Receipt payout |
|---|---|---|---|---|
| Man Utd v Chelsea / Home | 5.00 | 2.45 | €12.25 | €10.00 |
| Real Madrid v Barcelona / Draw | 4.00 | 3.40 | €13.60 | €8.00 |
| Bayern v Dortmund / Away | 2.50 | 6.00 | €15.00 | €5.00 |

The API response carries the correct payout (`stake 10 @ 2.45 → payout 24.5`), so
the fault is in the receipt display.

**Business impact:** The customer's record of the bet shows different winnings
from what they agreed to — a direct trust and dispute/compliance problem.
**Evidence:** `evidence/01_bet-slip-before-placement.png` (€12.25) and
`evidence/02_receipt-after-placement.png` (€10.00).

---

### BUG-02 — API accepts a stake above the balance (balance goes negative) · **Critical**
**Reproduction**
1. Place bets until the balance is below €100 (here: €79.50).
2. `POST /api/place-bet` with `{"matchId":"la-liga-real-barca","selection":"HOME","stake":80}`.

**Expected:** Rejected as insufficient balance (spec 4.1, "UI + API"); balance unchanged.
**Actual:** `200 Bet placed successfully`, and the balance becomes **-0.5**.
```
{"message":"Bet placed successfully","matchId":"la-liga-real-barca","selection":"HOME",
 "stake":80,"odds":1.85,"payout":148,"balance":-0.5,"currency":"USD"}
```
The UI blocks this correctly ("Insufficient balance", button disabled), so the
only guard is client-side.

**Business impact:** Anyone calling the API directly (or a buggy client) can bet
money they do not have; the operator carries liability on negative balances.

---

### BUG-03 — Past matches are listed and can be bet on · **Critical**
**Reproduction**
1. Open the app (today: 2026-10-11).
2. The first cards under "Upcoming Football Matches" are tagged **PAST**
   (e.g. *Manchester Utd vs Chelsea*, Fri Feb 27).
3. Click any odds on a PAST match, enter a stake, and click **Place Bet**.

**Expected:** Only upcoming (pre-match) events are offered (spec 1 and 3); past
events cannot be selected, and the API rejects them.
**Actual:** 83 of the 103 matches returned by `/api/matches` have a `kickoffDate`
before today. Their odds stay clickable, and bets on them succeed (all of TC-01's
bets were on the 2026-02-27 match).

**Business impact:** Betting on events whose result is already known is an
exploitable money loss for the operator and a regulatory breach.
**Evidence:** "PAST" tags with a live selection in
`evidence/01_bet-slip-before-placement.png`.

---

### BUG-04 — Double-clicking Place Bet can place the bet twice · **High**
**Reproduction**
1. Select *Juventus vs AC Milan* home and enter stake €2.00.
2. Double-click **Place Bet**.
3. Check `GET /api/balance`.

**Expected:** One bet. The button enters the "Placing..." state, and the API
answers a concurrent request with `409 bet already in progress`.
**Actual:** Intermittent. In one of two attempts the balance dropped by **€4.00**
(120 → 116) for one €2 stake. Sending 3 parallel API requests gave `200, 409, 200` —
the in-progress lock catches only some overlapping requests.

**Business impact:** Customers are charged twice for one action, which leads to
refunds, complaints and chargebacks.

---

### BUG-05 — Receipt lists the away team first · **High**
**Reproduction:** Place any bet and read the receipt match line.

**Expected:** "Home vs Away", as in the match list and the API (Match Ordering convention).
**Actual:** Reversed on every match tried:

| API (home / away) | Receipt |
|---|---|
| Manchester Utd / Chelsea | "Chelsea vs Manchester Utd" |
| Real Madrid / Barcelona | "Barcelona vs Real Madrid" |
| Bayern Munich / Dortmund | "Dortmund vs Bayern Munich" |

**Business impact:** On a 1/X/2 market the user cannot tell from the receipt which
side they backed — likely disputes, especially together with BUG-01.
**Evidence:** `evidence/02_receipt-after-placement.png`.

---

### BUG-06 — Reset balance response differs from the saved balance · **High**
**Reproduction**
1. Place a bet (balance 120 → 113).
2. `POST /api/reset-balance`.
3. `GET /api/balance`.

**Expected:** Spec 5.3 — response and saved state agree; both are the initial €125.50.
**Actual:** The response always says `125.5`, but the saved balance is set to **120**.
```
before 120 → bet 7 → 113
reset resp: {"message":"Balance reset successfully","balance":125.5,"currency":"EUR"}
after reset: {"balance":120,"currency":"EUR"}
```
Reset does restore funds, just to the wrong amount, and it reports a value that
was not saved. (Swagger itself notes "response payload may differ from persisted
balance", which contradicts spec 5.3.)

**Business impact:** Clients trusting the response show the wrong balance; the
user is €5.50 short after every reset.

---

### BUG-07 — place-bet response returns currency "USD" · **High**
**Reproduction:** `POST /api/place-bet` with any valid body.

**Expected:** `"currency":"EUR"` (single-currency product; same as `/api/balance`).
**Actual:** `"currency":"USD"`, while `/api/balance` returns `"EUR"`.
```
{"message":"Bet placed successfully",...,"payout":24.5,"balance":113.5,"currency":"USD"}
```
**Business impact:** Clients may format or convert amounts wrongly; inconsistent
financial data across endpoints.

---

### BUG-08 — Header balance is not updated after a bet · **Medium**
**Reproduction**
1. Note the header balance (€120.00).
2. Place a €5 bet and close the receipt.

**Expected:** Header (and bet slip) show €115.00 right away (spec: balance is
shared across header and slip).
**Actual:** Header and slip stay at **€120.00**; the API already says 115. The
correct value appears only after a page reload.

**Business impact:** The user sees money they no longer have and may try bets
that will fail.
**Evidence:** `evidence/03_after-close-header-not-updated.png`.

---

### BUG-09 — Malformed JSON returns 500 instead of 400 · **Medium**
**Reproduction:** `POST /api/place-bet` with body `{bad json`.

**Expected:** `400` malformed payload (spec 4.3, Swagger `invalid_json`).
**Actual:** `500 {"error":"internal_server_error","message":"Unable to process request."}`.
A valid JSON non-object (`"a string"`) is handled correctly with `400 invalid_json`.

**Business impact:** Client errors look like server outages — noisy alerts, and
integrators can't tell what they did wrong.

---

### BUG-10 — GET on place-bet returns 200 instead of 405 · **Medium**
**Reproduction:** `GET /api/place-bet` with a valid `x-user-id`.

**Expected:** `405 method not allowed` (spec 4.3).
**Actual:** `200 {}`.

**Business impact:** A wrongly-wired client gets a "success" status and fails silently.

---

### BUG-11 — Bet slip hides the available balance while a selection is active · **Low**
**Reproduction:** Select any odds and look at the bet slip.

**Expected:** Spec 2.2 — the slip shows stake, **available balance** and potential payout.
**Actual:** "Balance: €x" appears in the slip only while it is empty; with a
selection it shows only stake and payout (the header still shows the balance).

**Business impact:** Minor — the user must look away from the slip to check funds
while choosing a stake.
**Evidence:** compare the slip in `evidence/01_bet-slip-before-placement.png`
(no balance) with `evidence/03_after-close-header-not-updated.png` (balance shown).

---

### BUG-12 — Spec contradiction: minimum stake €1.00 vs €1.01 · **Low (spec)**
**Observation:** Section 3 says the minimum is €1.00; table 4.1 says €1.01.
The UI ("Minimum stake is €1.00") and API (`0.99` → `invalid_stake_min`, `1.00` →
accepted) both use **€1.00**.

**Expected:** One value in the spec.
**Business impact:** Low today, but an ambiguous rule leads to wrong
implementations or tests later. Recommend correcting table 4.1 to €1.00.
