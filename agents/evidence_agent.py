import json
import os
from google import genai

MODEL = "gemini-3.6-flash"


def load_case():
    with open("data/pioneer/blind_case.json", "r") as f:
        return json.load(f)


def run_evidence_agent(case):
    client = genai.Client(api_key=os.environ["GEMINI_API_KEY"])

    prompt = f"""
You are the Evidence Agent in a multi-agent scientific investigation system.

Your job is NOT to solve the scientific anomaly.

Your job is to examine the supplied observations and separate:

1. Established observations
2. Important clues
3. Relationships between observations
4. Uncertainties
5. Evidence that could help distinguish competing explanations

STRICT RULES:
- Do not invent facts.
- Do not use outside knowledge.
- Do not state a hypothesis as an established fact.
- Do not give the historical explanation of this case.
- Do not assume that an anomaly has a known cause.
- Be scientifically conservative.

Return ONLY valid JSON in this structure:

{{
  "established_observations": [],
  "important_clues": [],
  "relationships": [],
  "uncertainties": [],
  "discriminating_evidence": []
}}

CASE:

{json.dumps(case, indent=2)}
"""

    response = client.models.generate_content(
        model=MODEL,
        contents=prompt
    )

    return response.text


if __name__ == "__main__":
    case = load_case()
    result = run_evidence_agent(case)

    print("\n===== EVIDENCE AGENT =====\n")
    print(result)
