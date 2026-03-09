# Parameter Scale Normalization v1.0

Status: Active  
Scope: Canonical 1-9 parameter normalization  
Authority Context: Post-replacement stabilization

## Canonical Interpretation

The active personality scale is:

```text
1 .. 9
```

with:

- `1` = low pole
- `5` = midpoint
- `9` = high pole

This normalization pass does not change archetype ordering or semantic meaning.

It only removes remaining code-level assumptions that still behaved as if the old domain extended to `10`.

## Code Updates

### 1. `runtime/runtime_v0_1.py`

The active normalization helper now matches the canonical scale:

```text
normalized = (value - 1) / 8
domain check = [1, 9]
```

This replaced the stale helper that still used:

```text
(value - 1) / 9
domain [1, 10]
```

As a result, canonical endpoints now map correctly:

- `1 -> 0.0`
- `5 -> 0.5`
- `9 -> 1.0`

### 2. `runtime/engine_skeleton.py`

The direct `mobility_bias` mapping in movement was updated from the old scale assumption:

```text
MB_eff = 0.2 * (mobility_bias - 5) / 5
```

to the canonical 1-9 interpretation:

```text
MB_eff = 0.2 * (mobility_bias - 5) / 4
```

with the same final clip:

```text
[-0.2, +0.2]
```

This keeps midpoint semantics unchanged while restoring full endpoint reach under the 1-9 scale.

## Data Confirmation

`archetypes/archetypes_v1_5.json` was checked against the active ten-parameter keys.

Result:

- minimum value = `1.0`
- maximum value = `9.0`
- out-of-range entries = `0`

So the remaining normalization work was code-level, not data-level.

## Semantics Preserved

This pass does not:

- reorder archetypes
- reinterpret personality dimensions
- rewrite historical reports
- introduce new runtime mechanisms

The intent is normalization, not redesign.

## Explicit Non-Goal

This pass does not correct pre-existing runtime paths that are outside the narrow normalization target.

Example:

- combat currently reads `UnitState.offense_defense_weight`
- `build_initial_state(...)` does not yet inject archetype ODW into `UnitState`

That is a separate runtime semantics issue and was intentionally left untouched in this stabilization pass.

## Effect on Runtime Behavior

A small amount of behavior drift is expected because normalized endpoints now align exactly with the canonical 1-9 domain.

This drift is accepted as part of normalization and was checked through a lightweight post-replacement signal audit.
