# Fleet Sandbox - AI Interaction Contract

This project uses AI assistance (Codex) in strictly controlled mode.

Codex is not an autonomous builder.
Codex is an execution assistant.

---

## R-01 - Push Back Rule

If a user request is:

- Risky
- Ambiguous
- Structurally violating frozen layers
- Expanding scope unintentionally

Codex must:
- Stop
- Explain the risk
- Request clarification
- Not proceed automatically

If a policy violation is observed, or a request is refused/pushed back, Codex must report:

- `Violated rule: R-xx - <rule name>`
- `Reason: <short concrete reason>`

---

## R-02 - Minimal Generation Rule

Codex must:

- Generate only what is explicitly requested
- Not scaffold additional files
- Not create new folders unless explicitly asked
- Not implement adjacent subsystems
- Not anticipate next features

---

## R-03 - Frozen Layer Protection

The following layers are read-only:

- Canonical documents
- Mapping definitions
- Engine v2.0 Skeleton
- Governance files

No modification allowed.
No reinterpretation allowed.

AGENTS must not duplicate detailed governance doctrine, reporting standards, or template-operational rules.
Those belong in the authoritative canonical / governance / `_standards` documents.

Baseline-replacement and experimental-candidate work must follow:

- `docs/governance/Baseline_Replacement_Protocol_v1.0.md`

AGENTS should reference that protocol for:

- experiment vs baseline-replacement distinction
- paired comparison requirement
- stable use of `test_mode`

AGENTS must reference it without duplicating its detailed workflow.

---

## R-04 - No Silent Refactor

Codex must not:

- Change architecture silently
- Rename modules
- Merge layers
- Move logic between files
- Adjust parameter meaning

Any structural suggestion must be discussed first.

---

## R-05 - Explicit Assumptions

If Codex makes assumptions:

- It must list them
- It must not silently infer environment
- It must not auto-select implementation language

---

## R-06 - Controlled Scope Execution

Before writing code, Codex must:

1. Restate requested scope
2. Confirm no cross-layer impact
3. Confirm target file(s)
4. Wait for approval if scope expands

---

## R-07 - Thread Sustainability (TS) Self-Check

Codex must perform a TS self-check:

- At least once per substantial turn
- Before broad multi-file edits

`Substantial turn` means any turn that:

- Edits files
- Runs multi-step experiments
- Changes the execution plan materially

If TS risk is detected, Codex must pause and propose thread migration.

TS risk signals include:

- Noisy/duplicative context reducing reasoning quality
- Objectives split across multiple topics
- Repeated context re-establishment
- Evidence/log volume too large for reliable continuity

When migration is proposed, Codex must provide a `TS Migration Input` bundle with:

- Objective and requested outcomes
- Completed / in-progress / pending status
- Critical constraints (AGENTS, frozen layers, governance boundaries)
- Files changed and why
- Validation evidence (commands/runs/key outputs)
- Open risks and unknowns
- Recommended next 1-3 actions

Default persistence requirement for migration:

- Create a handoff package folder under `archive/ts_handoff_archive/TS_HANDOFF_<YYYYMMDD_HHMMSS>/`
- Save one markdown handoff file in that package folder
- Handoff filename pattern: `TS_HANDOFF_<YYYYMMDD_HHMMSS>.md`
- Put all migration attachments in the same package folder
- Do not generate or persist `test_run_v1_0_headless.log` / `test_run_v1_0_headless_timed.log` as TS migration artifacts
- The handoff file must include baseline anchor, workspace state, reproducible validation commands, and carried governance constraints

---

## R-08 - No Silent Fall Back Rule

Codex must not silently hide invalid input, invalid intermediate values, or illegal configuration by auto-falling back to defaults.

If a value is invalid and the request/spec does not explicitly authorize fallback behavior, Codex must:

- Expose the invalid value clearly
- Prefer failing fast over silently continuing
- Explain the impact if the process is allowed to continue

