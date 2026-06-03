# A3 Guide — sections, techniques, and when to use each variant

Reference for the `a3-thinking` skill. Load this when you need depth on a section
or on which variant to use. Grounded in primary A3 sources (Sobek & Smalley;
Shook/Lean Enterprise Institute; MIT Sloan).

## The discipline behind every A3

- **One page, told as a story**, read top to bottom (on paper, left = current
  state, right = future state). The constraint is the feature: it forces you to
  separate signal from noise.
- **A3 thinking > the template.** "Internalizing that thinking is the objective,
  not technical mastery of the format" (John Shook). A neat template over weak
  analysis is worthless — *garbage in, garbage out*.
- **It embeds PDCA.** Most of the work lives in **Plan** (understanding the
  problem and its cause). Rushing to countermeasures is the #1 failure.
- **It's a dialogue.** The A3 is a coaching/alignment tool — the author owns it, a
  coach asks questions rather than gives answers. Work it *with* the people who
  have the facts, not solo at a desk.

---

## Variant 1 — Problem-Solving A3

Use when a problem is **real, important, tied to a goal, and its root cause is not
yet understood**. Seven sections:

### 1. Background
Why should anyone care? Context needed to understand the problem and **how it
relates to business goals/values**. How the problem surfaced, who's affected,
past performance. Anchor to strategy.

### 2. Current Condition
A **fact-based** picture of how the process works *today*. Prefer a diagram
(swimlane/flow) with problems marked. Demand observation at the *gemba* (the
actual place), not assumptions. **Quantify the gap** — its size and trend.
*This is usually the most important section.* If the current state is vague, stop
and get data before going further.

### 3. Goal / Target Condition
A short statement of the **desired, measurable outcome** with a **deadline**. Set
it from observed data and current capacity. Make it SMART. The gap between
Current Condition and Goal is what the A3 is trying to close.

### 4. Root-Cause Analysis
Trace the problem to its **true source** before proposing fixes. Tools:
- **5-Why** — ask "why?" iteratively down a causal chain until you hit a cause you
  can act on (not a symptom). Verify each step by observation, not guesswork.
- **Fishbone / Ishikawa** — categorize candidate causes (Method, Machine,
  Material, Man, Measurement, Environment) to widen the search before narrowing.
- **Fault Tree** — for complex multi-cause failures.
Causes must be **verified**, not assumed. This is where coaching adds the most.

### 5. Countermeasures
Designed changes that **eliminate the root cause** — changes to the
process/system, not band-aids. Split into:
- **Short-term** — stabilize now.
- **Long-term** — prevent recurrence.
Each countermeasure must **trace to a specific root cause** from §4. If it doesn't
map to a cause, cut it.

### 6. Implementation Plan
How the countermeasures get done: **Who / What / When** — owner + due date per
task (a small table or simple Gantt). Concrete and assignable.

### 7. Follow-Up
How you'll **confirm it worked**: track actual results vs. the target (a run
chart, an audit cadence — what's checked, when, by whom). If the target is met,
**standardize** (update the SOP/standard work) and **share the learning**
(*yokoten*). If not, **return to root-cause analysis** — re-enter PDCA.

---

## Variant 2 — Proposal A3

Use when **pitching a new initiative or investment** — a forward-looking business
case that replaces a slide deck. There may be no existing "problem with a root
cause"; the work is articulating an opportunity, the cost of inaction, and a
recommended course. Seven sections:

### 1. Background
The theme and context. What opportunity/need prompts this, and how it ties to
organizational goals.

### 2. Current Situation
Where things stand now and **the cost of doing nothing**. Facts and data that
establish the gap or opportunity size.

### 3. Goal / Target
The measurable outcome the proposal aims for, with a timeframe.

### 4. Analysis
The options considered and the reasoning/criteria. Why the recommended option
beats the alternatives (and the do-nothing baseline).

### 5. Proposal
The **recommended countermeasure / course of action**, stated clearly, with its
rationale and expected mechanism.

### 6. Implementation Plan
Who / What / When, plus **cost and resources** required. The concrete path to
execute the proposal.

### 7. Expected Results & Follow-Up
The benefits expected (quantified where possible), risks/unresolved issues, and
how results will be verified after rollout.

---

## Variant 3 — Status A3

Use to **report progress** on an ongoing effort. Four sections (it shares the A3
flow but each section's nature is "where are we", not "what should we do"):

### 1. Background
Context and the objective of the work being reported on.

### 2. Current State
What's been done so far — plan vs. actual.

### 3. Results
Progress against targets/KPIs (charts/numbers vs. the goal).

### 4. Remaining Issues / Next Actions
What's left, current blockers, and the next steps with owners.

---

## When NOT to use an A3

- The problem is **trivial** — just fix it.
- **Speed is paramount and the cause is already known** — don't ritualize.
- The underlying problem-solving rigor is weak — an A3 won't rescue bad analysis.
- "Make the tool fit the problem, not the other way round."

## Common pitfalls (call these out while coaching)

- **Form over content** — obsessing over layout instead of substance.
- **Information overload** — cramming the page; defeats the one-page purpose.
- **Working solo** — losing the dialogue/alignment value (ideal team 2–5).
- **Jumping to solutions** — skipping current-state facts and root cause.
- **No measurable target / no date.**
- **Countermeasures untraceable to a root cause.**

## Sources

- [Toyota's Secret: The A3 Report — MIT Sloan Management Review](https://sloanreview.mit.edu/article/toyotas-secret-the-a3-report/)
- [Discovering the True Value of the A3 Process (John Shook) — Lean Enterprise Institute](https://www.lean.org/the-lean-post/articles/the-a3-process-discovery-at-toyota-and-what-it-can-do-for-you/)
- [The A3 Report — Sobek, Montana State University](https://www.montana.edu/dsobek/a3/report.html)
- [What are A3 status reports? — Mark Dalgarno](https://markdalgarno.medium.com/what-are-a3-status-reports-63558e3f6e05)
- [A3 problem solving — Wikipedia](https://en.wikipedia.org/wiki/A3_problem_solving)
- [Understanding A3 Thinking (Sobek & Smalley) — getAbstract summary](https://www.getabstract.com/en/summary/understanding-a3-thinking/40569)
- See also the fuller write-up in this repo: `.ai-docs/research/a3-thinking.md`
