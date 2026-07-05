"""
Primary Agent — Discovery Mapper (Orchestrator).

Coordinates the full 4-agent pipeline:
  1. Subagent A (Outcome Tracker)     — extracts the business outcome
  2. Subagent B (Pain Point Synthesizer) — finds customer opportunity branches
  3. Subagent C (Experiment Ideator)  — generates hypotheses per branch
  4. Assembles the final D3-compatible tree_data.json

Run this script directly to generate the OST:
    python agents/orchestrator.py
"""

import json
import os
import sys
from datetime import datetime, timezone

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.file_parser import parse_file, parse_directory
import agents.outcome_tracker as outcome_tracker
import agents.pain_point_synthesizer as pain_point_synthesizer
import agents.experiment_ideator as experiment_ideator

# ── Paths ──────────────────────────────────────────────────────────────────────

INPUTS_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "inputs")
OKR_FILE = os.path.join(INPUTS_DIR, "okr.md")
INTERVIEWS_DIR = os.path.join(INPUTS_DIR, "interviews")
CONTEXT_DIR = os.path.join(INPUTS_DIR, "context")
OUTPUT_FILE = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "docs", "tree_data.json")


def load_inputs() -> tuple[str, str, str]:
    """
    Load all input text from files or environment variables (for workflow_dispatch).

    Environment variables take priority (set by GitHub Actions when using web form):
        INPUT_OKR_TEXT
        INPUT_INTERVIEW_TEXT
        INPUT_CONTEXT_TEXT

    Returns:
        Tuple of (okr_text, interview_text, context_text)
    """
    # Check for env var inputs (from web form via workflow_dispatch)
    okr_text = os.environ.get("INPUT_OKR_TEXT", "").strip()
    interview_text = os.environ.get("INPUT_INTERVIEW_TEXT", "").strip()
    context_text = os.environ.get("INPUT_CONTEXT_TEXT", "").strip()

    # Fall back to files if env vars are empty
    if not okr_text:
        if not os.path.exists(OKR_FILE):
            raise FileNotFoundError(
                f"OKR file not found at {OKR_FILE}. "
                "Create inputs/okr.md or set the INPUT_OKR_TEXT environment variable."
            )
        okr_text = parse_file(OKR_FILE)
        print(f"[orchestrator] Loaded OKR from file: {OKR_FILE}")

    if not interview_text:
        interview_text = parse_directory(INTERVIEWS_DIR)
        if not interview_text.strip():
            print("[orchestrator] Warning: No interview files found in inputs/interviews/. "
                  "Subagent B will have limited input.")

    if not context_text:
        context_text = parse_directory(CONTEXT_DIR)

    return okr_text, interview_text, context_text


def build_tree(outcome_data: dict, opportunities: list, experiments_by_opp: dict) -> dict:
    """
    Assemble the D3-compatible nested tree structure.

    D3 hierarchy format:
    {
      "name": ...,
      "type": "outcome" | "opportunity" | "experiment",
      "meta": { ... },
      "children": [ ... ]
    }
    """
    opportunity_nodes = []

    for opp in opportunities:
        opp_id = opp["id"]
        experiments = experiments_by_opp.get(opp_id, [])

        experiment_nodes = [
            {
                "name": exp["hypothesis"],
                "type": "experiment",
                "meta": {
                    "experiment": exp.get("experiment", ""),
                    "signal": exp.get("signal", ""),
                    "effort": exp.get("effort", ""),
                    "id": exp.get("id", ""),
                }
            }
            for exp in experiments
        ]

        opportunity_nodes.append({
            "name": opp["opportunity"],
            "type": "opportunity",
            "meta": {
                "evidence": opp.get("evidence", ""),
                "customer_segment": opp.get("customer_segment", ""),
                "id": opp_id,
            },
            "children": experiment_nodes,
        })

    tree = {
        "name": outcome_data.get("outcome", "Business Outcome"),
        "type": "outcome",
        "meta": {
            "metric": outcome_data.get("metric", ""),
            "time_horizon": outcome_data.get("time_horizon", ""),
            "alignment": outcome_data.get("alignment", ""),
            "confidence": outcome_data.get("confidence", ""),
        },
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "children": opportunity_nodes,
    }

    return tree


def run():
    print("\n" + "=" * 60)
    print("  OST Architect — Discovery Mapper")
    print("=" * 60 + "\n")

    # ── Step 1: Load inputs ────────────────────────────────────────
    print("[orchestrator] Loading inputs...")
    okr_text, interview_text, context_text = load_inputs()
    print(f"[orchestrator] OKR text: {len(okr_text)} chars")
    print(f"[orchestrator] Interview text: {len(interview_text)} chars")
    print(f"[orchestrator] Context text: {len(context_text)} chars\n")

    # ── Input validation ───────────────────────────────────────────
    if len(okr_text.strip()) < 20:
        raise ValueError(
            "[orchestrator] OKR text is too short (minimum 20 characters). "
            "Provide a meaningful OKR or business outcome before running the pipeline."
        )
    if len(interview_text.strip()) < 50:
        raise ValueError(
            "[orchestrator] Interview text is too short (minimum 50 characters). "
            "Provide at least one user interview or research note before running the pipeline."
        )

    # ── Step 2: Subagent A — Outcome Tracker ──────────────────────
    print("[orchestrator] Running Subagent A: Outcome Tracker...")
    outcome_data = outcome_tracker.run(okr_text=okr_text, context_text=context_text)
    print(f"[orchestrator] ✓ Outcome: {outcome_data['outcome']}\n")

    # ── Step 3: Subagent B — Pain Point Synthesizer ───────────────
    print("[orchestrator] Running Subagent B: Pain Point Synthesizer...")
    opportunities = pain_point_synthesizer.run(
        interview_text=interview_text,
        outcome=outcome_data["outcome"]
    )
    print(f"[orchestrator] ✓ Found {len(opportunities)} opportunities\n")

    # ── Step 4: Subagent C — Experiment Ideator (per branch) ──────
    experiments_by_opp = {}
    for i, opp in enumerate(opportunities):
        print(f"[orchestrator] Running Subagent C for opportunity {i + 1}/{len(opportunities)}: {opp['id']}...")
        experiments = experiment_ideator.run(
            opportunity=opp,
            outcome=outcome_data["outcome"]
        )
        experiments_by_opp[opp["id"]] = experiments

    print(f"\n[orchestrator] ✓ Experiments generated for all {len(opportunities)} opportunities\n")

    # ── Step 5: Assemble tree ──────────────────────────────────────
    print("[orchestrator] Assembling OST tree...")
    tree = build_tree(outcome_data, opportunities, experiments_by_opp)

    # ── Step 6: Write output ───────────────────────────────────────
    os.makedirs(os.path.dirname(OUTPUT_FILE), exist_ok=True)
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        json.dump(tree, f, indent=2, ensure_ascii=False)

    print(f"[orchestrator] ✓ Tree written to: {OUTPUT_FILE}")

    # ── Summary ────────────────────────────────────────────────────
    total_experiments = sum(len(v) for v in experiments_by_opp.values())
    print("\n" + "=" * 60)
    print("  OST Generation Complete")
    print("=" * 60)
    print(f"  Outcome:      {outcome_data['outcome']}")
    print(f"  Metric:       {outcome_data.get('metric', 'N/A')}")
    print(f"  Opportunities: {len(opportunities)}")
    print(f"  Experiments:  {total_experiments}")
    print(f"  Output:       {OUTPUT_FILE}")
    print("=" * 60 + "\n")

    return tree


if __name__ == "__main__":
    run()
