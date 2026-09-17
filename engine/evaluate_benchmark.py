import os
import json
from google import genai

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

RESULTS_ROOT = os.path.join(
    PROJECT_ROOT,
    "benchmark_results"
)

BENCHMARK_ROOT = os.path.join(
    PROJECT_ROOT,
    "data",
    "benchmarks"
)

MODEL = "gemini-3.6-flash"


def load_json(path):
    with open(path, "r") as f:
        return json.load(f)


def evaluate_case(case_name):
    result_path = os.path.join(
        RESULTS_ROOT,
        f"{case_name}_result.json"
    )

    answer_path = os.path.join(
        BENCHMARK_ROOT,
        case_name,
        "answer_key.json"
    )

    result = load_json(result_path)
    answer_key = load_json(answer_path)

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    prompt = f"""
You are the Benchmark Evaluation Agent for a scientific
reasoning system called ANOMALY.

Evaluate the agent's blind investigation against the
historical evaluation key.

IMPORTANT:

- Judge scientific reasoning, not writing quality.
- Do not reward confident unsupported claims.
- Do not penalize an agent for refusing to conclude when
  the evidence is insufficient.
- Distinguish observations from hypotheses.
- Check whether the agent considered conventional/systematic
  explanations before exotic explanations.
- Check whether it identified useful discriminating tests.
- The answer key is the evaluation standard, not information
  that the original agent was allowed to see.

CASE:

{json.dumps(result["case"], indent=2)}

ANOMALY OUTPUT:

EVIDENCE:
{json.dumps(result["evidence"], indent=2)}

ANOMALY:
{json.dumps(result["anomaly"], indent=2)}

HYPOTHESES:
{json.dumps(result["hypotheses"], indent=2)}

CRITIC:
{json.dumps(result["critic"], indent=2)}

TESTING:
{json.dumps(result["testing"], indent=2)}

ANSWER KEY:

{json.dumps(answer_key, indent=2)}

Score the case from 0 to 10 in each category:

1. anomaly_detection
2. evidence_usage
3. hypothesis_quality
4. falsification_and_criticism
5. scientific_restraint
6. discriminating_test_quality

Then calculate an overall score from 0 to 10.

Also determine:

PASS = scientifically successful
PARTIAL = meaningful reasoning but important weakness
FAIL = scientifically incorrect or fundamentally misguided

Return ONLY valid JSON:

{{
    "case": "{case_name}",
    "classification": "PASS|PARTIAL|FAIL",
    "scores": {{
        "anomaly_detection": 0,
        "evidence_usage": 0,
        "hypothesis_quality": 0,
        "falsification_and_criticism": 0,
        "scientific_restraint": 0,
        "discriminating_test_quality": 0,
        "overall": 0
    }},
    "strengths": [],
    "weaknesses": [],
    "critical_error": "",
    "reasoning_summary": ""
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


def main():

    cases = [
        "pioneer",
        "opera",
        "flyby"
    ]

    evaluations = []

    print("\n")
    print("########################################")
    print("#                                      #")
    print("#       ANOMALY SCIENTIFIC AUDIT       #")
    print("#                                      #")
    print("########################################")

    for case_name in cases:

        print("\n========================================")
        print(f"       EVALUATING: {case_name.upper()}")
        print("========================================\n")

        evaluation = evaluate_case(case_name)

        evaluations.append(evaluation)

        print(
            "Classification:",
            evaluation["classification"]
        )

        print(
            "Overall:",
            evaluation["scores"]["overall"],
            "/ 10"
        )

        print("\nStrengths:")

        for item in evaluation.get("strengths", []):
            print("-", item)

        print("\nWeaknesses:")

        for item in evaluation.get("weaknesses", []):
            print("-", item)

    output = {
        "evaluations": evaluations
    }

    output_path = os.path.join(
        PROJECT_ROOT,
        "benchmark_evaluation.json"
    )

    with open(output_path, "w") as f:
        json.dump(output, f, indent=2)

    print("\n")
    print("========================================")
    print("          FINAL BENCHMARK AUDIT")
    print("========================================\n")

    for evaluation in evaluations:

        print(
            evaluation["case"].upper(),
            "→",
            evaluation["classification"],
            "(",
            evaluation["scores"]["overall"],
            "/10)"
        )

    passed = sum(
        1
        for e in evaluations
        if e["classification"] == "PASS"
    )

    partial = sum(
        1
        for e in evaluations
        if e["classification"] == "PARTIAL"
    )

    failed = sum(
        1
        for e in evaluations
        if e["classification"] == "FAIL"
    )

    print("\nPASS:", passed)
    print("PARTIAL:", partial)
    print("FAIL:", failed)

    print("\n✓ Evaluation saved:")
    print("  → benchmark_evaluation.json")


if __name__ == "__main__":
    main()
