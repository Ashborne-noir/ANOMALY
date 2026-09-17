import json
import os
from google import genai


MODEL = "gemini-3.6-flash"


# ============================================================
# SCIENTIFIC TOOLS
# ============================================================

def calculate_thermal_recoil(
    power_watts,
    direction_factor,
    spacecraft_mass_kg
):
    if power_watts < 0:
        raise ValueError("power_watts cannot be negative")

    if not 0 <= direction_factor <= 1:
        raise ValueError(
            "direction_factor must be between 0 and 1"
        )

    if spacecraft_mass_kg <= 0:
        raise ValueError(
            "spacecraft_mass_kg must be positive"
        )

    speed_of_light = 299_792_458

    recoil_force = (
        power_watts * direction_factor
    ) / speed_of_light

    acceleration = (
        recoil_force / spacecraft_mass_kg
    )

    return {
        "recoil_force_N": recoil_force,
        "recoil_acceleration_m_s2": acceleration
    }


def compare_acceleration(observed, predicted):

    difference = observed - predicted

    if predicted != 0:
        ratio = observed / predicted
    else:
        ratio = None

    return {
        "observed_m_s2": observed,
        "predicted_m_s2": predicted,
        "difference_m_s2": difference,
        "ratio_observed_to_predicted": ratio
    }


TOOLS = {
    "thermal_recoil_estimation": {
        "description": (
            "Estimate acceleration caused by "
            "anisotropic thermal radiation."
        ),
        "required_inputs": [
            "thermal_power_watts",
            "direction_factor",
            "spacecraft_mass_kg"
        ]
    },

    "acceleration_comparison": {
        "description": (
            "Compare an observed acceleration "
            "with a predicted acceleration."
        ),
        "required_inputs": [
            "observed_acceleration",
            "predicted_acceleration"
        ]
    }
}


# ============================================================
# TEST SELECTION
# ============================================================

def select_test(hypotheses, critic):

    client = genai.Client(
        api_key=os.environ["GEMINI_API_KEY"]
    )

    tool_descriptions = {}

    for name, tool in TOOLS.items():
        tool_descriptions[name] = {
            "description": tool["description"],
            "required_inputs": tool["required_inputs"]
        }

    prompt = f"""
You are the Testing Agent in a scientific
investigation system.

Your job is to select the most useful deterministic
scientific test for the current hypotheses.

AVAILABLE TOOLS:

{json.dumps(tool_descriptions, indent=2)}

HYPOTHESES:

{json.dumps(hypotheses, indent=2)}

CRITIC ANALYSIS:

{json.dumps(critic, indent=2)}

Return ONLY valid JSON:

{{
    "selected_tool": "",
    "target_hypothesis": "",
    "reason": "",
    "required_inputs": []
}}

RULES:

- selected_tool must exactly match an available tool.
- target_hypothesis must identify an existing hypothesis.
- required_inputs must match the selected tool.
- Do not perform calculations.
- Do not invent results.
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


# ============================================================
# GET INPUTS FROM INVESTIGATION DATA
# ============================================================

def get_test_inputs(tool_name, case):

    observations = case.get("observations", [])

    observation_text = " ".join(
        observation["observation"]
        for observation in observations
    ).lower()

    if tool_name == "thermal_recoil_estimation":

        # Current Pioneer blind case contains qualitative
        # thermal information but not numerical telemetry.
        # Therefore numerical demonstration values remain
        # explicitly marked as unavailable historical data.

        return {
            "thermal_power_watts": 2000,
            "direction_factor": 0.05,
            "spacecraft_mass_kg": 250,
            "source": "demonstration_parameters",
            "historical_data_available": False,
            "note": (
                "The current blind case does not contain "
                "numerical thermal telemetry, so these "
                "values are demonstration parameters."
            )
        }

    if tool_name == "acceleration_comparison":

        return {
            "observed_acceleration": None,
            "predicted_acceleration": None,
            "source": "case_data",
            "historical_data_available": False,
            "note": (
                "The current blind case does not contain "
                "both numerical acceleration values."
            )
        }

    raise ValueError(
        f"Unknown scientific tool: {tool_name}"
    )


# ============================================================
# EXECUTE TOOL
# ============================================================

def execute_test(selection, case):

    tool_name = selection["selected_tool"]

    inputs = get_test_inputs(
        tool_name,
        case
    )

    if tool_name == "thermal_recoil_estimation":

        result = calculate_thermal_recoil(
            inputs["thermal_power_watts"],
            inputs["direction_factor"],
            inputs["spacecraft_mass_kg"]
        )

    elif tool_name == "acceleration_comparison":

        if (
            inputs["observed_acceleration"] is None
            or inputs["predicted_acceleration"] is None
        ):
            result = {
                "status": "insufficient_data",
                "reason": inputs["note"]
            }
        else:
            result = compare_acceleration(
                inputs["observed_acceleration"],
                inputs["predicted_acceleration"]
            )

    else:
        raise ValueError(
            f"Unknown scientific tool: {tool_name}"
        )

    return {
        "tool": tool_name,
        "target_hypothesis": (
            selection["target_hypothesis"]
        ),
        "inputs": inputs,
        "result": result
    }


# ============================================================
# MAIN TESTING AGENT
# ============================================================

def run_testing_agent(
    hypotheses,
    critic,
    case
):

    selection = select_test(
        hypotheses,
        critic
    )

    result = execute_test(
        selection,
        case
    )

    return {
        "selection": selection,
        "execution": result
    }
