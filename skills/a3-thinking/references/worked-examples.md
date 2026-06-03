# A3 Worked Examples

One filled example per variant for the `a3-thinking` skill. Figures are
illustrative — they demonstrate structure and the *level of rigor* expected, not
real data. Use them as a quality bar when coaching the real content.

---

## Example A — Problem-Solving A3

**Title:** Shipping errors rising in fulfillment
**Owner:** Warehouse Lead · **Coach:** Ops Manager

### 1. Background
The fulfillment center ships ~4,000 orders/week. Shipping-error complaints rose
from 1.2% to 3.1% of orders last quarter, threatening the "on-time, accurate
delivery" promise and driving up return cost and CSAT decline.

### 2. Current Condition
Swimlane: pick → pack → label → ship. Of 124 errors sampled at the gemba over two
weeks: 68% wrong item, 22% wrong quantity, 10% wrong address. Errors cluster on
multi-line orders during the 2–6 p.m. peak. Current accuracy: **96.9%**.

### 3. Goal / Target Condition
Reduce shipping errors to **≤1.0% of orders within 8 weeks**, held for four
consecutive weeks.

### 4. Root-Cause Analysis
5-Why on "wrong item": picker grabbed adjacent SKU → two similar SKUs in adjacent
bins with near-identical labels → bin labels show truncated SKU, no image →
slotting never updated after a packaging redesign. **Root cause:** lookalike SKUs
co-located without visual differentiation, plus no scan-verification at pack.

### 5. Countermeasures
- *Short-term:* relocate the two lookalike SKUs to non-adjacent bins; add product
  photos to bin labels.
- *Long-term:* add barcode **scan-to-verify** at packing that blocks confirmation
  on mismatch; update slotting rules to flag visually similar SKUs.

### 6. Implementation Plan
| Task | Owner | Due |
|------|-------|-----|
| Re-slot lookalike SKUs | Warehouse lead | Wk 1 |
| Add photo bin labels | Ops associate | Wk 2 |
| Pilot scan-to-verify (1 line) | IT + Pack lead | Wk 3–4 |
| Roll out scan-to-verify (all lines) | Ops manager | Wk 5–6 |

### 7. Follow-Up
Track weekly error rate vs. 1.0% on a run chart; Quality lead audits 50
orders/week. At wk 8, if met, **standardize** the scan step in the SOP and
training, then **yokoten** to the second center. If not met, re-enter root-cause.

---

## Example B — Proposal A3

**Title:** Adopt automated regression testing for the checkout service
**Owner:** Eng Lead · **Coach:** Director of Engineering

### 1. Background
Checkout is our highest-revenue path. Releases are gated by manual QA; we ship
twice a week and want daily. Reliability of checkout ties directly to revenue.

### 2. Current Situation
Manual regression takes ~6 engineer-hours per release. Two checkout incidents last
quarter reached production (est. cost ~$40k). Cost of inaction: continued slow
releases and recurring escaped defects as the service grows.

### 3. Goal / Target
Cut release regression time to **<30 min automated** and catch ≥90% of checkout
regressions pre-merge, within one quarter.

### 4. Analysis
Options: (a) status quo, (b) hire more manual QA, (c) build automated E2E
regression. (b) scales cost linearly and doesn't speed releases; (c) has upfront
build cost but compounding returns. Selection criteria: release speed, escaped-
defect rate, cost at 2× volume — (c) wins on all three.

### 5. Proposal
Build an automated E2E regression suite for checkout (happy paths + top 10 failure
modes) wired into CI as a merge gate, with a nightly full run.

### 6. Implementation Plan
| Task | Owner | When | Cost |
|------|-------|------|------|
| Framework + CI wiring | Platform eng | Wk 1–2 | 1 eng |
| Author top-20 scenarios | Checkout team | Wk 2–5 | 2 eng |
| Gate merges on suite | Eng lead | Wk 6 | — |

### 7. Expected Results & Follow-Up
Expect regression time 6h → <30min and escaped checkout defects ↓ ≥80%. Risk:
flaky tests eroding trust — mitigate with a quarantine policy. Review escaped-
defect rate and suite runtime monthly.

---

## Example C — Status A3

**Title:** Checkout regression automation — status, week 4
**Owner:** Eng Lead

### 1. Background
Reporting progress on the approved initiative to automate checkout regression
(target: <30 min automated, ≥90% regressions caught pre-merge by end of quarter).

### 2. Current State
Framework and CI wiring complete (wk 1–2, on plan). 12 of 20 target scenarios
authored (plan: 14 by now — slightly behind). Merge-gating not yet enabled.

### 3. Results
Suite runtime: 22 min (target <30 ✓). On the 12 live scenarios, caught 3 of 3
seeded regressions in dry-run. Manual regression still the official gate.

### 4. Remaining Issues / Next Actions
- 8 scenarios left; two blocked on a test-data fixture (owner: Platform, due wk 5).
- Flaky payment-sandbox test under investigation.
- Enable merge gate once all 20 scenarios are green for 3 consecutive nightly runs
  (owner: Eng Lead, target wk 6).
