"""
Render an A3 report (problem-solving, proposal, or status variant) to a
formatted markdown file on disk.

Part of the `a3-thinking` skill. This script is the deterministic "save" step:
the *thinking* (working through the sections, root-cause rigor, setting a
measurable target) happens in the conversation per SKILL.md; this script only
validates the agreed content and renders it as a clean A3 document.

Returns {"status": "success", "path": ..., "variant": ...} or
        {"status": "error", "message": ...}.
"""

import sys
import os
import json
import re
from datetime import date as _date


# Ordered (section_key, display heading) for each variant. The order IS the
# canonical A3 "story" order, read top to bottom.
VARIANTS = {
    "problem-solving": [
        ("background", "Background"),
        ("current_condition", "Current Condition"),
        ("goal", "Goal / Target Condition"),
        ("root_cause_analysis", "Root-Cause Analysis"),
        ("countermeasures", "Countermeasures"),
        ("implementation_plan", "Implementation Plan"),
        ("follow_up", "Follow-Up"),
    ],
    "proposal": [
        ("background", "Background"),
        ("current_situation", "Current Situation"),
        ("goal", "Goal / Target"),
        ("analysis", "Analysis"),
        ("proposal", "Proposal"),
        ("implementation_plan", "Implementation Plan"),
        ("expected_results", "Expected Results & Follow-Up"),
    ],
    "status": [
        ("background", "Background"),
        ("current_state", "Current State"),
        ("results", "Results"),
        ("remaining_issues", "Remaining Issues / Next Actions"),
    ],
}


def _slugify(text: str) -> str:
    slug = re.sub(r"[^a-z0-9]+", "-", (text or "").lower()).strip("-")
    return slug or "a3"


def _unique_path(path: str) -> str:
    """Avoid clobbering an existing file by appending -2, -3, ... before .md."""
    if not os.path.exists(path):
        return path
    root, ext = os.path.splitext(path)
    i = 2
    while os.path.exists(f"{root}-{i}{ext}"):
        i += 1
    return f"{root}-{i}{ext}"


def _render(variant: str, title: str, meta: dict, sections: dict) -> str:
    spec = VARIANTS[variant]
    lines = [f"# {title}", ""]

    meta_bits = []
    for key, label in (("owner", "Owner"), ("coach", "Coach/Mentor"), ("date", "Date")):
        val = meta.get(key)
        if val:
            meta_bits.append(f"**{label}:** {val}")
    meta_bits.append(f"**Type:** {variant} A3")
    lines.append(" · ".join(meta_bits))
    lines.append("")

    for n, (skey, heading) in enumerate(spec, start=1):
        lines.append(f"## {n}. {heading}")
        lines.append("")
        lines.append(str(sections.get(skey, "")).strip())
        lines.append("")

    return "\n".join(lines).rstrip() + "\n"


def run(params: dict = None) -> dict:
    """
    Params:
        variant (str): "problem-solving" | "proposal" | "status". Required.
        title (str): The A3 theme/title (a problem statement, not a solution). Required.
        sections (dict): Maps section_key -> markdown content. All sections for the
            chosen variant are required (see VARIANTS for keys).
        owner (str): Optional. Person who owns the A3.
        coach (str): Optional. Mentor/coach for the A3 dialogue.
        date (str): Optional. Defaults to today (YYYY-MM-DD).
        output_path (str): Optional. Full path to write. Defaults to
            ./a3-plans/<slug>-<date>.md. Never overwrites: auto-suffixes on collision.
    """
    params = params or {}

    variant = params.get("variant")
    if variant not in VARIANTS:
        return {"status": "error",
                "message": f"'variant' must be one of {sorted(VARIANTS)} (got {variant!r})"}

    title = (params.get("title") or "").strip()
    if not title:
        return {"status": "error", "message": "'title' is required"}

    sections = params.get("sections") or {}
    if not isinstance(sections, dict):
        return {"status": "error", "message": "'sections' must be an object of section_key -> content"}

    required = [k for k, _ in VARIANTS[variant]]
    missing = [k for k in required if not str(sections.get(k, "")).strip()]
    if missing:
        return {"status": "error",
                "message": f"Missing required sections for {variant} A3: {missing}. "
                           f"Required: {required}"}

    unknown = [k for k in sections if k not in required]

    the_date = params.get("date") or _date.today().isoformat()
    meta = {"owner": params.get("owner"), "coach": params.get("coach"), "date": the_date}

    output_path = params.get("output_path")
    if not output_path:
        output_path = os.path.join("a3-plans", f"{_slugify(title)}-{the_date}.md")
    output_path = os.path.abspath(output_path)
    parent = os.path.dirname(output_path)
    if parent:
        os.makedirs(parent, exist_ok=True)
    output_path = _unique_path(output_path)

    content = _render(variant, title, meta, sections)
    try:
        with open(output_path, "w", encoding="utf-8") as fh:
            fh.write(content)
    except OSError as exc:
        return {"status": "error", "message": f"Could not write file: {exc}"}

    result = {"status": "success", "path": output_path, "variant": variant,
              "sections_written": required}
    if unknown:
        result["warning"] = f"Ignored unknown section keys: {unknown}"
    return result


if __name__ == "__main__":
    p = {}
    if len(sys.argv) > 1:
        try:
            p = json.loads(sys.argv[1])
        except json.JSONDecodeError:
            print(json.dumps({"status": "error", "message": "Could not parse params as JSON"}))
            sys.exit(1)
    print(json.dumps(run(p), indent=2, default=str))
