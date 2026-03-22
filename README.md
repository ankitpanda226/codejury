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
  - two_sum
  - binary_search
  - palindrome_string
  - max_subarray
  - sliding_window
  - linked_list
  - tree
  - graph
  - heap
  - interval
  - dp
  - backtracking
  - matrix
- Runtime execution checks for supported categories
- Weighted voting across jurors
- Safety veto logic when verifier/runtime evidence finds likely bugs
- Deliberation history across multiple rounds
- Exportable JSON review reports

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
