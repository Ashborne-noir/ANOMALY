import os
import sys
import json

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from agents.evidence_agent import run_evidence_agent
from agents.anomaly_agent import run_anomaly_agent
from agents.hypothesis_agent import run_hypothesis_agent
from agents.critic_agent import run_critic_agent
from agents.testing_agent import run_testing_agent


BENCHMARK_ROOT = os.path.join(
    PROJECT_ROOT,
    "data",
    "benchmarks"
)

RESULTS_ROOT = os.path.join(
    PROJECT_ROOT,
    "benchmark_results"
)


def extract_json(text):
    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines)

    return json.loads(text)


def validate_hypotheses(hypothesis_output, critic_output):
    hypothesis_ids = {
        h["id"]
        for h in hypothesis_output.get("hypotheses", [])
    }

    critic_ids = {
        c["hypothesis_id"]
        for c in critic_output.get("critiques", [])
    }

    return {
        "valid": hypothesis_ids == critic_ids,
        "hypothesis_ids": sorted(hypothesis_ids),
        "critic_ids": sorted(critic_ids),
        "missing_from_critic": sorted(
            hypothesis_ids - critic_ids
        ),
        "unexpected_in_critic": sorted(
            critic_ids - hypothesis_ids
        )
    }


def load_case(case_name):
    path = os.path.join(
        BENCHMARK_ROOT,
        case_name,
        "blind_case.json"
    )

    with open(path, "r") as f:
        return json.load(f)


def run_case(case_name):
    print("\n")
    print("========================================")
    print(f"       BENCHMARK: {case_name.upper()}")
    print("========================================\n")

    case = load_case(case_name)

    print("[1/5] Evidence Agent...")
    evidence_raw = run_evidence_agent(case)
    evidence = extract_json(evidence_raw)
    print("      ✓\n")

    print("[2/5] Anomaly Agent...")
    anomaly_raw = run_anomaly_agent(
        json.dumps(evidence, indent=2)
    )
    anomaly = extract_json(anomaly_raw)
    print("      ✓\n")

    print("[3/5] Hypothesis Agent...")
    hypothesis_raw = run_hypothesis_agent(
        json.dumps(anomaly, indent=2)
    )
    hypotheses = extract_json(hypothesis_raw)

    print(
        f"      ✓ Generated "
        f"{len(hypotheses.get('hypotheses', []))} hypotheses\n"
    )

    print("[4/5] Critic Agent...")
    critic_raw = run_critic_agent(
        json.dumps(hypotheses, indent=2),
        json.dumps(anomaly, indent=2)
    )
    critic = extract_json(critic_raw)
    print("      ✓\n")

    validation = validate_hypotheses(
        hypotheses,
        critic
    )

    print("Contract validation:")

    if validation["valid"]:
        print("      ✓ PASSED")
    else:
        print("      ✗ FAILED")
        print(
            "      Missing:",
            validation["missing_from_critic"]
        )
        print(
            "      Unexpected:",
            validation["unexpected_in_critic"]
        )

    print("\n[5/5] Dynamic Scientific Testing...")

    testing = run_testing_agent(
        hypotheses,
        critic,
        case
    )

    print(
        "      ✓ Selected:",
        testing["selection"]["selected_tool"]
    )

    print(
        "      ✓ Target:",
        testing["selection"]["target_hypothesis"]
    )

    result = {
        "case": case,
        "evidence": evidence,
        "anomaly": anomaly,
        "hypotheses": hypotheses,
        "critic": critic,
        "testing": testing,
        "validation": validation
    }

    os.makedirs(
        RESULTS_ROOT,
        exist_ok=True
    )

    result_path = os.path.join(
        RESULTS_ROOT,
        f"{case_name}_result.json"
    )

    with open(result_path, "w") as f:
        json.dump(result, f, indent=2)

    print("\n✓ Result saved:")
    print(f"  → benchmark_results/{case_name}_result.json")

    return result


def main():
    print("\n")
    print("########################################")
    print("#                                      #")
    print("#        ANOMALY BENCHMARK SUITE       #")
    print("#                                      #")
    print("########################################")

    cases = [
        "pioneer",
        "opera",
        "flyby"
    ]

    completed = []

    for case_name in cases:
        try:
            run_case(case_name)
            completed.append(case_name)

        except Exception as e:
            print("\n✗ BENCHMARK FAILED")
            print("Case:", case_name)
            print("Error:", type(e).__name__)
            print("Details:", str(e))
            break

    print("\n")
    print("========================================")
    print("         BENCHMARK RUN SUMMARY")
    print("========================================\n")

    for case_name in cases:
        if case_name in completed:
            print(f"✓ {case_name.upper()}")
        else:
            print(f"- {case_name.upper()}")

    print(
        f"\nCompleted: {len(completed)}/{len(cases)}"
    )

    if len(completed) == len(cases):
        print("\n✓ ALL BENCHMARK CASES COMPLETED")
        print(
            "  Results stored in "
            "benchmark_results/"
        )


if __name__ == "__main__":
    main()
