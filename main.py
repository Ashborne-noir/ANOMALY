import json
import os
import sys
import time

ROOT = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, ROOT)

from engine.orchestrator import run_pipeline


def main():
    print("\n" + "=" * 60)
    print("                 ANOMALY")
    print("     Autonomous Scientific Discovery Agent")
    print("=" * 60)

    print("\nResearch objective:")
    print("Investigate an unexplained scientific anomaly.")
    print("\nPipeline:")
    print("Evidence → Anomaly → Hypotheses → Critic → Test → Conclusion")

    input("\nPress ENTER to begin investigation...")

    print("\n[ANOMALY] Starting scientific investigation...\n")

    start = time.time()
    run_pipeline()
    elapsed = time.time() - start

    state_path = os.path.join(ROOT, "investigation_state.json")

    if os.path.exists(state_path):
        with open(state_path) as f:
            state = json.load(f)

        print("\n" + "=" * 60)
        print("                 INVESTIGATION COMPLETE")
        print("=" * 60)

        hypotheses = state.get("hypotheses", {}).get("hypotheses", [])
        testing = state.get("testing", {})

        print(f"\nHypotheses generated: {len(hypotheses)}")

        for h in hypotheses:
            print(f"  {h.get('id', '?')}: {h.get('name', 'Unknown hypothesis')}")
            print(f"      Plausibility: {h.get('current_plausibility', 'unknown')}")

        selection = testing.get("selection", {})
        execution = testing.get("execution", {})
        result = execution.get("result", {})

        print("\nScientific test:")
        print(f"  Tool:   {selection.get('selected_tool', 'N/A')}")
        print(f"  Target: {selection.get('target_hypothesis', 'N/A')}")
        print(f"  Reason: {selection.get('reason', 'N/A')}")

        if result:
            print(f"  Result: {result.get('recoil_acceleration_m_s2', 'N/A')} m/s²")

        print(f"\nRuntime: {elapsed:.1f}s")
        print("\nState saved → investigation_state.json")
        print("=" * 60)

    else:
        print("\nWARNING: investigation_state.json was not created.")


if __name__ == "__main__":
    main()
