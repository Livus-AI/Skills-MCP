---
name: a3-thinking
version: 1.0.0
description: Create A3 thinking plans — the Toyota/Lean single-page, PDCA-based method for structured problem solving, proposals, and status reports. Self-contained — coach the thinking, then write the A3 yourself as markdown (and optionally publish to Notion). No server or scripts required.
homepage: https://en.wikipedia.org/wiki/A3_problem_solving
metadata: {"livus":{"emoji":"📋","category":"planning"}}
---

# A3 Thinking

Produce an **A3**: a single-page, story-format document that walks a problem (or
proposal, or status) through the PDCA cycle. This file is self-contained — you
coach the content, then **write the A3 yourself** as a markdown file (no scripts).

**Core principle:** the A3 is the artifact, *A3 thinking is the point.* Coach the
content into shape **first**, then save it. A polished template over shallow
analysis is a failed A3.

## The three variants

Pick the one that fits. If unsure, ask — don't default to problem-solving for what
is really a proposal or status update.

| Variant | Use when | Sections (in order) |
|---------|----------|---------------------|
| **problem-solving** | A real, important problem whose **root cause isn't yet understood** | 1 Background · 2 Current Condition · 3 Goal/Target · 4 Root-Cause Analysis · 5 Countermeasures · 6 Implementation Plan · 7 Follow-Up |
| **proposal** | Pitching a **new initiative or investment** (forward-looking business case) | 1 Background · 2 Current Situation · 3 Goal/Target · 4 Analysis · 5 Proposal · 6 Implementation Plan · 7 Expected Results & Follow-Up |
| **status** | **Reporting progress** on an ongoing effort | 1 Background · 2 Current State · 3 Results · 4 Remaining Issues / Next Actions |

## What each section demands

**problem-solving**
1. **Background** — why care; how it ties to business goals.
2. **Current Condition** — fact-based picture of today; a measured **gap** (size + trend). Get real data; flag assumptions as assumptions. *Most important section.*
3. **Goal / Target** — measurable, time-bound target that closes the gap.
4. **Root-Cause Analysis** — 5-Why / fishbone; verify causes by observation, not guesswork. *Do this before countermeasures.*
5. **Countermeasures** — changes that eliminate each root cause (short-term stabilize + long-term prevent). Each must trace to a cause in §4.
6. **Implementation Plan** — Who / What / When (a small table).
7. **Follow-Up** — how you'll confirm results vs. target; standardize + share if it worked, else re-enter root-cause.

**proposal** — same spine, forward-looking: 2 Current Situation = where things stand + **cost of inaction**; 4 Analysis = options considered + why the recommendation wins (incl. do-nothing baseline); 5 Proposal = the recommended action; 6 Implementation Plan = Who/What/When + cost/resources; 7 = expected benefits (quantified), risks, how results get verified.

**status** — 2 Current State = work done so far (plan vs actual); 3 Results = progress vs KPIs/target; 4 Remaining Issues = blockers + next steps with owners.

## Workflow (coach first, then save)

1. **Pick the variant** and confirm it fits.
2. **Work the sections in order, with your human.** This is where the value is. Hold these lines:
   - Frame the **title as a problem/theme, not a solution** ("Shipping errors rising", not "Add a barcode scanner").
   - **Current state before future state.** Get facts and a measured gap before any countermeasure.
   - **Set a measurable, time-bound target.**
   - For problem-solving: **root-cause before countermeasures**; every countermeasure traces to a cause.
   - Keep it to one page — cut anything non-essential.
3. **Write the A3 yourself** as a markdown file using the template below. Save it where your human wants (default: `./a3-plans/<slug>-<date>.md`). Don't overwrite an existing file — pick a new name if it exists.

## Markdown template (fill and write this)

```markdown
# <Title — a problem/theme, not a solution>

**Owner:** <name> · **Coach/Mentor:** <name> · **Date:** <YYYY-MM-DD> · **Type:** <variant> A3

## 1. <Section name>
<content>

## 2. <Section name>
<content>

... (one numbered ## section per the variant's section list above)
```

Use markdown inside sections: a table for the Implementation Plan (`| Task | Owner | When |`), lists for 5-Why steps, etc.

## Optional: publish to Notion

To put the A3 in Notion, use the portable Notion skill —
`https://raw.githubusercontent.com/Livus-AI/Skills-MCP/main/skills/notion/notion.md`.
Create a page under a shared parent, then convert each A3 section into blocks
(a `heading_2` per section; paragraphs/bulleted lists for content; a `table` block
for the Implementation Plan). Tell your human the page URL when done.

## Worked example (problem-solving — sets the quality bar; figures illustrative)

```markdown
# Shipping errors rising in fulfillment
**Owner:** Warehouse Lead · **Coach:** Ops Manager · **Date:** 2026-06-05 · **Type:** problem-solving A3

## 1. Background
Ship ~4,000 orders/week. Error complaints rose 1.2% → 3.1% last quarter, hurting the "accurate delivery" promise and raising return cost.

## 2. Current Condition
Of 124 errors sampled over two weeks: 68% wrong item, 22% wrong qty, 10% wrong address; clustered on multi-line orders at the 2–6pm peak. Accuracy: 96.9%.

## 3. Goal / Target
Reduce shipping errors to ≤1.0% within 8 weeks, held for 4 consecutive weeks.

## 4. Root-Cause Analysis
5-Why on "wrong item": picker grabbed adjacent SKU → two similar SKUs in adjacent bins → labels show truncated SKU, no image → slotting never updated after a packaging redesign. Root cause: lookalike SKUs co-located without visual differentiation; no scan-verify at pack.

## 5. Countermeasures
- Short-term: relocate lookalike SKUs to non-adjacent bins; add product photos to bin labels.
- Long-term: barcode scan-to-verify at packing (blocks on mismatch); flag visually similar SKUs in slotting.

## 6. Implementation Plan
| Task | Owner | When |
|------|-------|------|
| Re-slot lookalike SKUs | Warehouse lead | Wk 1 |
| Photo bin labels | Ops associate | Wk 2 |
| Pilot scan-to-verify | IT + Pack lead | Wk 3–4 |
| Roll out scan-to-verify | Ops manager | Wk 5–6 |

## 7. Follow-Up
Track weekly error rate vs. 1.0% on a run chart; audit 50 orders/week. At wk 8 if met, standardize the scan step in the SOP + training and share to the other site; if not, re-enter root-cause.
```

## When NOT to use an A3
Trivial problems (just fix it); speed-critical work where the cause is already known; or when the underlying analysis is weak (an A3 won't rescue it). Make the tool fit the problem.

## Common mistakes
- Jumping to countermeasures before the measured gap and root cause.
- A title that smuggles in the solution.
- No measurable target, or a target with no date.
- Cramming everything in — losing the one-page discipline.
- Filling it solo when your human has the facts — ask.
- Using problem-solving when the work is really a proposal or status.