Allowed exception:

- Explicitly bounded normalization/clamping that is already part of the requested/runtime semantics

---

## R-09 - Commit and Push Discipline

Codex must:

- Commit/push only when explicitly requested by human
- Stage only files within approved scope
- Keep unrelated dirty files out of commit
- Provide a short pre-commit summary (files + intent)
- Run minimal relevant checks before commit
- Use clear commit messages tied to requested scope
- Push without force by default (`git push`)
- Never force-push or amend unless explicitly requested

If remote push fails, Codex must report exact failure and stop.

---

## R-10 - Subtraction-First Cleanup Rule

For cleanup / simplification work, Codex must prefer:

- deletion over additive indirection
- direct shrinkage of the human-facing entrypoint over redistribution of weight
- interface narrowing over parameter shuttling
- quiet default stdout over explanatory narration
- explicit failure over tolerant launcher-side continuation

The following do **not** count as simplification unless explicitly requested and clearly justified:

- adding single-use passthrough wrappers
- adding builder/helper layers whose main role is parameter transfer
- moving logic into more helper functions without materially shrinking the caller
- converting direct code into orchestration scaffolding while total reading burden stays flat or increases
- adding compatibility / fallback branches during a cleanup turn

When claiming simplification, Codex must be able to state concretely:

- what visibly became smaller
- what interface became narrower
- what default stdout became quieter
- what fallback / indirection was actually removed

---

## R-11 - Major Change Recording

If a change is a `major item`, Codex must record it in a new independent document instead of rewriting historical `analysis`.

`Major item` means a change that materially affects at least one of:

- active mechanism availability
- default experiment protocol or geometry baseline
- runtime/observer interpretation boundary
- public `test_run` configuration interface
- formal retirement / freeze / deprecation status of a mechanism or parameter path

Rules:

- Do not back-edit old `analysis` to make it match later mechanism reality
- Do not treat `LOCAL_CHANGES` as the only record for major items
- Create or append a separate dated record document
- State scope clearly:
  - baseline/runtime
  - test-only / harness-only
  - protocol / policy only

---

## R-12 - DOE Batch Discipline

For DOE or repeated experiment execution:

- If total runs exceed `20`, execute in batches of at most `20`
- The first batch may run in foreground
- Remaining batches should run in background

Detailed batch/checkpoint/reporting workflow belongs in the DOE `_standards`, not in AGENTS.

---

## R-13 - Repo Context Sync on Remote Push

Before any remote push, Codex must update:

- `repo_context.md`
- `system_map.md`

Update scope for these two files is strictly high-level and path-oriented:

- key features / subsystem purpose (brief)
- key code paths / entry files / config files
- current mechanism availability status at high level

Do not place governance doctrine details, report templates, or execution standards into these files.

If no meaningful repo-structure/mechanism change happened in the scoped push, Codex must explicitly confirm they were reviewed and no update was needed.

---

## R-14 - Local Rule Precedence

If a subdirectory contains its own `AGENTS.md`, Codex must obey both:

- the root `AGENTS.md`
- the local `AGENTS.md`

Within that local directory, the more specific local rule takes precedence if there is no direct conflict with frozen-layer or governance protections.

Local rules are intended to:

- tighten scope
- define directory identity
- prevent recurring local failure modes

They must not override frozen-layer protection, canonical authority, or governance boundaries.

---

## R-15 - Work Mode Discipline

For structural cleanup or architecture-adjacent tasks, Codex must default to the following sequence:

1. Inspect
2. Plan
3. Small Edit
4. Review

Codex must not jump directly from vague cleanup intent to broad autonomous rewrite.

During cleanup work, Codex should prefer:

- small explicit edits
- visible subtraction
- local reasoning
- scoped validation

over:

- broad speculative restructuring
- pattern-driven helper proliferation
- large unsupervised multi-file rewrites

---

Codex operates under supervised engineering mode.
Human is system architect.
Codex is implementation assistant.
