import json
import os
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from engine.input_processor import (
    load_investigation_file,
    validate_investigation,
)

from agents.evidence_agent import run_evidence_agent
from agents.anomaly_agent import run_anomaly_agent
from agents.hypothesis_agent import run_hypothesis_agent
from agents.critic_agent import run_critic_agent
from agents.testing_agent import run_testing_agent


def extract_json(text):
    """
    Safely extract JSON from an LLM response.
    Handles responses wrapped in markdown code fences.
    """
    if isinstance(text, dict):
        return text

    text = text.strip()

    if text.startswith("```"):
        lines = text.splitlines()

        if lines and lines[0].startswith("```"):
            lines = lines[1:]

        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]

        text = "\n".join(lines).strip()

        if text.startswith("json"):
            text = text[4:].strip()

    return json.loads(text)


def prepare_evidence(investigation):
    """
    Convert the user's investigation object into the evidence representation
    expected by the existing Evidence Agent.
    """

    evidence = investigation.get("evidence", {})

    return {
        "research_objective": investigation.get("objective", ""),
        "observations": evidence.get("observations", []),
        "measurements": evidence.get("measurements", []),
        "documents": evidence.get("documents", []),
        "raw_data": evidence.get("raw_data", []),
        "experimental_context": investigation.get(
            "experimental_context", {}
        ),
        "expected_behavior": investigation.get(
            "expected_behavior", ""
        ),
        "constraints": investigation.get(
            "constraints", []
        ),
        "researcher_hypotheses": investigation.get(
            "researcher_hypotheses", []
        ),
        "sources": investigation.get("sources", []),
    }


def validate_hypotheses(hypothesis_output, critic_output):
    """
    Ensure every generated hypothesis receives a corresponding critique.
    """

    hypothesis_ids = {
        h.get("id")
        for h in hypothesis_output.get("hypotheses", [])
        if h.get("id")
    }

    critic_ids = {
        c.get("hypothesis_id")
        for c in critic_output.get("critiques", [])
        if c.get("hypothesis_id")
    }

    return {
        "valid": (
            not hypothesis_ids - critic_ids
            and not critic_ids - hypothesis_ids
        ),
        "hypothesis_ids": sorted(hypothesis_ids),
        "critic_ids": sorted(critic_ids),
        "missing_from_critic": sorted(
            hypothesis_ids - critic_ids
        ),
        "unexpected_in_critic": sorted(
            critic_ids - hypothesis_ids
        ),
    }


def run_investigation(investigation):
    """
    Full ANOMALY investigation pipeline.

    Input:
        Scientist investigation object

    Output:
        Structured investigation state
    """

    print("\n========================================")
    print("        ANOMALY INVESTIGATION")
    print("========================================")

    print("\n[0/5] Validating investigation input")

    valid, errors = validate_investigation(investigation)

    if not valid:
        raise ValueError(
            "Invalid investigation input:\n"
            + "\n".join(f"- {error}" for error in errors)
        )

    print("✓ Input valid")
    print("✓ Objective:", investigation["objective"])

    evidence_input = prepare_evidence(investigation)

    print("\n[1/5] Evidence Agent")
    evidence_raw = run_evidence_agent(
        json.dumps(evidence_input, indent=2)
    )
    evidence = extract_json(evidence_raw)
    print("✓ Evidence structured")

    print("\n[2/5] Anomaly Agent")
    anomaly_raw = run_anomaly_agent(
        json.dumps(evidence, indent=2)
    )
    anomaly = extract_json(anomaly_raw)
    print("✓ Anomaly analysis complete")

    print("\n[3/5] Hypothesis Agent")
    hypotheses_raw = run_hypothesis_agent(
        json.dumps(anomaly, indent=2)
    )
    hypotheses = extract_json(hypotheses_raw)

    hypothesis_count = len(
        hypotheses.get("hypotheses", [])
    )

    print(
        f"✓ Generated {hypothesis_count} hypotheses"
    )

    print("\n[4/5] Critic Agent")
    critic_raw = run_critic_agent(
        json.dumps(hypotheses, indent=2),
        json.dumps(anomaly, indent=2),
    )
    critic = extract_json(critic_raw)

    validation = validate_hypotheses(
        hypotheses,
        critic,
    )

    if validation["valid"]:
        print("✓ Hypothesis/critic contract passed")
    else:
        print("⚠ Hypothesis/critic contract failed")
        print(json.dumps(validation, indent=2))

    print("\n[5/5] Scientific Testing")
    testing = run_testing_agent(
        hypotheses,
        critic,
        investigation,
    )

    state = {
        "investigation": investigation,
        "evidence": evidence,
        "anomaly": anomaly,
        "hypotheses": hypotheses,
        "critic": critic,
        "testing": testing,
        "validation": validation,
    }

    output_path = os.path.join(
        PROJECT_ROOT,
        "test_investigation_state.json",
    )

    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(
            state,
            f,
            indent=2,
            ensure_ascii=False,
        )

    print("\n========================================")
    print("      INVESTIGATION COMPLETE")
    print("========================================")
    print("State saved → test_investigation_state.json")

    return state


def main():
    if len(sys.argv) < 2:
        print(
            "Usage:\n"
            "  python3 engine/input_pipeline.py "
            "data/test_input.json"
        )
        sys.exit(1)

    investigation_path = sys.argv[1]

    investigation = load_investigation_file(
        investigation_path
    )

    run_investigation(investigation)


if __name__ == "__main__":
    main()
