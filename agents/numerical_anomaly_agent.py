import json
import os
import statistics


def load_partial_data(path):

    with open(path, "r") as f:
        return json.load(f)


def calculate_residuals(data):

    results = []

    for row in data:

        residual = (
            row["observed_acceleration_m_s2"]
            - row["predicted_acceleration_m_s2"]
        )

        results.append({
            "time_days": row["time_days"],
            "observed_acceleration_m_s2":
                row["observed_acceleration_m_s2"],
            "predicted_acceleration_m_s2":
                row["predicted_acceleration_m_s2"],
            "residual_m_s2": residual,
            "thermal_power_watts":
                row["thermal_power_watts"]
        })

    return results


def calculate_basic_statistics(residuals):

    values = [
        row["residual_m_s2"]
        for row in residuals
    ]

    mean_value = statistics.mean(values)

    minimum = min(values)
    maximum = max(values)

    return {
        "mean_residual_m_s2": mean_value,
        "minimum_residual_m_s2": minimum,
        "maximum_residual_m_s2": maximum,
        "persistent_nonzero_residual": (
            all(value != 0 for value in values)
        )
    }


def calculate_thermal_relationship(data):

    thermal = [
        row["thermal_power_watts"]
        for row in data
    ]

    residuals = [
        row["observed_acceleration_m_s2"]
        - row["predicted_acceleration_m_s2"]
        for row in data
    ]

    n = len(thermal)

    mean_x = statistics.mean(thermal)
    mean_y = statistics.mean(residuals)

    numerator = sum(
        (x - mean_x) * (y - mean_y)
        for x, y in zip(thermal, residuals)
    )

    denominator_x = sum(
        (x - mean_x) ** 2
        for x in thermal
    )

    denominator_y = sum(
        (y - mean_y) ** 2
        for y in residuals
    )

    denominator = (
        denominator_x * denominator_y
    ) ** 0.5

    if denominator == 0:
        correlation = None
    else:
        correlation = numerator / denominator

    return {
        "thermal_power_residual_correlation":
            correlation
    }


def run_numerical_anomaly_detection(path):

    case = load_partial_data(path)

    data = case["data"]

    residuals = calculate_residuals(data)

    statistics_result = calculate_basic_statistics(
        residuals
    )

    relationship = calculate_thermal_relationship(
        data
    )

    return {
        "case_id": case["case_id"],
        "analysis_type": "numerical_residual_analysis",
        "residuals": residuals,
        "statistics": statistics_result,
        "relationships": relationship
    }


if __name__ == "__main__":

    path = (
        "data/partial/"
        "pioneer_partial.json"
    )

    result = run_numerical_anomaly_detection(
        path
    )

    print(
        json.dumps(
            result,
            indent=2
        )
    )
