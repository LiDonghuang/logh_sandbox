# Baseline Replacement Protocol v1.0

LOGH Fleet Sandbox

Status: Active  
Authority: Governance Core  
Applicable Scope: Mechanism Replacement  
Protocol Compatibility: Sandbox_CrossThread_Protocol_v1.2

---

## I. Purpose

This protocol governs the replacement of baseline mechanisms within the sandbox.

It applies when Engineering proposes replacing a current baseline mechanism with a new one.

Typical examples include:
- movement model replacement
- cohesion mechanism replacement
- collapse logic replacement
- event detection threshold replacement
- observer/report semantics replacement

The objective is to ensure:
- structural clarity
- deterministic reproducibility
- stable semantics
- minimal governance overhead

This protocol is intentionally lightweight.

---

## II. What Counts as a Baseline Replacement

A replacement occurs when the default mechanism used by normal runtime or reporting changes.

Examples:

`movement v1 -> movement v3`  
`cohesion v2 -> cohesion v3`  
`Channel-T threshold set A -> threshold set B`  
`observer semantics old -> observer semantics new`

This protocol does not apply to:
- experimental branches
- temporary probes
- diagnostic instrumentation
- local engineering trials

Only mechanisms proposed as default behavior trigger this protocol.

---

## III. Replacement Philosophy

The sandbox evolves through the following cycle:

`experiment -> compare -> validate -> replace`

Baseline changes must never occur through silent drift.

Principle:

`No silent baseline drift.`

Every replacement must be explicitly recorded.

---

## IV. Engineering Autonomy Before Gate

Engineering may freely perform:
- candidate mechanism design
- parameter exploration
- DOE experiments
- diagnostic instrumentation
- exploratory validation runs

Governance is engaged only when Engineering believes a candidate is ready for baseline evaluation.

This maintains rapid engineering iteration.

---

## V. Gate Entry Conditions

A candidate mechanism may enter replacement evaluation when four conditions are met.

### 1. Candidate Configuration Frozen

Engineering must specify the exact candidate configuration.

Example:

```text
movement_model = v3a
centroid_probe_scale = 0.5
bridge_theta_split = 1.7
bridge_theta_env = 0.5
```

During evaluation:
- parameters should be treated as frozen
- micro-tuning should stop unless structural defects appear

### 2. Paired Comparison Exists

Evaluation must compare:

`current baseline`  
vs  
`candidate mechanism`

Runs should share:
- identical seeds
- identical scenarios
- identical opponents
- identical reporting configuration

Paired comparison is mandatory.

Detailed seed discipline and execution details may evolve and should be maintained in engineering standards rather than duplicated here.

### 3. Structural Scope Declared

Engineering must explicitly declare the affected system layer.

Example:

`Modified Layer: Movement`

Engineering must state whether the change affects:
- formation geometry
- contact timing
- event detection
- collapse interpretation
- observer/report semantics

This prevents mechanism changes from being misinterpreted as bug fixes.

### 4. Cross-Layer Boundaries Remain Clear

If the candidate also changes another system layer, the replacement becomes:

`multi-layer replacement`

and should be treated with additional caution.

Single-layer replacements remain preferred.

If a proposed threshold replacement is evaluated together with changes in movement, cohesion, collapse, or observer metric source, it is not a pure threshold replacement and must be treated as a multi-layer replacement.

---

## VI. Minimal Evaluation Checklist

Engineering evaluation reports should remain concise.

The following checklist is sufficient.

### A. Behavioral Improvement

Does the candidate solve the motivating problem?

Example:
- persistent outlier reduction
- pre-contact formation stability improvement

### B. Event Integrity

Event detection must remain valid.

Expected structure:

`First Contact -> Formation Cut -> Pocket Formation -> Endgame`

Events must remain detectable and ordered.

### C. Determinism and Stability

Confirm:
- determinism preserved
- mirror symmetry stable
- no severe jitter regression

