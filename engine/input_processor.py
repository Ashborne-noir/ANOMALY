import os
import json
import csv
import io
import re

try:
    from pypdf import PdfReader
except ImportError:
    PdfReader = None


SUPPORTED_EXTENSIONS = {
    ".json": "json",
    ".csv": "csv",
    ".txt": "text",
    ".md": "text",
    ".pdf": "pdf",
}


def _convert_value(value):
    """Convert CSV strings into useful Python types."""
    if value is None:
        return value

    value = value.strip()

    if value == "":
        return ""

    lowered = value.lower()

    if lowered == "true":
        return True

    if lowered == "false":
        return False

    # Integer
    if re.fullmatch(r"[+-]?\d+", value):
        try:
            return int(value)
        except ValueError:
            pass

    # Float / scientific notation
    if re.fullmatch(
        r"[+-]?(?:\d+\.\d*|\.\d+|\d+)(?:[eE][+-]?\d+)?",
        value,
    ):
        try:
            return float(value)
        except ValueError:
            pass

    return value


def normalize_csv_rows(rows):
    """Convert CSV string values to appropriate Python types."""
    normalized = []

    for row in rows:
        normalized.append(
            {
                key: _convert_value(value)
                for key, value in row.items()
            }
        )

    return normalized


def read_file(path):
    """
    Read a supported file.

    JSON -> parsed Python object
    CSV  -> list of dictionaries
    TXT/MD -> text
    PDF -> extracted text
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"File not found: {path}")

    extension = os.path.splitext(path)[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(
            f"Unsupported file type: {extension}. "
            f"Supported: {', '.join(SUPPORTED_EXTENSIONS)}"
        )

    file_type = SUPPORTED_EXTENSIONS[extension]

    if file_type == "json":
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)

    if file_type == "csv":
        with open(path, "r", encoding="utf-8-sig", newline="") as f:
            reader = csv.DictReader(f)
            return normalize_csv_rows(list(reader))

    if file_type == "text":
        with open(path, "r", encoding="utf-8") as f:
            return f.read()

    if file_type == "pdf":
        if PdfReader is None:
            raise ImportError(
                "pypdf is required for PDF ingestion. "
                "Install it with: pip install pypdf"
            )

        try:
            reader = PdfReader(path)
            pages = []

            for page in reader.pages:
                text = page.extract_text() or ""
                pages.append(text)

            return "\n\n".join(pages)

        except Exception as exc:
            raise ValueError(
                f"Failed to extract text from PDF: {path}"
            ) from exc


def ingest_file(path):
    """Read and package a single file with metadata."""
    extension = os.path.splitext(path)[1].lower()

    if extension not in SUPPORTED_EXTENSIONS:
        raise ValueError(f"Unsupported file type: {extension}")

    content = read_file(path)

    return {
        "filename": os.path.basename(path),
        "extension": extension,
        "type": SUPPORTED_EXTENSIONS[extension],
        "content": content,
    }


def ingest_files(paths):
    """Ingest multiple files."""
    return [ingest_file(path) for path in paths]


def build_investigation(
    objective,
    observations=None,
    measurements=None,
    experimental_context=None,
    expected_behavior=None,
    constraints=None,
    sources=None,
    files=None,
):
    """Build the canonical ANOMALY Investigation object."""
    return {
        "objective": objective,
        "observations": observations or [],
        "measurements": measurements or [],
        "experimental_context": experimental_context or {},
        "expected_behavior": expected_behavior,
        "constraints": constraints or [],
        "sources": sources or [],
        "files": files or [],
    }


def validate_investigation(investigation):
    """Validate the canonical Investigation structure."""
    errors = []

    if not isinstance(investigation, dict):
        return False, ["Investigation must be a dictionary."]

    objective = investigation.get("objective")

    if not isinstance(objective, str) or not objective.strip():
        errors.append("objective must be a non-empty string.")

    list_fields = [
        "observations",
        "measurements",
        "constraints",
        "sources",
        "files",
    ]

    for field in list_fields:
        if field in investigation and not isinstance(
            investigation[field], list
        ):
            errors.append(f"{field} must be a list.")

    if "experimental_context" in investigation and not isinstance(
        investigation["experimental_context"], dict
    ):
        errors.append("experimental_context must be a dictionary.")

    if "expected_behavior" in investigation:
        value = investigation["expected_behavior"]

        if value is not None and not isinstance(value, str):
            errors.append(
                "expected_behavior must be a string or null."
            )

    return len(errors) == 0, errors


def create_from_files(
    paths,
    objective,
    expected_behavior=None,
    experimental_context=None,
    constraints=None,
    sources=None,
):
    """
    Create a canonical Investigation from uploaded files.

    JSON dictionaries can contribute canonical fields.
    JSON lists become observations.
    CSV rows become measurements.
    TXT/MD/PDF become file/document entries.
    """
    observations = []
    measurements = []
    files = []

    investigation_context = dict(
        experimental_context or {}
    )

    investigation_constraints = list(
        constraints or []
    )

    investigation_sources = list(
        sources or []
    )

    for path in paths:
        item = ingest_file(path)

        file_type = item["type"]
        content = item["content"]

        if file_type == "csv":
            measurements.extend(content)

        elif file_type == "json":
            if isinstance(content, dict):
                # Import matching canonical fields.
                if isinstance(
                    content.get("observations"),
                    list,
                ):
                    observations.extend(
                        content["observations"]
                    )

                if isinstance(
                    content.get("measurements"),
                    list,
                ):
                    measurements.extend(
                        content["measurements"]
                    )

                if isinstance(
                    content.get("experimental_context"),
                    dict,
                ):
                    investigation_context.update(
                        content["experimental_context"]
                    )

                if isinstance(
                    content.get("constraints"),
                    list,
                ):
                    investigation_constraints.extend(
                        content["constraints"]
                    )

                if isinstance(
                    content.get("sources"),
                    list,
                ):
                    investigation_sources.extend(
                        content["sources"]
                    )

                if (
                    expected_behavior is None
                    and isinstance(
                        content.get("expected_behavior"),
                        str,
                    )
                ):
                    expected_behavior = content[
                        "expected_behavior"
                    ]

            elif isinstance(content, list):
                observations.extend(content)

        elif file_type in ("text", "pdf"):
            files.append(
                {
                    "filename": item["filename"],
                    "type": file_type,
                    "content": content,
                }
            )

        # Keep a lightweight record of every input file.
        if file_type not in ("text", "pdf"):
            files.append(
                {
                    "filename": item["filename"],
                    "type": file_type,
                    "extension": item["extension"],
                }
            )

    return build_investigation(
        objective=objective,
        observations=observations,
        measurements=measurements,
        experimental_context=investigation_context,
        expected_behavior=expected_behavior,
        constraints=investigation_constraints,
        sources=investigation_sources,
        files=files,
    )


def load_investigation_file(path):
    """Load an existing JSON Investigation file."""
    data = read_file(path)

    if not isinstance(data, dict):
        raise ValueError(
            "Investigation JSON must contain an object."
        )

    # Support the previous test-input format while converting
    # it into the new canonical structure.
    evidence = data.get("evidence", {})

    investigation = build_investigation(
        objective=data.get("objective", ""),
        observations=(
            data.get("observations")
            if "observations" in data
            else evidence.get("observations", [])
        ),
        measurements=(
            data.get("measurements")
            if "measurements" in data
            else evidence.get("measurements", [])
        ),
        experimental_context=data.get(
            "experimental_context", {}
        ),
        expected_behavior=data.get(
            "expected_behavior"
        ),
        constraints=data.get(
            "constraints", []
        ),
        sources=data.get(
            "sources", []
        ),
        files=data.get(
            "files",
            evidence.get("documents", []),
        ),
    )

    valid, errors = validate_investigation(
        investigation
    )

    if not valid:
        raise ValueError(
            "Invalid investigation:\n"
            + "\n".join(
                f"- {error}" for error in errors
            )
        )

    return investigation


def create_demo_files():
    """Create small local fixtures for testing."""
    os.makedirs(
        "data/test_inputs",
        exist_ok=True,
    )

    json_path = "data/test_input.json"

    json_data = {
        "objective": (
            "Investigate why the measured efficiency "
            "of a material decreases unexpectedly "
            "at high temperature."
        ),
        "evidence": {
            "observations": [
                "Efficiency is stable at moderate temperature.",
                "Efficiency decreases above 400 C.",
                "The effect is repeatable.",
            ],
            "measurements": [
                {
                    "temperature_C": 300,
                    "efficiency": 0.91,
                },
                {
                    "temperature_C": 350,
                    "efficiency": 0.90,
                },
                {
                    "temperature_C": 400,
                    "efficiency": 0.89,
                },
                {
                    "temperature_C": 450,
                    "efficiency": 0.82,
                },
                {
                    "temperature_C": 500,
                    "efficiency": 0.73,
                },
            ],
            "documents": [],
            "raw_data": [],
        },
        "experimental_context": {
            "system": "Demo Material X",
            "temperature_range": "300-500 C",
            "pressure": "1 atm",
        },
        "expected_behavior": (
            "Efficiency should remain approximately stable."
        ),
        "constraints": [
            "Do not exceed 650 C.",
            "Consider measurement artifacts.",
        ],
        "researcher_hypotheses": [],
        "sources": [],
    }

    with open(
        json_path,
        "w",
        encoding="utf-8",
    ) as f:
        json.dump(
            json_data,
            f,
            indent=2,
        )

    csv_path = "data/test_inputs/example.csv"

    with open(
        csv_path,
        "w",
        encoding="utf-8",
        newline="",
    ) as f:
        writer = csv.writer(f)
        writer.writerow(
            ["temperature_C", "efficiency"]
        )
        writer.writerows(
            [
                [300, 0.91],
                [350, 0.90],
                [400, 0.89],
                [450, 0.82],
                [500, 0.73],
            ]
        )

    txt_path = "data/test_inputs/example.txt"

    with open(
        txt_path,
        "w",
        encoding="utf-8",
    ) as f:
        f.write(
            "Research objective:\n"
            "Investigate why the efficiency of "
            "Demo Material X decreases above 400 C.\n\n"
            "Observations:\n"
            "Efficiency remains stable at moderate temperature.\n"
            "Efficiency decreases significantly above 400 C.\n"
            "The effect appears repeatable.\n\n"
            "Expected behavior:\n"
            "Efficiency should remain approximately stable.\n\n"
            "Constraints:\n"
            "Do not exceed 650 C.\n"
            "Distinguish measurement artifacts from "
            "physical mechanisms.\n"
        )

    return json_path, csv_path, txt_path


if __name__ == "__main__":
    print("=== INPUT PROCESSOR TEST ===")

    json_path, csv_path, txt_path = create_demo_files()

    investigation = load_investigation_file(
        json_path
    )

    valid, errors = validate_investigation(
        investigation
    )

    print("\nJSON")
    print("VALID:", valid)
    print("OBJECTIVE:", investigation["objective"])
    print(
        "MEASUREMENTS:",
        len(investigation["measurements"]),
    )

    csv_result = ingest_file(csv_path)

    print("\nCSV")
    print("TYPE:", csv_result["type"])
    print(
        "ROWS:",
        len(csv_result["content"]),
    )
    print(
        "FIRST ROW:",
        csv_result["content"][0],
    )

    txt_result = ingest_file(txt_path)

    print("\nTXT")
    print("TYPE:", txt_result["type"])
    print(
        "TEXT LENGTH:",
        len(txt_result["content"]),
    )

    print("\n=== INPUT PROCESSOR TEST COMPLETE ===")
