---
name: a3-thinking
description: Create A3 thinking plans — the Toyota/Lean single-page, PDCA-based method for structured problem solving, proposals, and status reports. Use when the user wants to work through a problem rigorously, plan/pitch an initiative, or report progress as an A3, or mentions "A3", "A3 thinking", root-cause analysis, or a one-page structured plan. Coaches the thinking section by section, then saves a formatted markdown A3.
license: MIT
metadata:
  author: Livus
  version: "1.0"
---

# A3 Thinking

Produce an **A3**: a single-page, story-format document that walks a problem (or
proposal, or status) through the PDCA cycle. The artifact is markdown; the value
is the **thinking** — disciplined, fact-based reasoning that resists jumping to
solutions.

**Core principle:** the A3 is the artifact, *A3 thinking is the point.* Your job
is to coach the content into shape first, then save it. A polished template over
shallow analysis is a failed A3.

## The three variants

| Variant | Use when | Sections |
|---------|----------|----------|
| `problem-solving` | A real, important problem whose **root cause isn't yet understood** | Background · Current Condition · Goal · Root-Cause Analysis · Countermeasures · Implementation Plan · Follow-Up |
| `proposal` | Pitching a **new initiative or investment** (forward-looking business case) | Background · Current Situation · Goal · Analysis · Proposal · Implementation Plan · Expected Results & Follow-Up |
| `status` | **Reporting progress** on an ongoing effort | Background · Current State · Results · Remaining Issues / Next Actions |

If unsure which variant fits, ask. Don't default to `problem-solving` for work
that is actually a proposal or a status update.

Full section-by-section guidance, root-cause techniques, and when-NOT-to-use are
in `references/a3-guide.md`. Filled examples per variant are in
`references/worked-examples.md`. Load them with `get_skill_resource` when you need
depth.

## Workflow (coach first, then save)

1. **Pick the variant** and confirm it fits.
2. **Work the sections in order, with the user.** This is the coaching step — the
   bulk of the value. Hold these lines:
   - Frame the **title as a problem/theme, not a solution** ("Shipping errors
     rising", not "Add barcode scanner").
   - **Current state before future state.** Get facts and a *measured gap* before
     any countermeasure. Ask for real data; flag assumptions as assumptions.
   - **Set a measurable, time-bound target** (Goal section).
   - For `problem-solving`: **do root-cause analysis before countermeasures**
     (5-Why / fishbone). Each countermeasure must trace to a root cause.
   - Keep it tight — an A3 is one page. Cut anything non-essential.
3. **Save** once the content is agreed:

```
execute_skill_script("a3-thinking", "save_a3.py", {
  "variant": "problem-solving",
  "title": "Shipping errors rising in fulfillment",
  "owner": "Jane", "coach": "Lee",
  "sections": {
    "background": "…", "current_condition": "…", "goal": "…",
    "root_cause_analysis": "…", "countermeasures": "…",
    "implementation_plan": "…", "follow_up": "…"
  },
  "output_path": "/abs/path/a3-plans/shipping-errors.md"   // optional
})
```

- Every section for the variant is **required** — the script errors listing any
  missing. That's intentional: an A3 with an empty Root-Cause section isn't done.
- `output_path` is optional; default is `./a3-plans/<slug>-<date>.md`. The script
  never overwrites (auto-suffixes on collision). Prefer passing an absolute
  `output_path` so the file lands where the user expects.
- Use markdown inside section content (tables for the implementation plan, lists
  for 5-Why steps, etc.).

## Reporting back

After saving, tell the user the **path** and give a one-line recap of the A3's
target and key countermeasures/next actions. Only claim what the script returned.

## Common mistakes

- Jumping to countermeasures before establishing the measured gap and root cause.
- A title that smuggles in the solution.
- No measurable target, or a target with no date.
- Cramming everything in — losing the one-page discipline.
- Filling the template solo when the user has the facts — ask.
- Using `problem-solving` when the work is really a `proposal` or `status`.
