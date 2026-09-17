import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

CASES = {
    "pioneer": {
        "required_terms": [
            "thermal", "recoil"
        ],
        "required_behavior": [
            "hypoth", "critic", "falsif", "test"
        ]
    },
    "opera": {
        "required_terms": [
            "timing", "systematic"
        ],
        "required_behavior": [
            "hypoth", "critic", "falsif", "test"
        ]
    },
    "flyby": {
        "required_terms": [
            "null", "systematic"
        ],
        "required_behavior": [
            "hypoth", "critic", "falsif", "test"
        ]
    }
}


def flatten(obj):
    if isinstance(obj, dict):
        return " ".join(flatten(v) for v in obj.values())
    if isinstance(obj, list):
        return " ".join(flatten(v) for v in obj)
    return str(obj)


def check_case(case_name):
    path = os.path.join(
        ROOT, "benchmark_results", f"{case_name}_result.json"
    )

    if not os.path.exists(path):
        return {
            "case": case_name,
            "classification": "FAIL",
            "score": 0,
            "checks": {},
            "reason": "Result file missing"
        }

    with open(path) as f:
        result = json.load(f)

    text = flatten(result).lower()

    checks = {}

    # 1. Required scientific signal
    for term in CASES[case_name]["required_terms"]:
        checks[f"contains_{term}"] = term in text

    # 2. Agentic/scientific reasoning behavior
    for term in CASES[case_name]["required_behavior"]:
        checks[f"contains_{term}"] = term in text

    # 3. Structured pipeline outputs
    checks["evidence_present"] = bool(result.get("evidence"))
    checks["anomaly_present"] = bool(result.get("anomaly"))
    checks["hypotheses_present"] = bool(
        result.get("hypotheses", {}).get("hypotheses")
    )
    checks["critic_present"] = bool(
        result.get("critic", {}).get("critiques")
    )
    checks["testing_present"] = bool(result.get("testing"))

    # 4. Hypothesis ↔ critic contract
    hypotheses = {
        h.get("id")
        for h in result.get("hypotheses", {}).get("hypotheses", [])
    }

    critiques = {
        c.get("hypothesis_id")
        for c in result.get("critic", {}).get("critiques", [])
    }

    checks["hypothesis_critic_contract"] = (
        bool(hypotheses)
        and hypotheses == critiques
    )

    passed = sum(checks.values())
    total = len(checks)
    score = round((passed / total) * 100, 1)

    if score >= 90:
        classification = "PASS"
    elif score >= 70:
        classification = "PARTIAL"
    else:
        classification = "FAIL"

    return {
        "case": case_name,
        "classification": classification,
        "score": score,
        "passed_checks": passed,
        "total_checks": total,
        "checks": checks
    }


def main():
    evaluations = [
        check_case("pioneer"),
        check_case("opera"),
        check_case("flyby")
    ]

    passed = sum(x["classification"] == "PASS" for x in evaluations)

    output = {
        "evaluation_type": "deterministic_structural_scientific_checks",
        "evaluations": evaluations,
        "summary": {
            "cases": len(evaluations),
            "passed": passed,
            "partial": sum(
                x["classification"] == "PARTIAL"
                for x in evaluations
            ),
            "failed": sum(
                x["classification"] == "FAIL"
                for x in evaluations
            )
        }
    }

    out = os.path.join(ROOT, "objective_evaluation.json")

    with open(out, "w") as f:
        json.dump(output, f, indent=2)

    print("\n=== OBJECTIVE EVALUATION ===")

    for x in evaluations:
        print(
            f'{x["case"].upper():8} '
            f'{x["classification"]:7} '
            f'{x["score"]}% '
            f'({x["passed_checks"]}/{x["total_checks"]})'
        )

    print("\nSaved:")
    print("→ objective_evaluation.json")


if __name__ == "__main__":
    main()
