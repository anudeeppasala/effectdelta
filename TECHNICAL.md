# EffectDelta — Technical Disclosure Draft

> Informal invention disclosure for portfolio + optional US provisional filing.
> This is **not** legal advice and is **not** a filed patent application.

## Problem

Autonomous and assisted agents propose actions (tool calls, API calls, code edits) whose **real-world blast radius** can diverge from the human’s stated intent. Existing systems often rely on generic policy middleware or LLM “does this look safe?” judgments, which do not quantitatively compare *wanted* versus *proposed* consequences.

## Proposed method

A computer-implemented method for pre-execution authorization of an action, comprising:

1. Receiving a human intent description and a proposed action descriptor (kind + payload).
2. Deriving an **Intent Effect Vector** with dimensions such as cardinality/scope, targets, amount, channels, irreversibility, sensitivity, and environment.
3. Deriving a **Proposed Effect Vector** using a **non-mutating probe/adapter** appropriate to the action kind (for example: expand a mailing-list address; rewrite mutating SQL into a count estimate; expand filesystem globs; measure code diff file scope; read transfer amount fields).
4. Computing a **Delta Report** of dimensional differences and ratios between the Intent and Proposed vectors.
5. Evaluating user-configured rules against the Delta Report to produce a verdict: allow, require human approval, or block — **before** executing the mutating action.

## Distinguishing points

- Authorization is driven by **quantitative effect deltas**, not solely by an LLM safety classifier.
- Probes forecast consequences **without performing** the irreversible side effect.
- The same gate applies to heterogeneous action kinds through pluggable adapters (communications, data stores, payments, publishing, and source-code changes).
- Rules are threshold policies over deltas (ratios, absolute deltas, mismatch flags), enabling enterprise-specific governance.

## Example claim-style statement (illustrative)

A method comprising: constructing an intent effect vector from a natural-language request; constructing a proposed effect vector from a tool or action payload via a non-executing probe; computing cardinality and destination deltas between said vectors; and preventing execution of the action when a configured cardinality ratio threshold is exceeded.

## Embodiment notes

Reference implementation: Python package `effectdelta` (this repository), including adapters for `send_email`, `sql`, `file`, `bank_transfer`, `media_publish`, and `code_change`, plus `Gate`, `Rule`, `wrap_action`, and `check_action` APIs.

## Filing checklist (when ready)

1. Freeze a tagged release of this repo as supporting material.
2. File US provisional with micro-entity fees (confirm eligibility).
3. Within 12 months, decide on non-provisional / PCT with patent counsel.
4. Only then add “US provisional patent pending” to a resume.
