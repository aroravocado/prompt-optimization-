"""
optimizer.py
------------
Handles all communication with the Google Gemini API to optimize a
user-supplied prompt so that it uses fewer tokens while preserving:
- intent
- constraints
- context
- expected output

This module is intentionally kept separate from the Streamlit UI code
(app.py) so the logic is modular, testable, and easy to reuse.
"""

import os
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables from a local .env file (if present).
load_dotenv()

# ----------------------------------------------------------------------
# System instruction sent to Gemini. This tells the model exactly how
# to behave when optimizing the user's prompt.
# ----------------------------------------------------------------------
SYSTEM_INSTRUCTION = """Rewrite the following prompt using the minimum number of tokens while preserving:
- intent
- constraints
- context
- expected output

Do not change the meaning.
Do not remove important information.
Return only the optimized prompt. Do not include any explanations,
headers, labels, quotation marks, or markdown formatting - just the
optimized prompt text itself."""


class OptimizerError(Exception):
    """Custom exception raised for any prompt-optimization failure.

    Using a custom exception lets app.py distinguish between
    "expected" errors (missing key, empty prompt, API failure) and
    truly unexpected bugs, so it can show friendly messages.
    """
    pass


def get_api_key() -> str:
    """
    Retrieves the Gemini API key from environment variables.

    Returns:
        str: The API key.

    Raises:
        OptimizerError: If the API key is missing.
    """
    api_key = os.getenv("GEMINI_API_KEY")
    if not api_key or not api_key.strip():
        raise OptimizerError(
            "Gemini API key not found. Please add GEMINI_API_KEY to your "
            ".env file. See .env.example for the required format."
        )
    return api_key


def configure_gemini():
    """
    Configures the Gemini client with the API key from the environment.

    Raises:
        OptimizerError: If configuration fails (e.g. missing key).
    """
    api_key = get_api_key()
    genai.configure(api_key=api_key)


def optimize_prompt(original_prompt: str, model_name: str = "gemini-1.5-flash") -> str:
    """
    Sends the original prompt to Gemini and returns the optimized
    (token-reduced) version.

    Args:
        original_prompt (str): The prompt the user wants optimized.
        model_name (str): Which Gemini model to use. Defaults to the
            fast, cost-efficient "gemini-1.5-flash" model, which is
            ideal for a quick hackathon demo.

    Returns:
        str: The optimized prompt text.

    Raises:
        OptimizerError: For empty input, missing API key, or any
            failure while calling the Gemini API (auth errors,
            network errors, rate limits, etc.).
    """
    # --- Validate input -------------------------------------------------
    if not original_prompt or not original_prompt.strip():
        raise OptimizerError("Please enter a prompt before optimizing.")

    # --- Configure Gemini (raises OptimizerError if key is missing) -----
    configure_gemini()

    try:
        # Create the generative model with our system instruction baked
        # in, so every call follows the same optimization rules.
        model = genai.GenerativeModel(
            model_name=model_name,
            system_instruction=SYSTEM_INSTRUCTION,
        )

        # Ask Gemini to optimize the prompt. Low temperature keeps the
        # output focused and deterministic rather than "creative".
        response = model.generate_content(
            original_prompt,
            generation_config=genai.types.GenerationConfig(
                temperature=0.2,
                max_output_tokens=2048,
            ),
        )

        optimized_text = (response.text or "").strip()

        if not optimized_text:
            raise OptimizerError(
                "Gemini returned an empty response. Please try again."
            )

        return optimized_text

    except OptimizerError:
        # Re-raise our own errors unchanged.
        raise
    except Exception as exc:
        # Wrap any Gemini/network/library exception in a friendly
        # OptimizerError so app.py can display it cleanly.
        raise OptimizerError(f"Failed to optimize prompt: {exc}") from exc
