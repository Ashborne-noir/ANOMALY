import json
import os
from google import genai


MODEL = "gemini-3.6-flash"


def run_interpretation_agent(
    numerical_analysis
):

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    prompt = f"""
You are the Scientific Interpretation Agent.

A deterministic Python analysis has detected patterns
in a scientific dataset.

Your job is to interpret the detected patterns.

IMPORTANT:

- Do not assume the cause.
- Do not claim causation from correlation alone.
- Generate competing explanations.
- Distinguish observations from hypotheses.
- Identify what evidence is still missing.
- Prefer conventional/systematic explanations before exotic ones.
- Do not use outside knowledge.

NUMERICAL ANALYSIS:

{json.dumps(numerical_analysis, indent=2)}

Return ONLY valid JSON:

{{
    "detected_anomalies": [],
    "important_patterns": [],
    "possible_explanations": [
        {{
            "id": "H1",
            "explanation": "",
            "supporting_evidence": [],
            "contradicting_evidence": [],
            "required_test": ""
        }}
    ],
    "critical_unknowns": [],
    "recommended_next_test": ""
}}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    text = response.text.strip()

    if text.startswith("```"):

        lines = text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)
