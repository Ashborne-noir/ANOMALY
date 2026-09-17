import json
import os
from google import genai

MODEL = "gemini-3.6-flash"


def run_anomaly_agent(evidence):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""
You are the Anomaly Detection Agent in a multi-agent scientific investigation system.

Your job is to identify what is scientifically unexpected, contradictory,
unexplained, or potentially interesting in the evidence.

You are NOT allowed to solve the anomaly.

Do NOT use outside knowledge.

Do NOT name the historical explanation of this case.

Do NOT turn a clue into a confirmed cause.

Focus on:
1. What is unexpected?
2. What relationships are unusual?
3. What observations require explanation?
4. Are there contradictions?
5. What patterns deserve hypothesis testing?

Return ONLY valid JSON:

{{
  "core_anomalies": [],
  "unexpected_patterns": [],
  "possible_relationships_to_investigate": [],
  "contradictions_or_tensions": [],
  "questions_for_hypothesis_agent": []
}}

EVIDENCE AGENT OUTPUT:

{evidence}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    with open("data/pioneer/blind_case.json", "r") as f:
        case = json.load(f)

    # For this first prototype, run the evidence agent internally.
    from evidence_agent import run_evidence_agent

    evidence = run_evidence_agent(case)

    result = run_anomaly_agent(evidence)

    print("\n===== ANOMALY AGENT =====\n")
    print(result)
