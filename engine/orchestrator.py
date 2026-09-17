import sys
import os
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
from engine.numerical_anomaly import analyze_measurements


CASE_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "pioneer",
    "blind_case.json"
)


def load_case():
    with open(CASE_PATH, "r") as f:
        return json.load(f)


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

    missing_from_critic = hypothesis_ids - critic_ids
    unexpected_in_critic = critic_ids - hypothesis_ids

    return {
        "valid": (
            not missing_from_critic
            and not unexpected_in_critic
        ),
        "hypothesis_ids": sorted(hypothesis_ids),
        "critic_ids": sorted(critic_ids),
        "missing_from_critic": sorted(missing_from_critic),
        "unexpected_in_critic": sorted(unexpected_in_critic)
    }


def run_pipeline():

    print("\n========================================")
    print("          ANOMALY ENGINE")
    print("========================================\n")

    case = load_case()

    print("[1/5] Running Evidence Agent...")

    evidence_raw = run_evidence_agent(case)
    evidence = extract_json(evidence_raw)

    print("      ✓ Evidence complete\n")

    print("[2/6] Running Numerical Anomaly Engine...")

    measurements = case.get("data", [])

    if not measurements:
        measurements = case.get("measurements", [])

    if measurements:
        numerical = analyze_measurements(measurements)

        print(
            "      ✓ Numerical analysis complete"
        )

        print(
            "      ✓ Numeric columns:",
            len(numerical.get("numeric_columns", []))
        )

        print(
            "      ✓ Candidate anomalies:",
            len(numerical.get("candidate_anomalies", []))
        )

        print(
            "      ✓ Patterns:",
            len(numerical.get("patterns", []))
        )
    else:
        print("      ! No numerical measurement table in this case")
        print("      ✓ Numerical analysis skipped safely")

        numerical = {
            "status": "no_data",
            "row_count": 0,
            "numeric_columns": [],
            "columns": {},
            "correlations": [],
            "residuals": [],
            "patterns": [],
            "candidate_anomalies": []
        }

    print("\n[3/6] Running Anomaly Agent...")

    anomaly_input = {
        "evidence": evidence,
        "numerical_analysis": numerical
    }

    anomaly_raw = run_anomaly_agent(
        json.dumps(anomaly_input, indent=2)
    )

    anomaly = extract_json(anomaly_raw)

    print("      ✓ Anomaly analysis complete\n")

    print("[4/6] Running Hypothesis Agent...")

    hypothesis_raw = run_hypothesis_agent(
        json.dumps(anomaly, indent=2)
    )

    hypotheses = extract_json(hypothesis_raw)

    print(
        "      ✓ Generated "
        f"{len(hypotheses.get('hypotheses', []))} hypotheses\n"
    )

    print("[5/6] Running Critic Agent...")

    critic_raw = run_critic_agent(
        json.dumps(hypotheses, indent=2),
        json.dumps(anomaly, indent=2)
    )

    critic = extract_json(critic_raw)

    print("      ✓ Critic analysis complete\n")

    print("========================================")
    print("          PIPELINE VALIDATION")
    print("========================================\n")

    validation = validate_hypotheses(
        hypotheses,
        critic
    )

    print(
        "Hypotheses:",
        validation["hypothesis_ids"]
    )

    print(
        "Critic:",
        validation["critic_ids"]
    )

    if validation["valid"]:
        print("\n✓ HYPOTHESIS CONTRACT PASSED")
    else:
        print("\n✗ HYPOTHESIS CONTRACT FAILED")

        if validation["missing_from_critic"]:
            print(
                "Missing from critic:",
                validation["missing_from_critic"]
            )

        if validation["unexpected_in_critic"]:
            print(
                "Unexpected critic IDs:",
                validation["unexpected_in_critic"]
            )

    print("\n[5/5] Running Dynamic Scientific Testing...")

    test_result = run_testing_agent(
        hypotheses,
        critic,
        case
    )

    print(
        "      ✓ Selected tool:",
        test_result["selection"]["selected_tool"]
    )

    print(
        "      ✓ Target:",
        test_result["selection"]["target_hypothesis"]
    )

    print("      ✓ Scientific test complete\n")

    state = {
        "case": case,
        "evidence": evidence,
        "numerical_analysis": numerical,
        "anomaly": anomaly,
        "hypotheses": hypotheses,
        "critic": critic,
        "testing": test_result,
        "validation": validation
    }

    state_path = os.path.join(
        PROJECT_ROOT,
        "investigation_state.json"
    )

    with open(state_path, "w") as f:
        json.dump(state, f, indent=2)

    print("✓ Investigation state saved.")
    print("  → investigation_state.json")

    print("\n========================================")
    print("             STAGE 2C DONE")
    print("========================================\n")


if __name__ == "__main__":
    run_pipeline()
