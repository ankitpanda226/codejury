# CodeJury

CodeJury is a jury-style multi-agent code review system that combines LLM reasoning, rule-based verifiers, and runtime execution checks to evaluate code across common interview-style programming problems.

## Overview

Traditional prompt-only code review can produce convincing but incorrect judgments. CodeJury improves reliability by combining multiple layers of evidence:

- problem classification
- specialized review agents
- pattern-specific verifiers
- runtime execution checks
- weighted voting
- safety veto logic

The system is designed to review common coding interview solutions such as two-sum, binary search, palindrome checking, max subarray, and related algorithmic patterns.

## Features

- Multi-agent review with specialized jurors for:
  - Correctness
  - Edge Cases
  - Complexity
  - Code Quality
  - Bug Hunting
- Problem classifier for routing solutions into known categories
- Pattern-specific verifiers for categories like:
  - `two_sum`
  - `binary_search`
  - `palindrome_string`
  - `max_subarray`
  - `sliding_window`
  - `linked_list`
  - `tree`
  - `graph`
  - `heap`
  - `interval`
  - `dp`
  - `backtracking`
  - `matrix`
  - `generic_array_search`
- Runtime execution checks for supported categories
- Weighted voting across jurors
- Safety veto logic when verifier/runtime evidence finds likely bugs
- Deliberation history across multiple rounds
- Exportable JSON review reports
- Optional Ollama-backed jurors with fallback behavior

## Why this project

Prompt-only AI code review often struggles with:

- hallucinated bug reports
- weak edge-case reasoning
- overconfidence on incorrect code
- lack of hard evidence

CodeJury explores a hybrid approach where LLM-based reasoning is combined with:

- deterministic verifier checks
- runtime testing
- structured final judgment

## Architecture

```text
User Input
   ↓
Problem Classifier
   ↓
Category-Specific Verifier
   ↓
Runtime Execution Runner
   ↓
Specialized Jurors
   ├── Correctness
   ├── Edge Cases
   ├── Complexity
   ├── Code Quality
   └── Bug Hunting
   ↓
Judge Agent
   ├── Weighted Voting
   ├── Safety Veto
   └── Final Verdict
```

## Tech Stack

- Python
- Streamlit
- Ollama
- Rule-based verifiers
- Runtime execution runner
- JSON-based structured outputs

## Project Structure

```text
codejury/
├── app.py
├── requirements.txt
├── agents/
│   ├── base.py
│   ├── bug_hunter.py
│   ├── code_quality.py
│   ├── complexity.py
│   ├── correctness.py
│   ├── edge_cases.py
│   └── problem_classifier.py
├── models/
│   └── schemas.py
├── orchestrator/
│   └── judge.py
├── utils/
│   ├── ollama_client.py
│   └── signals.py
└── verifiers/
    ├── backtracking.py
    ├── base.py
    ├── binary_search.py
    ├── dp.py
    ├── generic.py
    ├── generic_array_search.py
    ├── graph.py
    ├── heap.py
    ├── interval.py
    ├── linked_list.py
    ├── matrix.py
    ├── max_subarray.py
    ├── palindrome_string.py
    ├── python_runner.py
    ├── registry.py
    ├── sliding_window.py
    ├── tree.py
    └── two_sum.py
```

## How It Works

1. The user provides a problem statement and candidate code.
2. A classifier predicts the problem category.
3. A category-specific verifier checks for common implementation mistakes.
4. A runtime runner executes supported solutions on sample tests.
5. Multiple jurors analyze the code from different perspectives.
6. A judge combines jury votes with verifier/runtime evidence.
7. The app returns:
   - final verdict
   - confidence
   - majority reasons
   - minority reasons
   - recommended improvements
   - deliberation history

## Example Supported Scenarios

- Accepting a correct brute-force two-sum solution
- Accepting a correct hashmap two-sum solution
- Accepting a correct binary search implementation
- Revising a binary search solution with non-progressing bounds
- Revising or rejecting obviously wrong solutions
- Using runtime failures as strong evidence in the final verdict

## Running Locally

### 1. Create and activate a virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 2. Install dependencies

```bash
pip install -r requirements.txt
```

### 3. Start the app

```bash
streamlit run app.py
```

### 4. Optional: enable Ollama-backed jurors

```bash
ollama pull llama3.2
```


## License

MIT
