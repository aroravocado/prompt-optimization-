"""
app.py
------
Main Streamlit application for "Prompt Optimizer for Lower Token Usage".

This app lets a user paste in a long AI prompt, optimizes it using the
Google Gemini API to reduce token usage while preserving meaning, and
displays before/after statistics (tokens, cost, reduction %) in a
polished, hackathon-ready UI.

Run with:
    streamlit run app.py
"""

import streamlit as st

from optimizer import optimize_prompt, OptimizerError, get_api_key
from token_counter import calculate_savings


# ============================================================================
# PAGE CONFIG
# ============================================================================
st.set_page_config(
    page_title="Prompt Optimizer | Lower Token Usage",
    page_icon="⚡",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ============================================================================
# SAMPLE PROMPTS
# Pre-written example prompts users can click to auto-fill the textbox.
# ============================================================================
SAMPLE_PROMPTS = {
    "💻 Coding": (
        "I want you to act as a senior Python software engineer. Please "
        "write a complete, well-documented Python function that takes a "
        "list of integers as input and returns a new list containing only "
        "the even numbers from the original list, sorted in ascending "
        "order. Make sure to include docstrings, type hints, inline "
        "comments explaining the logic, and handle edge cases such as "
        "empty lists or lists containing non-integer values gracefully. "
        "Also provide a few example usages at the bottom of the code so "
        "that I can understand how to call the function correctly."
    ),
    "🗄️ SQL": (
        "You are an expert database administrator with many years of "
        "experience writing optimized SQL queries. I have a table called "
        "'orders' with columns order_id, customer_id, order_date, and "
        "total_amount, and another table called 'customers' with columns "
        "customer_id, customer_name, and country. Please write a SQL "
        "query that returns the total amount spent by each customer, "
        "grouped by country, only including customers who have spent "
        "more than 1000 in total, and sort the results by total amount "
        "spent in descending order. Please also explain what each part "
        "of the query does in simple terms."
    ),
    "📄 Resume": (
        "I would like you to act as a professional resume writer and "
        "career coach. Please help me rewrite my work experience bullet "
        "points to make them more impactful and results-oriented, using "
        "strong action verbs and quantifiable achievements wherever "
        "possible. I currently have five years of experience working as "
        "a marketing manager at a mid-sized technology company, where I "
        "led a team of four people, managed a budget of $200,000 per "
        "year, and was responsible for increasing website traffic and "
        "lead generation through digital marketing campaigns."
    ),
    "✉️ Email": (
        "Please act as a professional business communication expert. I "
        "need you to help me write a polite but firm follow-up email to "
        "a client who has not responded to my previous two emails about "
        "an overdue invoice payment. The email should remind them of the "
        "outstanding amount, mention the original due date, request "
        "prompt payment, and offer to discuss a payment plan if they are "
        "experiencing difficulties, while maintaining a professional and "
        "respectful tone throughout the entire message."
    ),
    "🎧 Customer Support": (
        "You are a helpful and empathetic customer support agent working "
        "for an e-commerce company. A customer has written in saying "
        "that they received a damaged product in their last order and "
        "they are frustrated because this is the second time this has "
        "happened. Please write a response that acknowledges their "
        "frustration, apologizes sincerely for the inconvenience, "
        "explains that a replacement will be shipped immediately at no "
        "extra cost, and offers a discount code for their next purchase "
        "as a gesture of goodwill, while keeping the tone warm and "
        "genuinely caring."
    ),
}


# ============================================================================
# SESSION STATE INITIALIZATION
# Streamlit re-runs the whole script on every interaction, so we use
# st.session_state to persist values (like the prompt text and results)
# across reruns.
# ============================================================================
if "prompt_text" not in st.session_state:
    st.session_state.prompt_text = ""

if "results" not in st.session_state:
    st.session_state.results = None  # Will hold dict with optimization results


def fill_sample(sample_text: str):
    """Callback used by sample prompt buttons to populate the textbox."""
    st.session_state.prompt_text = sample_text


def clear_all():
    """Callback for the Clear button - resets prompt and results."""
    st.session_state.prompt_text = ""
    st.session_state.results = None


# ============================================================================
# CUSTOM CSS - dark theme, gradient title, professional card styling
# ============================================================================
CUSTOM_CSS = """
<style>
    /* Overall app background */
    .stApp {
        background: radial-gradient(circle at top left, #1a1a2e 0%, #0f0f1a 60%, #0a0a12 100%);
        color: #e6e6f0;
    }

    /* Gradient title */
    .gradient-title {
        font-size: 3rem;
        font-weight: 800;
        background: linear-gradient(90deg, #7F5AF0, #2CB67D, #FF7676);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 0px;
        padding-bottom: 0px;
    }

    .subtitle {
        color: #a0a0b8;
        font-size: 1.05rem;
        margin-top: 4px;
        margin-bottom: 1.5rem;
    }

    /* Card container */
    .custom-card {
        background: rgba(255, 255, 255, 0.04);
        border: 1px solid rgba(127, 90, 240, 0.25);
        border-radius: 16px;
        padding: 1.4rem 1.6rem;
        margin-bottom: 1rem;
        box-shadow: 0 4px 24px rgba(0,0,0,0.25);
    }

    .section-header {
        font-size: 1.3rem;
        font-weight: 700;
        color: #ffffff;
        margin-bottom: 0.6rem;
    }

    /* Badge */
    .badge {
        display: inline-block;
        padding: 4px 12px;
        border-radius: 999px;
        font-size: 0.75rem;
        font-weight: 700;
        letter-spacing: 0.03em;
        margin-right: 6px;
    }
    .badge-purple { background: rgba(127, 90, 240, 0.2); color: #b9a2fb; border: 1px solid #7F5AF0; }
    .badge-green { background: rgba(44, 182, 125, 0.15); color: #6fe3b4; border: 1px solid #2CB67D; }
    .badge-orange { background: rgba(255, 118, 118, 0.15); color: #ffb3b3; border: 1px solid #FF7676; }

    /* Buttons */
    div.stButton > button {
        border-radius: 10px;
        font-weight: 600;
        border: 1px solid rgba(127, 90, 240, 0.4);
        transition: all 0.2s ease-in-out;
    }
    div.stButton > button:hover {
        border-color: #7F5AF0;
        color: #ffffff;
        background-color: rgba(127, 90, 240, 0.15);
    }

    /* Text areas */
    textarea {
        border-radius: 12px !important;
    }

    /* Footer */
    .footer-note {
        text-align: center;
        color: #6c6c85;
        font-size: 0.85rem;
        margin-top: 2rem;
    }
</style>
"""

st.markdown(CUSTOM_CSS, unsafe_allow_html=True)


# ============================================================================
# SIDEBAR
# ============================================================================
with st.sidebar:
    st.markdown("### ⚡ Prompt Optimizer")
    st.markdown(
        "Reduce your AI prompt's token usage with Gemini-powered "
        "optimization, without losing meaning or quality."
    )
    st.markdown("---")
    st.markdown("#### 🔑 API Key Status")
    try:
        get_api_key()
        st.success("Gemini API key detected ✅")
    except OptimizerError:
        st.error("No API key found ❌")
        st.caption(
            "Add `GEMINI_API_KEY` to a `.env` file in the project root. "
            "See `.env.example` for the format."
        )
    st.markdown("---")
    st.markdown("#### 📊 How it works")
    st.markdown(
        "1. Paste or select a sample prompt\n"
        "2. Click **Optimize Prompt**\n"
        "3. Gemini rewrites it using fewer tokens\n"
        "4. Compare stats & download the result"
    )
    st.markdown("---")
    st.caption("Built for a 3-hour hackathon ⏱️ with Streamlit + Gemini")


# ============================================================================
# HEADER
# ============================================================================
st.markdown('<div class="gradient-title">⚡ Prompt Optimizer</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Cut your prompt token usage with AI — without losing intent, '
    'context, or output quality.</div>',
    unsafe_allow_html=True,
)


# ============================================================================
# SAMPLE PROMPT BUTTONS
# ============================================================================
st.markdown('<div class="section-header">✨ Try a Sample Prompt</div>', unsafe_allow_html=True)
sample_cols = st.columns(len(SAMPLE_PROMPTS))
for col, (label, text) in zip(sample_cols, SAMPLE_PROMPTS.items()):
    with col:
        st.button(
            label,
            key=f"sample_{label}",
            use_container_width=True,
            on_click=fill_sample,
            args=(text,),
        )

st.write("")  # spacing


# ============================================================================
# SECTION 1: PROMPT INPUT
# ============================================================================
st.markdown('<div class="section-header">📝 Paste your Prompt</div>', unsafe_allow_html=True)

prompt_input = st.text_area(
    label="Prompt input",
    key="prompt_text",
    height=220,
    placeholder="Paste your long AI prompt here...",
    label_visibility="collapsed",
)


# ============================================================================
# SECTION 2: ACTION BUTTONS (Optimize / Clear)
# ============================================================================
action_col1, action_col2, _ = st.columns([1, 1, 4])

with action_col1:
    optimize_clicked = st.button("🚀 Optimize Prompt", type="primary", use_container_width=True)

with action_col2:
    st.button("🗑️ Clear", on_click=clear_all, use_container_width=True)


# ============================================================================
# HANDLE OPTIMIZE BUTTON CLICK
# ============================================================================
if optimize_clicked:
    current_prompt = st.session_state.prompt_text

    if not current_prompt or not current_prompt.strip():
        st.warning("⚠️ Please enter a prompt before optimizing.")
    else:
        with st.spinner("🤖 Optimizing your prompt with Gemini..."):
            try:
                optimized = optimize_prompt(current_prompt)
                stats = calculate_savings(current_prompt, optimized)
                st.session_state.results = {
                    "original": current_prompt,
                    "optimized": optimized,
                    "stats": stats,
                }
                st.success("✅ Prompt optimized successfully!")
            except OptimizerError as e:
                # Friendly, expected errors (missing key, empty prompt,
                # API/network failures) are shown as clean messages.
                st.error(f"❌ {e}")
            except Exception as e:
                # Catch-all for anything truly unexpected.
                st.error(f"❌ An unexpected error occurred: {e}")


# ============================================================================
# SECTION 3: RESULTS
# ============================================================================
if st.session_state.results:
    results = st.session_state.results
    stats = results["stats"]

    st.markdown("---")
    st.markdown('<div class="section-header">📊 Results</div>', unsafe_allow_html=True)

    # --- Badges summarizing the outcome ---
    st.markdown(
        f'<span class="badge badge-purple">TOKENS SAVED: {stats["tokens_saved"]}</span>'
        f'<span class="badge badge-green">REDUCTION: {stats["reduction_percent"]}%</span>'
        f'<span class="badge badge-orange">COST SAVED: ${stats["estimated_cost_saved"]}</span>',
        unsafe_allow_html=True,
    )
    st.write("")

    # --- Side-by-side prompt comparison ---
    col_orig, col_opt = st.columns(2)

    with col_orig:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("**📄 Original Prompt**")
        st.text_area(
            "Original prompt output",
            value=results["original"],
            height=220,
            disabled=True,
            label_visibility="collapsed",
            key="original_display",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    with col_opt:
        st.markdown('<div class="custom-card">', unsafe_allow_html=True)
        st.markdown("**⚡ Optimized Prompt**")
        st.text_area(
            "Optimized prompt output",
            value=results["optimized"],
            height=220,
            disabled=True,
            label_visibility="collapsed",
            key="optimized_display",
        )
        st.markdown("</div>", unsafe_allow_html=True)

    st.write("")

    # --- Metrics row ---
    st.markdown('<div class="custom-card">', unsafe_allow_html=True)
    m1, m2, m3, m4 = st.columns(4)
    m1.metric("Original Tokens", stats["original_tokens"])
    m2.metric("Optimized Tokens", stats["optimized_tokens"])
    m3.metric("Tokens Saved", stats["tokens_saved"], delta=f"-{stats['reduction_percent']}%")
    m4.metric("Estimated Cost Saved", f"${stats['estimated_cost_saved']}")

    st.write("")
    st.markdown("**Reduction Progress**")
    # Progress bar visually shows how much smaller the optimized prompt is.
    progress_value = min(max(stats["reduction_percent"] / 100, 0.0), 1.0)
    st.progress(progress_value, text=f"{stats['reduction_percent']}% smaller")
    st.markdown("</div>", unsafe_allow_html=True)

    # --- Detailed cost breakdown (expander) ---
    with st.expander("💰 Detailed Cost Breakdown (GPT-4 equivalent pricing)"):
        st.write(f"**Estimated cost (original prompt):** ${stats['estimated_cost_original']}")
        st.write(f"**Estimated cost (optimized prompt):** ${stats['estimated_cost_optimized']}")
        st.write(f"**Estimated cost saved per request:** ${stats['estimated_cost_saved']}")
        st.caption(
            "Cost estimates use an average of GPT-4 input ($0.03/1K tokens) "
            "and output ($0.06/1K tokens) pricing, applied via tiktoken's "
            "cl100k_base tokenizer. Actual savings scale with your request "
            "volume — e.g. at 10,000 requests/month, this becomes "
            f"${round(stats['estimated_cost_saved'] * 10000, 2)}."
        )

    st.write("")

    # ========================================================================
    # SECTION 4: COPY / DOWNLOAD / CLEAR
    # ========================================================================
    st.markdown('<div class="section-header">📥 Export</div>', unsafe_allow_html=True)
    export_col1, export_col2, export_col3 = st.columns(3)

    with export_col1:
        # True one-click "copy to clipboard" isn't natively supported by
        # Streamlit, so we show the text in a code block which has a
        # built-in copy icon on hover - a simple, reliable workaround.
        st.markdown("**📋 Copy Optimized Prompt**")
        st.code(results["optimized"], language=None)

    with export_col2:
        st.markdown("**⬇️ Download**")
        st.download_button(
            label="Download optimized_prompt.txt",
            data=results["optimized"],
            file_name="optimized_prompt.txt",
            mime="text/plain",
            use_container_width=True,
        )

    with export_col3:
        st.markdown("**🗑️ Reset**")
        st.button(
            "Clear Everything",
            on_click=clear_all,
            use_container_width=True,
            key="clear_bottom",
        )


# ============================================================================
# FOOTER
# ============================================================================
st.markdown(
    '<div class="footer-note">Built with ⚡ Streamlit + Gemini · '
    'Prompt Optimizer for Lower Token Usage</div>',
    unsafe_allow_html=True,
)
