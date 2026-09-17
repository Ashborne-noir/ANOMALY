import os
import sys
import json

PROJECT_ROOT = os.path.dirname(
    os.path.dirname(os.path.abspath(__file__))
)

sys.path.insert(0, PROJECT_ROOT)

from agents.numerical_anomaly_agent import (
    run_numerical_anomaly_detection
)

from agents.interpretation_agent import (
    run_interpretation_agent
)


DATA_PATH = os.path.join(
    PROJECT_ROOT,
    "data",
    "partial",
    "pioneer_partial_blind.json"
)


def run_partial_test():

    print("\n========================================")
    print("       ANOMALY PARTIAL-DATA TEST")
    print("========================================\n")

    print("[1/2] Running numerical anomaly detection...")

    numerical_analysis = (
        run_numerical_anomaly_detection(
            DATA_PATH
        )
    )

    print(
        "      ✓ Numerical analysis complete\n"
    )

    print("[2/2] Running scientific interpretation...")

    interpretation = (
        run_interpretation_agent(
            numerical_analysis
        )
    )

    print(
        "      ✓ Interpretation complete\n"
    )

    print("========================================")
    print("        DETECTED ANOMALIES")
    print("========================================\n")

    for anomaly in interpretation.get(
        "detected_anomalies",
        []
    ):
        print("-", anomaly)

    print("\n========================================")
    print("       POSSIBLE EXPLANATIONS")
    print("========================================\n")

    for hypothesis in interpretation.get(
        "possible_explanations",
        []
    ):
        print(
            hypothesis["id"],
            "-",
            hypothesis["explanation"]
        )

    print("\n========================================")
    print("       CRITICAL UNKNOWNS")
    print("========================================\n")

    for unknown in interpretation.get(
        "critical_unknowns",
        []
    ):
        print("-", unknown)

    output = {
        "numerical_analysis":
            numerical_analysis,
        "interpretation":
            interpretation
    }

    output_path = os.path.join(
        PROJECT_ROOT,
        "partial_test_result.json"
    )

    with open(output_path, "w") as f:
        json.dump(
            output,
            f,
            indent=2
        )

    print(
        "\n✓ Partial test state saved."
    )

    print(
        "  → partial_test_result.json"
    )

    print("\n========================================")
    print("          PARTIAL TEST DONE")
    print("========================================\n")


if __name__ == "__main__":
    run_partial_test()
