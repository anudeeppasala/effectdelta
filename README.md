# EffectDelta

Blast-radius **policy gate** for high-impact actions. Compares what the human asked for vs what is about to happen, then allow / ask a human / block.

**In this repo:** a Python library with numeric rules (cardinality, destination, amount). Demos: 1 vs 5,000 email recipients; $50 vs $5,000 transfer. This is not an IAM console replacement.

**Cloud analogue:** same pattern as IAM conditions, SCPs, and change tickets. Sit this check in front of `terraform apply`, a deploy, SES send, or a Step Functions state so a plan larger than what was approved cannot proceed.

Gate **any action** (email, SQL, banking, media publish, code changes) by comparing:

1. **What the human asked for** → Intent Effect Vector  
2. **What is about to happen** → Proposed Effect Vector  
3. **The difference (delta)** → allow / ask human / block

This is not “ask an LLM if it feels unsafe.”  
It measures blast radius with numbers, then applies **your rules**.

## 30-second demo

```bash
pip install -e ".[dev]"
python examples/full_demo.py
```

Example outcome:

```text
User asked: Send report to John          → 1 recipient
AI proposed: email all@company.com       → 5000 recipients
Delta: 4999                              → BLOCK
```

## Install

```bash
pip install -e .
```

## Quick start

```python
from effectdelta import Action, Gate, Rule

gate = Gate(rules=[
    Rule(name="cardinality", max_cardinality_ratio=2.0, on_breach="block"),
    Rule(name="destination", forbid_destination_mismatch=True, on_breach="approve"),
])

decision = gate.check(Action(
    intent="Send this report to John",
    kind="send_email",
    payload={"to": "all@company.com"},
))

print(decision.verdict)  # block
print(decision.deltas.cardinality_ratio)  # 5000.0
```

## Works beyond email

| Kind | Example intent | Dangerous proposal |
|------|----------------|--------------------|
| `send_email` | to John | `all@company.com` (5000 people) |
| `bank_transfer` | Transfer $50 to Alice | amount `5000` |
| `media_publish` | draft to editors | channel `live` to 50k subscribers |
| `sql` | delete user id 42 | `DELETE FROM users` (no WHERE) |
| `file` | delete one log | `data/**` |
| `code_change` | Settings dark mode only | 40-file redesign |

### Banking / media companies

Ship your own adapter (plugin) for internal systems. The core Gate stays the same; you teach EffectDelta how to forecast *your* action’s blast radius.

### Cursor / feature enhancement (manual call)

The library does not inject itself into the IDE. You (or a script) call it before accepting a large AI change:

```python
from effectdelta import check_action, Gate, Rule

gate = Gate(rules=[
    Rule(name="scope", max_scope_files_delta=5, on_breach="block"),
])

decision = check_action(
    intent="Add dark mode toggle on Settings page only",
    kind="code_change",
    payload={
        "files_changed": ["src/design-system/a.tsx", "...40 files..."],
        "diff_summary": "refactor entire design system",
    },
    gate=gate,
)
decision.raise_if_blocked()
```

See `examples/cursor_feature_check.py`.

### Wrap any Python function

```python
from effectdelta import wrap_action, ActionBlocked

@wrap_action(
    "send_email",
    intent="Send this report to John",
    payload_from_args=lambda to, **kw: {"to": to},
)
def send_email(to: str) -> None:
    ...

try:
    send_email("all@company.com")
except ActionBlocked as exc:
    print(exc.decision.reason)
```

## How it works

```text
Human intent ──► Intent Effect Vector ──┐
                                        ├──► DeltaScorer ──► Rules ──► allow|approve|block
Proposed action ► Domain Adapter Probe ─┘
```

Adapters perform **non-mutating probes** (resolve mailing lists, estimate SQL row counts, expand file globs, measure diff scope) *before* the real side effect runs.

## Development

```bash
pip install -e ".[dev]"
pytest -q
python examples/full_demo.py
```

## License

MIT
