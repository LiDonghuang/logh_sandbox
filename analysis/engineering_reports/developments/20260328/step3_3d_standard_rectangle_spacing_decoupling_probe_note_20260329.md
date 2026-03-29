# Step 3 3D Standard Rectangle Spacing Decoupling Probe Note

- Engine Version: `dev_v2.0`
- Modified Layer: `analysis / probe record only`
- Affected Parameters: none in committed runtime
- New Variables Introduced: none
- Cross-Dimension Coupling: none
- Mapping Impact: none
- Governance Impact: records a bounded probe result for future spacing-line review
- Backward Compatible: yes
- Summary: a small harness-local decoupling probe strongly suggests that the current overloaded low-level spacing radius is a major amplifier in the early standard-rectangle stretching problem

## Purpose

This note records one bounded, harness-local decoupling probe following the earlier standard-rectangle root-cause read.

The goal was not to implement a new spacing mechanism.

The goal was only to test whether separating:

- expected / reference formation spacing
- low-level physical separation floor

changes the observed early stretching behavior in a way that is stronger than a plain coupled `min_unit_spacing` sweep.

## Probe Design

Three local probe cases were compared:

1. `coupled_2.0_2.0`
- spawn/reference spacing = `2.0`
- runtime low-level separation floor = `2.0`

2. `decoupled_2.0_1.0`
- spawn/reference spacing = `2.0`
- runtime low-level separation floor = `1.0`

3. `coupled_1.0_1.0`
- spawn/reference spacing = `1.0`
- runtime low-level separation floor = `1.0`

Each case was checked on:

- `aspect_ratio = 1.0`
- `aspect_ratio = 4.0`

Readouts used:

- width/depth ratio over time
- front extent ratio
- expected-position RMS error
- projection pairs / corrected-unit ratio
- rear / middle / front rank forward-slot error
- read-only row-pitch ratio relative to expected slots

## Result

The key result was very strong:

- `coupled_2.0_2.0` still showed the known early stretching
- `decoupled_2.0_1.0` became effectively rigid over the sampled early ticks
- `coupled_1.0_1.0` also became effectively rigid

In the sampled local read:

- `decoupled_2.0_1.0` held:
  - width/depth ratio at `1.0` for `aspect_ratio = 1.0`
  - width/depth ratio at `4.75` for `aspect_ratio = 4.0`
  - front extent ratio at `1.0`
  - expected-position RMS error at `0.0`
  - rear / middle / front forward-slot error at `0.0`

across the sampled early ticks.

## Current Read

This does **not** prove that a future two-layer spacing mechanism should be implemented immediately.

It does, however, support the following stronger engineering read:

- the current overloaded low-level spacing radius is not a minor confounder
- it is a major amplifier, and may be close to the primary operational lever in the present maintained path

At the same time, the result still does **not** justify reading the issue as:

- malformed reference-layout generation
- viewer-only artifact
- legality/projection primary cause

The earlier movement-vs-restore read still stands.

The new point is narrower:

- the maintained path currently appears to entangle expected/reference spacing and low-level physical spacing too strongly

## Bounded Conclusion

The probe supports a future governance discussion line in which:

- expected/reference formation spacing
- low-level physical minimum spacing

may need to be treated as deliberately distinct concepts.

But this note should still be read as:

- diagnostic-first
- harness-local
- pre-implementation

It is not a committed runtime semantics change.
