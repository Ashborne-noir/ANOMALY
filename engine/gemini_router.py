import os
import time
from google import genai


# ============================================================
# ANOMALY GEMINI MODEL ROUTER
# ============================================================
#
# Purpose:
# - Use the preferred Gemini model first.
# - Retry temporary failures.
# - Automatically fall back to another available model.
# - Do NOT hide permanent errors such as authentication or
#   malformed requests.
#
# This protects the investigation pipeline from temporary
# model/service availability problems during demos.
# ============================================================

MODELS = [
    "gemini-3.8-flash",
    "gemini-3.7-flash",
    "gemini-3.6-flash",
]

RETRY_DELAYS = [2, 5]

TRANSIENT_MARKERS = (
    "503",
    "UNAVAILABLE",
    "429",
    "RESOURCE_EXHAUSTED",
    "rate limit",
    "temporarily unavailable",
    "deadline exceeded",
    "timeout",
    "timed out",
)


def _is_transient_error(error):
    message = str(error).upper()
    return any(marker.upper() in message for marker in TRANSIENT_MARKERS)


def generate_content(contents):
    """
    Generate Gemini content with retry + model fallback.

    Returns:
        Gemini response object

    Raises:
        Exception from the final failed model if every
        available model fails.
    """

    api_key = os.environ.get("GEMINI_API_KEY")

    if not api_key:
        raise RuntimeError(
            "GEMINI_API_KEY is not set. "
            "Set the environment variable before running ANOMALY."
        )

    client = genai.Client(api_key=api_key)

    last_error = None

    for model in MODELS:

        print(f"[AI ROUTER] Trying {model}")

        for attempt in range(len(RETRY_DELAYS) + 1):

            try:
                response = client.models.generate_content(
                    model=model,
                    contents=contents,
                )

                print(f"[AI ROUTER] ✓ {model} responded")
                return response

            except Exception as error:
                last_error = error

                # Permanent errors should not silently trigger
                # model switching.
                if not _is_transient_error(error):
                    print(
                        f"[AI ROUTER] ✗ Permanent error from {model}: "
                        f"{type(error).__name__}"
                    )
                    raise

                # Retry temporary failures on the same model.
                if attempt < len(RETRY_DELAYS):
                    delay = RETRY_DELAYS[attempt]

                    print(
                        f"[AI ROUTER] {model} temporarily unavailable "
                        f"(attempt {attempt + 1}). "
                        f"Retrying in {delay}s..."
                    )

                    time.sleep(delay)

                else:
                    print(
                        f"[AI ROUTER] {model} unavailable after retries."
                    )

        print(f"[AI ROUTER] → Falling back from {model}")

    raise RuntimeError(
        "All configured Gemini models failed after retries."
    ) from last_error
