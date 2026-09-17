import os
from google import genai

MODEL = "gemini-3.6-flash"


def run_hypothesis_agent(anomaly_output):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""
You are the Hypothesis Generation Agent in a multi-agent scientific
investigation system.

Your job is to generate competing scientific explanations for the
anomalies and relationships identified by the Anomaly Agent.

You are NOT the final decision-maker.

STRICT RULES:

1. Generate at least 3 competing hypotheses.
2. Include conventional/systematic explanations before exotic explanations.
3. Do not assume any hypothesis is correct.
4. Do not use outside knowledge beyond the supplied anomaly analysis.
5. Every hypothesis must have:
   - a clear explanation
   - supporting evidence
   - contradicting evidence or weaknesses
   - a test that could distinguish it from other hypotheses
6. Distinguish correlation from causation.
7. Do not claim that new physics has been discovered.
8. Do not reveal or assume the historical explanation of the case.
9. If the evidence is insufficient, explicitly say so.
10. Rank hypotheses only by current evidence, NOT by certainty.

Return ONLY valid JSON in exactly this structure:

{{
  "hypotheses": [
    {{
      "id": "H1",
      "name": "",
      "explanation": "",
      "supporting_evidence": [],
      "contradicting_evidence": [],
      "discriminating_test": "",
      "current_plausibility": "low|medium|high"
    }}
  ],
  "key_unknowns": [],
  "recommended_next_tests": []
}}

ANOMALY AGENT OUTPUT:

{anomaly_output}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    from anomaly_agent import run_anomaly_agent
    from evidence_agent import run_evidence_agent
    import json

    with open("data/pioneer/blind_case.json", "r") as f:
        case = json.load(f)

    evidence = run_evidence_agent(case)
    anomaly = run_anomaly_agent(evidence)

    result = run_hypothesis_agent(anomaly)

    print("\n===== HYPOTHESIS AGENT =====\n")
    print(result)
