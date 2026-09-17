import json
import math
import statistics
from pathlib import Path


def is_number(value):
    return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)


def numeric_columns(rows):
    if not rows:
        return []

    columns = rows[0].keys()
    result = []

    for column in columns:
        values = [row.get(column) for row in rows]
        numeric = [v for v in values if is_number(v)]

        if len(numeric) >= 2:
            result.append(column)

    return result


def basic_statistics(values):
    if not values:
        return {}

    return {
        "count": len(values),
        "mean": statistics.mean(values),
        "median": statistics.median(values),
        "min": min(values),
        "max": max(values),
        "stdev": statistics.stdev(values) if len(values) > 1 else 0.0,
    }


def linear_trend(values):
    """
    Simple least-squares slope using index as x.
    Positive = increasing
    Negative = decreasing
    Near zero = stable
    """
    if len(values) < 2:
        return {
            "slope": 0.0,
            "direction": "insufficient_data"
        }

    x = list(range(len(values)))
    x_mean = statistics.mean(x)
    y_mean = statistics.mean(values)

    numerator = sum((xi - x_mean) * (yi - y_mean) for xi, yi in zip(x, values))
    denominator = sum((xi - x_mean) ** 2 for xi in x)

    slope = numerator / denominator if denominator else 0.0

    scale = abs(y_mean) if y_mean != 0 else 1.0
    normalized_slope = slope / scale

    if abs(normalized_slope) < 0.01:
        direction = "stable"
    elif slope > 0:
        direction = "increasing"
    else:
        direction = "decreasing"

    return {
        "slope": slope,
        "normalized_slope": normalized_slope,
        "direction": direction
    }


def pearson_correlation(x, y):
    if len(x) != len(y) or len(x) < 2:
        return None

    x_mean = statistics.mean(x)
    y_mean = statistics.mean(y)

    numerator = sum(
        (a - x_mean) * (b - y_mean)
        for a, b in zip(x, y)
    )

    x_sum = sum((a - x_mean) ** 2 for a in x)
    y_sum = sum((b - y_mean) ** 2 for b in y)

    denominator = math.sqrt(x_sum * y_sum)

    if denominator == 0:
        return None

    return numerator / denominator


def detect_outliers(values):
    if len(values) < 4:
        return {
            "method": "z_score",
            "indices": [],
            "count": 0
        }

    mean = statistics.mean(values)
    stdev = statistics.stdev(values)

    if stdev == 0:
        return {
            "method": "z_score",
            "indices": [],
            "count": 0
        }

    indices = [
        i for i, value in enumerate(values)
        if abs((value - mean) / stdev) >= 2.5
    ]

    return {
        "method": "z_score",
        "threshold": 2.5,
        "indices": indices,
        "count": len(indices)
    }


def detect_persistence(values):
    if len(values) < 3:
        return {
            "persistent": False,
            "nonzero_count": 0,
            "ratio": 0.0
        }

    nonzero = [v for v in values if abs(v) > 1e-15]
    ratio = len(nonzero) / len(values)

    return {
        "persistent": ratio >= 0.75,
        "nonzero_count": len(nonzero),
        "ratio": ratio
    }


def residual_analysis(rows, observed_column, predicted_column):
    observed = [
        row.get(observed_column)
        for row in rows
        if is_number(row.get(observed_column))
    ]

    predicted = [
        row.get(predicted_column)
        for row in rows
        if is_number(row.get(predicted_column))
    ]

    if len(observed) != len(predicted) or not observed:
        return {
            "available": False,
            "reason": "Observed and predicted columns could not be aligned."
        }

    residuals = [
        observed_value - predicted_value
        for observed_value, predicted_value in zip(observed, predicted)
    ]

    return {
        "available": True,
        "residuals": residuals,
        "statistics": basic_statistics(residuals),
        "trend": linear_trend(residuals),
        "persistence": detect_persistence(residuals),
        "outliers": detect_outliers(residuals)
    }


