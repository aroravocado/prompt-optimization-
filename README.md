# Prompt Optimizer for Lower Token Usage

Reduces LLM prompt token usage while preserving intent, via rule-based
cleanup with LLM-based semantic compression planned as the next layer.

## How it works
1. User submits a prompt
2. Rule-based cleanup removes filler/redundant phrasing
3. Token count is compared before/after
4. (Next) LLM rewrite layer for deeper compression

## Tech stack
Python
