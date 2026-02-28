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

## R-08 - Violation Reporting

If a policy violation is observed, or a request is refused/pushed back, Codex must report:

- `Violated rule: R-xx - <rule name>`
- `Reason: <short concrete reason>`

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

Codex operates under supervised engineering mode.
Human is system architect.
Codex is implementation assistant.