def analyze_measurements(rows):
    if not rows:
        return {
            "status": "no_data",
            "numeric_columns": [],
            "columns": {},
            "correlations": [],
            "residuals": []
        }

    columns = numeric_columns(rows)

    # Time/index columns are independent variables, not anomaly signals.
    analysis_columns = [
        column for column in columns
        if column.lower() not in {
            "time", "timestamp", "time_days", "day", "days", "index"
        }
    ]

    analysis = {
        "status": "success",
        "row_count": len(rows),
        "numeric_columns": columns,
        "columns": {},
        "correlations": [],
        "residuals": []
    }

    # Analyze each numeric column.
    for column in columns:
        values = [
            row[column]
            for row in rows
            if is_number(row.get(column))
        ]

        analysis["columns"][column] = {
            "statistics": basic_statistics(values),
            "trend": linear_trend(values),
            "outliers": detect_outliers(values),
            "persistence": detect_persistence(values)
        }

    # Analyze every numeric-column pair.
    for i, column_a in enumerate(columns):
        for column_b in columns[i + 1:]:
            paired = [
                (row.get(column_a), row.get(column_b))
                for row in rows
                if is_number(row.get(column_a))
                and is_number(row.get(column_b))
            ]

            if len(paired) >= 3:
                x = [pair[0] for pair in paired]
                y = [pair[1] for pair in paired]

                correlation = pearson_correlation(x, y)

                if correlation is not None:
                    analysis["correlations"].append({
                        "column_a": column_a,
                        "column_b": column_b,
                        "pearson_r": correlation,
                        "strength": (
                            "strong"
                            if abs(correlation) >= 0.7
                            else "moderate"
                            if abs(correlation) >= 0.4
                            else "weak"
                        ),
                        "direction": (
                            "positive"
                            if correlation > 0
                            else "negative"
                            if correlation < 0
                            else "none"
                        )
                    })

    # Automatically detect common observed/predicted naming patterns.
    observed_candidates = [
        c for c in columns
        if "observed" in c.lower()
    ]

    predicted_candidates = [
        c for c in columns
        if "predicted" in c.lower()
        or "expected" in c.lower()
        or "model" in c.lower()
    ]

    for observed in observed_candidates:
        for predicted in predicted_candidates:
            result = residual_analysis(
                rows,
                observed,
                predicted
            )

            if result.get("available"):
                analysis["residuals"].append({
                    "observed_column": observed,
                    "predicted_column": predicted,
                    **result
                })

    # Generate deterministic scientific findings.
    # Separate observations/patterns from actual anomaly candidates.
    candidates = []
    patterns = []

    for column in analysis_columns:
        result = analysis["columns"][column]

        # Trends and persistence are observations, not automatically anomalies.
        if result["trend"]["direction"] != "stable":
            patterns.append({
                "type": "trend",
                "column": column,
                "evidence": result["trend"]
            })

        if result["persistence"]["persistent"]:
            patterns.append({
                "type": "persistent_signal",
                "column": column,
                "evidence": result["persistence"]
            })

        if result["outliers"]["count"] > 0:
            candidates.append({
                "type": "outlier",
                "column": column,
                "evidence": result["outliers"]
            })

    for correlation in analysis["correlations"]:
        if abs(correlation["pearson_r"]) >= 0.7:
            patterns.append({
                "type": "strong_correlation",
                "columns": [
                    correlation["column_a"],
                    correlation["column_b"]
                ],
                "evidence": correlation
            })

    for residual in analysis["residuals"]:
        if residual["persistence"]["persistent"]:
            candidates.append({
                "type": "persistent_residual",
                "observed_column": residual["observed_column"],
                "predicted_column": residual["predicted_column"],
                "evidence": {
                    "statistics": residual["statistics"],
                    "persistence": residual["persistence"],
                    "trend": residual["trend"]
                }
            })

    analysis["patterns"] = patterns
    analysis["candidate_anomalies"] = candidates

    return analysis


def analyze_file(path):
    path = Path(path)

    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)

    # Support all current input formats.
    if isinstance(data, list):
        rows = data
    elif "measurements" in data:
        rows = data["measurements"]
    elif "data" in data and isinstance(data["data"], list):
        rows = data["data"]
    elif isinstance(data.get("evidence"), dict) and "measurements" in data["evidence"]:
        rows = data["evidence"]["measurements"]
    else:
        raise ValueError("No measurement rows found in input.")

    return analyze_measurements(rows)


if __name__ == "__main__":
    input_path = Path("data/partial/pioneer_partial.json")
    output_path = Path("numerical_analysis_result.json")

    result = analyze_file(input_path)

    with output_path.open("w") as f:
        json.dump(result, f, indent=2)

    print("=" * 55)
    print("DAY 3 — NUMERICAL ANOMALY ENGINE")
    print("=" * 55)

    print(f"Rows analyzed: {result['row_count']}")
    print(f"Numeric columns: {result['numeric_columns']}")

    print("\nCOLUMN ANALYSIS")
    for column, info in result["columns"].items():
        stats = info["statistics"]
        trend = info["trend"]

        print(f"\n{column}")
        print(f"  Mean: {stats['mean']}")
        print(f"  Min:  {stats['min']}")
        print(f"  Max:  {stats['max']}")
        print(f"  Trend: {trend['direction']}")

    print("\nCORRELATIONS")
    for correlation in result["correlations"]:
        print(
            f"  {correlation['column_a']} ↔ "
            f"{correlation['column_b']}: "
            f"r={correlation['pearson_r']:.4f} "
            f"({correlation['strength']}, {correlation['direction']})"
        )

    print("\nRESIDUAL ANALYSIS")
    for residual in result["residuals"]:
        print(
            f"  {residual['observed_column']} - "
            f"{residual['predicted_column']}"
        )

        print(
            f"    Mean residual: "
            f"{residual['statistics']['mean']}"
        )

        print(
            f"    Persistent: "
            f"{residual['persistence']['persistent']}"
        )

    print("\nOBSERVED PATTERNS")
    for pattern in result["patterns"]:
        if pattern["type"] == "strong_correlation":
            label = (
                f"{pattern['columns'][0]} ↔ "
                f"{pattern['columns'][1]}"
            )
        else:
            label = pattern.get("column", "")

        print(f"  - {pattern['type']} ({label})")

    print("\nCANDIDATE ANOMALIES")
    for candidate in result["candidate_anomalies"]:
        label = candidate.get(
            "column",
            candidate.get("observed_column", "")
        )

        print(f"  - {candidate['type']} ({label})")

    print(f"\nSaved: {output_path}")
    print("=" * 55)
