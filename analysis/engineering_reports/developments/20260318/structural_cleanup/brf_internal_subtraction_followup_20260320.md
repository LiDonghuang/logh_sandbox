# BRF Internal Subtraction Follow-Up (2026-03-20)

Status: follow-up record  
Scope: `test_run/battle_report_builder.py` internal subtraction only  
Classification: harness-side / report-layer internal cleanup / non-semantic

## 1. Identity

This round did not change BRF feature surface.

It kept the current maintained usage model:

- `test_run/test_run_entry.py` still hands off report export to `test_run/battle_report_builder.py`
- `test_run/brf_narrative_messages.py` remained unchanged
- no BRF semantic slots were removed
- no report assembly logic was copied into launcher code

## 2. What Was Deleted

The following internal helper layers were removed from `test_run/battle_report_builder.py`:

- `_message_exists(...)`
- `_sort_narrative_slots(...)`
- `_build_battle_narrative_semantics(...)`

Resulting simplifications:

- compact-message selection now checks the message table directly inside `_render_narrative_slot(...)`
- narrative slot ordering is now performed directly inside `_build_narrative_body_segments(...)`
- the battle narrative model is now assembled directly in `build_battle_report_markdown(...)`

## 3. Visible Effect

`battle_report_builder.py` line count:

- before this follow-up pass: `1322`
- after this follow-up pass: `1304`

This is a modest reduction, but it is real subtraction:

- fewer internal wrappers
- shorter internal call chain
- no launcher growth to pay for the reduction

## 4. Why This Is Internal Subtraction Instead Of Semantic Shrink

This round did **not**:

- remove BRF sections
- change narrative message semantics
- change narrative slot meaning
- reduce report output surface intentionally

The remaining BRF weight is still report assembly weight, not launcher glue.

Therefore this round should be classified as:

- internal subtraction inside the existing BRF feature surface

not:

- BRF semantic shrink
- BRF active-surface reduction

## 5. Maintained Path Status

The maintained launcher relationship is simpler but unchanged in shape:

- `test_run/test_run_entry.py` still calls `build_battle_report_markdown(...)`
- `battle_report_builder.py` remains the only canonical BRF assembly host
- `test_run/brf_narrative_messages.py` remains the canonical narrative-message host

## 6. Validation

Validation run after this follow-up:

- `python -m py_compile test_run/test_run_entry.py test_run/test_run_scenario.py test_run/test_run_execution.py test_run/battle_report_builder.py test_run/test_run_anchor_regression.py`
- `python test_run/test_run_anchor_regression.py`
- maintained launcher smoke through `test_run/test_run_entry.py`

Observed state:

- routine anchor remained `mismatch_count=0`
- maintained launcher still exported BRF successfully

No runtime semantics changed in this turn.
