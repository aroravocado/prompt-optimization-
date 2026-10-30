"""
token_counter.py
-----------------
Utility module for counting tokens in a piece of text and estimating
the dollar cost of those tokens (based on GPT-4 pricing) as well as
the cost saved when a prompt is optimized.

Uses OpenAI's `tiktoken` library, which is a fast, offline tokenizer.
Even though this project uses Gemini for the actual optimization,
tiktoken is used here purely as a consistent, well-known token
counting standard so users can estimate GPT-4-equivalent costs.
"""

import tiktoken


# ----------------------------------------------------------------------
# Pricing constants (USD per 1,000 tokens) - based on public GPT-4
# pricing at the time of writing. Feel free to tweak these values.
# ----------------------------------------------------------------------
GPT4_INPUT_COST_PER_1K = 0.03   # $0.03 / 1K input tokens
GPT4_OUTPUT_COST_PER_1K = 0.06  # $0.06 / 1K output tokens

# We use the average of input/output pricing for a simple, single
# "cost per token" estimate since we don't split prompt vs completion.
AVERAGE_COST_PER_1K = (GPT4_INPUT_COST_PER_1K + GPT4_OUTPUT_COST_PER_1K) / 2


def get_encoder():
    """
    Returns a tiktoken encoder.

    We use the 'cl100k_base' encoding, which is the encoding used by
    GPT-4 and GPT-3.5-turbo models. This keeps our token counts
    consistent and realistic for cost estimation purposes.
    """
    try:
        return tiktoken.get_encoding("cl100k_base")
    except Exception:
        # Fallback in case the encoding name changes in future tiktoken
        # versions - default to the encoding for a common model.
        return tiktoken.encoding_for_model("gpt-4")


# Create a single encoder instance to reuse (faster than re-creating it
# every time count_tokens() is called).
_ENCODER = get_encoder()


def count_tokens(text: str) -> int:
    """
    Counts the number of tokens in the given text using tiktoken.

    Args:
        text (str): The text to tokenize.

    Returns:
        int: Number of tokens. Returns 0 for empty/None text.
    """
    if not text or not text.strip():
        return 0

    tokens = _ENCODER.encode(text)
    return len(tokens)


def calculate_savings(original_text: str, optimized_text: str) -> dict:
    """
    Calculates a full statistics dictionary comparing the original and
    optimized prompt.

    Args:
        original_text (str): The user's original prompt.
        optimized_text (str): The AI-optimized prompt.

    Returns:
        dict: {
            "original_tokens": int,
            "optimized_tokens": int,
            "tokens_saved": int,
            "reduction_percent": float,
            "estimated_cost_original": float,
            "estimated_cost_optimized": float,
            "estimated_cost_saved": float,
        }
    """
    original_tokens = count_tokens(original_text)
    optimized_tokens = count_tokens(optimized_text)

    tokens_saved = max(original_tokens - optimized_tokens, 0)

    # Avoid division by zero when the original prompt is empty.
    if original_tokens > 0:
        reduction_percent = (tokens_saved / original_tokens) * 100
    else:
        reduction_percent = 0.0

    estimated_cost_original = (original_tokens / 1000) * AVERAGE_COST_PER_1K
    estimated_cost_optimized = (optimized_tokens / 1000) * AVERAGE_COST_PER_1K
    estimated_cost_saved = estimated_cost_original - estimated_cost_optimized

    return {
        "original_tokens": original_tokens,
        "optimized_tokens": optimized_tokens,
        "tokens_saved": tokens_saved,
        "reduction_percent": round(reduction_percent, 2),
        "estimated_cost_original": round(estimated_cost_original, 6),
        "estimated_cost_optimized": round(estimated_cost_optimized, 6),
        "estimated_cost_saved": round(estimated_cost_saved, 6),
    }
