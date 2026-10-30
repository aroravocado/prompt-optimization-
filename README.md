# Prompt Optimizer

An AI-powered prompt optimization application built with Python, Streamlit, and Google's Gemini API.

## Overview

Prompt Optimizer helps users rewrite lengthy or repetitive prompts into more concise versions while aiming to preserve their original intent, context, and constraints.

The application compares the original and optimized prompts and displays estimated token savings.

## Features

- AI-assisted prompt optimization using Gemini
- Token counting with `tiktoken`
- Before-and-after prompt comparison
- Estimated token reduction and percentage savings
- Illustrative API cost-savings estimates
- Interactive Streamlit interface
- Option to export optimized prompts

## Tech Stack

- **Language:** Python
- **Frontend:** Streamlit
- **AI Integration:** Google Gemini API
- **Libraries:** tiktoken, python-dotenv, google-generativeai

## How It Works

1. The user enters an original prompt.
2. The application sends the prompt to Gemini with optimization instructions.
3. Gemini generates a more concise version.
4. The application calculates token counts for both versions.
5. The interface displays the optimized prompt and estimated savings.

## Installation

Clone the repository and install the dependencies:

```bash
git clone https://github.com/aroravocado/prompt-optimization-.git
cd prompt-optimization-
pip install -r requirements.txt
```

Create a `.env` file based on `.env.example` and add your Gemini API key:

```env
GEMINI_API_KEY=your_api_key_here
```

Run the application:

```bash
streamlit run app.py
```

## Limitations

- Optimized prompts may not always produce equivalent model responses.
- Token counts are estimates based on the selected tokenizer.
- Cost savings are illustrative estimates, not actual Gemini billing.
- The application requires a valid Gemini API key and internet access.

## Future Improvements

- Support for multiple AI models
- Automated evaluation of output quality
- Additional prompt optimization strategies
- Detailed token usage analytics

## Project Context

Developed as a hackathon project exploring ways to reduce prompt token usage while maintaining useful instructions and context.
