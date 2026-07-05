"""
Subagent C — Experiment Ideator.

For a single customer opportunity branch, generates testable feature hypotheses.
Each hypothesis includes a proposed experiment and a measurable success signal.
"""

import json
import sys
import os
import re

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from utils.gemini_client import ask

SYSTEM_INSTRUCTION = """
You are a product manager skilled in hypothesis-driven development and lean experimentation.
You specialize in generating small, testable feature ideas that directly address customer
opportunities — following the Opportunity Solution Tree framework.

Each solution must be:
- Small enough to test in 1-2 weeks
- Directly traceable to the customer opportunity provided
- Paired with a concrete experiment (how to test it) and a measurable signal (what success looks like)

You always respond with valid JSON only — no markdown, no explanation, no code fences.
""".strip()


def run(opportunity: dict, outcome: str) -> list:
    """
    Generate testable feature hypotheses for a single customer opportunity.

    Args:
        opportunity: A single opportunity dict from Subagent B
                     (keys: id, opportunity, evidence, customer_segment)
        outcome: The top-level business outcome for context.

    Returns:
        List of dicts, each with keys: id, hypothesis, experiment, signal, effort
    """
    prompt = f"""
## Business Outcome (context)
{outcome}

## Customer Opportunity
{opportunity['opportunity']}

Customer segment: {opportunity.get('customer_segment', 'All users')}
Evidence: {opportunity.get('evidence', 'N/A')}

---

Generate 2 to 4 testable feature hypotheses that directly address this customer opportunity.

For each hypothesis:
- State the feature idea clearly and concisely
- Describe a lightweight experiment to test it (prototype, A/B test, fake door, etc.)
- Define a measurable success signal

Return a JSON array:
[
  {{
    "id": "{opportunity['id']}_exp_1",
    "hypothesis": "If we build [feature], then [customer segment] will [desired behaviour] because [reason]",
    "experiment": "How to test this in 1-2 weeks (e.g. clickable prototype, email campaign, fake door test)",
    "signal": "The metric or observable behaviour that indicates this is working",
    "effort": "Small / Medium / Large"
  }},
  ...
]
""".strip()

    response = ask(prompt=prompt, system_instruction=SYSTEM_INSTRUCTION)

    try:
        result = json.loads(response)
    except json.JSONDecodeError:
        match = re.search(r'\[.*\]', response, re.DOTALL)
        if match:
            result = json.loads(match.group())
        else:
            raise ValueError(f"Experiment Ideator: Could not parse JSON from Gemini response:\n{response}")

    print(f"[experiment_ideator] Generated {len(result)} experiments for: {opportunity['id']}")
    return result
