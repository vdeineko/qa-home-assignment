# Strategy & Recommendations

## Tests selected for automation

I selected these tests based on **business risk, critical user journeys, and automation value**.

**1. API Test – Insufficient Balance**

This test verifies a critical financial rule: users must not be able to place bets exceeding their available balance. The specification requires validation at both UI and API levels. Testing the API directly ensures the rule cannot be bypassed through a manipulated request.

API automation is fast, reliable, and provides immediate feedback on a high-impact business risk. The test also exposes a known defect (BUG-02).

**2. UI Test – Successful Bet Placement**

Bet placement is the application's primary business functionality. This test covers the complete user journey, from selecting odds and entering a stake to receiving confirmation and verifying the updated balance.

It was selected because it validates integration between the UI and backend, including payout calculation, receipt information, and state management. These interactions cannot be fully verified through API tests alone.

## What Was Left for Manual Testing

I prioritized automation of critical business functionality and left lower-risk or more exploratory scenarios for manual testing:

- **Visual and UX testing:** Layout, responsiveness, modal appearance, and clarity of error messages are better evaluated through human observation.
- **Error recovery UX:** Rebet, modal dismissal, and user experience during failures require exploratory testing, particularly when simulating unexpected backend behavior.

These scenarios are not permanently excluded from automation. Their priority should be reconsidered as the application grows and could be automated in future

## Recommendations for Scaling

**1. Integrate Automated Tests into CI/CD**

Run API tests on every pull request and maintain a UI smoke suite for deployments. Execute the broader regression suite regularly. Known defects should remain visible through `xfail` markers and be converted into regular assertions once fixed.

**2. Improve Test Data Management**

All runs share one account whose reset is wrong (BUG-06), so runs can't be parallel or repeatable.Introduce isolated test users, predictable match fixtures, and reliable balance reset mechanisms.
Expand API automation using parameterized tests for stake boundaries (€1/€100), decimal precision, invalid selections, authentication 

**2. Expand API Coverage**

Introduce automated API contract testing based on the OpenAPI specification. A significant proportion of identified defects (BUG-02, BUG-03, BUG-04, BUG-07, BUG-09, and BUG-10) involve API contract violations. Automatically validating response schemas, HTTP status codes, required fields, and error responses against the OpenAPI definition would help detect these regressions early and reduce the need for repetitive manual verification.
Expand API automation with parameterized tests covering stake boundaries (€1/€100), decimal precision, invalid selections, authentication.

**3. Clarify the Specification and API Contracts**

Resolve inconsistencies in the specification, particularly the minimum stake (€1.00 in business rules versus €1.01 in validation rules). Define expected behavior for retries, duplicate submissions, balance consistency, and error responses.

Clearer contracts will reduce ambiguity in test expectations and make automation more maintainable.

### Summary

My approach is to automate **high-risk business rules at the API layer and critical user journeys at the UI layer**, while keeping exploratory and visual testing manual initially. As the project scales, the priority should be reliable test data, fast CI feedback, and broader API-level regression coverage.