### D. Semantic Continuity

Parameter meanings must remain consistent.

Reporting language must not misrepresent runtime decisions.

---

## VII. Governance Decision Classes

Governance decisions fall into four categories.

`ACCEPT`

Candidate becomes the new baseline.

`ACCEPT-WITH-NOTE`

Candidate becomes baseline with recorded limitations.

`HOLD`

Candidate promising but not yet ready.

Engineering may continue limited exploration.

`REJECT`

Candidate unsuitable as baseline.

Mechanism remains experimental.

---

## VIII. Working Default vs Runtime Baseline

Two states are distinguished.

### Working Default

The mechanism used by Engineering as the preferred configuration during development.

### Runtime Baseline

The officially recognized system default.

Working default may precede runtime baseline declaration.

This allows stabilization without premature hard commits.

---

## IX. Baseline Clean-Up Rule

To maintain long-term code clarity, mechanism replacement requires code clean-up discipline.

When a candidate becomes baseline:

### 1. Old Baseline Leaves Main Execution Path

The previous baseline mechanism must no longer appear in the primary runtime branch.

### 2. Old Baseline Leaves Default Test Paths

The previous baseline should not remain selectable through normal runtime configuration used by humans.

### 3. Documentation Moves to Archive

Old baseline documentation should move to:

`archive/reference`

where it remains available for historical inspection.

### 4. Explicit Decision Record Required

Every accepted replacement must leave a short decision record containing at minimum:
- old baseline
- new baseline
- affected layer
- effective engine version or date
- whether the decision establishes a working default or a runtime baseline

This record is sufficient for future recovery or historical inspection and avoids silent baseline drift.

---

## X. Execution Mode Stability

User-facing execution interfaces should remain stable even as mechanisms evolve.

Example:

`test_mode`

may continue to expose:
- `0` default runtime
- `1` observe runtime
- `2` experimental runtime

However, the mechanisms used internally by these modes may change as baseline replacements occur.

Principle:

`execution interfaces remain stable`  
`mechanism implementations converge`

Detailed mode-specific behavior may evolve and should be maintained in engineering standards rather than duplicated here.

---

## XI. Lightweight Documentation Requirement

Each replacement proposal should produce a short engineering report containing:

- Engine Version
- Modified Layer
- Affected Parameters
- New Variables Introduced
- Cross-Dimension Coupling
- Mapping Impact
- Governance Impact
- Backward Compatibility
- Summary (<=15 lines)

No large governance packets are required.

---

## XII. Special Rule for Threshold Replacement

Threshold replacements should prioritize:
- semantic clarity
- event preservation
- stable detection

rather than numerical curve fitting.

Thresholds define event meaning, not optimization surfaces.

If threshold changes alter the meaning of the underlying metric source or are evaluated together with changes in another layer, the proposal must be treated as a broader mechanism replacement rather than a pure threshold replacement.

---

## XIII. Semantics-Only Fixes

If a change modifies only report wording or observer interpretation, and same-seed reruns produce identical event chains, the change is classified as:

`Semantics Fix`

Such changes do not trigger full baseline replacement review.

---

## XIV. Escalation Trigger

A replacement must escalate beyond this protocol if it involves:
- parameter semantic redefinition
- introduction of new personality parameters
- cross-layer architecture redesign
- canonical mapping change
- phase scope expansion

Such cases fall under broader governance review.

---

## XV. Default Replacement Workflow

Most replacements should follow this process:

`candidate mechanism created`  
`-> paired comparison vs baseline`  
`-> compact validation batch`  
`-> short evaluation report`  
`-> governance decision`  
`-> baseline update`  
`-> code clean-up`

---

## XVI. Guiding Principle

The protocol exists to maintain clarity without slowing engineering.

Replacement decisions should remain:

`small gate`  
`clear evidence`  
`simple decision`

not heavy approval procedures.
