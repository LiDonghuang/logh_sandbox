# GitHub Branch + PR Collaboration Workflow v1.0

Status: Active working workflow  
Scope: GitHub branch / PR collaboration for LOGH engineering carriers  
Authority: engineering workflow aid, not canonical semantics authority

This document records the current lightweight GitHub collaboration workflow for LOGH.

If this document conflicts with:

- `AGENTS.md`
- frozen-layer protections
- explicit Human instruction
- explicit Governance directive

then those higher-priority instructions win.

---

## 1. Purpose

This workflow exists to keep repo collaboration legible as LOGH moves from very small document carriers toward more review-sensitive structural and implementation-adjacent carriers.

The goal is:

- keep repo as the shared working base
- keep carriers narrow
- reduce accidental scope growth
- route larger or riskier carriers through branch + PR review

---

## 2. Action Mode Labels

Each formal Governance directive should now carry one explicit action-mode label.

Only the following three labels are valid:

- `[LOCAL ONLY]`
- `[DIRECT PUSH]`
- `[BRANCH + PR]`

Their meanings are:

- `[LOCAL ONLY]`
  - produce local work only
  - do not commit
  - do not push
  - do not open a PR

- `[DIRECT PUSH]`
  - commit the scoped work
  - push directly to `dev_v2.0`

- `[BRANCH + PR]`
  - commit the scoped work
  - push to the named feature branch
  - open a PR into `dev_v2.0`

Engineering should not infer remote intent from tone or surrounding context.

If a directive does not include an action-mode label, Engineering should stop and report:

- remote action not specified

One-line rule:

- remote behavior must be explicitly labeled rather than guessed

---

## 3. Shared Roles

The repo is the shared working base for three parties:

- Human
  - system architect
  - final approval authority
  - decides when scope expands, when work merges, and when implementation begins

- Governance / ChatGPT
  - phase identity owner
  - boundary / semantics reviewer
  - decides what is open, what remains closed, and what counts as structural overreach

- Engineering / VS-CODEX
  - execution assistant
  - produces scoped documentation, code, or experiment results inside authorized scope
  - must not autonomously widen structure or implementation scope

---

## 4. Direct Push vs Branch + PR

The recommended LOGH default remains:

- small, pure-document, low-risk carriers may use `[DIRECT PUSH]`
- medium or review-sensitive carriers should prefer `[BRANCH + PR]`

### Direct push to `dev_v2.0` is appropriate for:

- governance memo
- structural confirmation note
- scope confirmation note
- small `repo_context.md` / `system_map.md` sync
- very small closeout or index-only documentation updates
- other tiny, boundary-clear, document-only changes when Human prefers speed over PR overhead

### Branch + PR is preferred for:

- mapping minimum contract
- legality opening
- runtime touchpoints
- hook design
- implementation proposal
- any cross-layer change
- any multi-file structural carrier
- any code-changing carrier
- any turn likely to trigger review questions such as:
  - "is this already implementation?"
  - "did this silently open downstream ownership?"

One-line rule:

- small document carriers may go direct
- structure-sensitive or implementation-adjacent carriers should prefer PR

---

## 5. Branch Naming

Feature branches should normally start from `dev_v2.0`.

Recommended prefixes:

- `gov/<topic>`
- `eng/<topic>`
- `doc/<topic>`

Optional temporary prefixes:

- `exp/<topic>`
- `wip/<topic>`

Examples:

- `gov/mapping-opening`
- `eng/mapping-min-contract`
- `eng/legality-opening`
- `doc/repo-index-sync`

Branch names should stay short, readable, and carrier-specific.

---

## 6. One PR = One Carrier

Each PR should carry one carrier only.

Good examples:

- one `FormationLayoutSpec3D` structural confirmation
- one mapping opening scope confirmation
- one mapping minimum contract draft

Do not mix:

- formation + mapping
- mapping + legality
- docs + runtime hooks
- viewer polish + semantics opening

One-line rule:

- one PR = one carrier = one review question

---

## 7. Base Branch

Unless Human explicitly directs otherwise, the authoritative working base remains:

- base branch: `dev_v2.0`

Typical PR direction:

- base = `dev_v2.0`
- compare = scoped feature branch

Do not target `main` casually.

---

## 8. PR Titles

Recommended title prefixes:

- `docs: <topic>`
- `gov: <topic>`
- `eng: <topic>`
- `runtime: <topic>` only when implementation work is explicitly open

Examples:

- `docs: add Mapping Minimum Contract structural draft note`
- `gov: close FormationLayoutSpec3D opening`
- `eng: add legality opening scope note`

Titles should describe the carrier precisely and avoid implementation overclaim.

---

## 9. PR Description Template

PR descriptions should usually include:

- `Purpose`
  - the PR's one intended outcome

- `Scope`
  - what is included

- `Explicitly Closed`
  - what remains out of scope

- `Files`
  - which files changed

- `Governance Read`
  - how the carrier should be interpreted

Example shape:

- `Purpose: confirm mapping minimum contract`
- `Scope: structural-draft-only`
- `Explicitly Closed: legality / runtime hooks / implementation`
- `Files: one note + optional index sync`
- `Governance Read: mapping second carrier only`

### Path Reporting Rule

Engineering should use repo-relative paths first when reporting results to Human or Governance.

Preferred reporting shape:

- `analysis/engineering_reports/developments/20260327/xxx.md`
- `docs/engineering/xxx.md`

Engineering should not use local-machine path style or local clickable-link style as the standard reporting format.

Avoid standard report shapes such as:

- `/E:/logh_sandbox/...`
- local-machine file hyperlinks

If a local file path must be mentioned for some special reason, the repo-relative path should still be given first as the primary path.

---

## 10. Review Focus

### Human review emphasis

- should this carrier merge now
- did scope stay worth the repo churn
- does it fit the current project cadence

### Governance review emphasis

- is the phase identity correct
- did any boundary collapse
- did the carrier silently open downstream ownership
- did concept language drift into implementation language

### Engineering self-check emphasis

- did the change violate `AGENTS.md`
- did it create silent refactor or scope creep
- does it require `repo_context.md` / `system_map.md` sync
- is the carrier still singular and reviewable

---

## 11. When Not To Open A PR

PR overhead is usually not worth it for:

- typo-only edits
- very small path or index sync
- adding a just-accepted memo into a repo index
- a very lightweight closeout note

For those cases, direct push to `dev_v2.0` is often the cleaner workflow when Human approves that faster path.

---

## 12. When PR Is Strongly Recommended

PR workflow is strongly recommended for:

- runtime code changes
- mapping-contract work beyond the lightest clarification stage
- legality opening
- touchpoint inventory
- implementation proposal
- any structural multi-file change
- any carrier that may be mistaken for implementation activation

One-line rule:

- if the review question is non-trivial, prefer branch + PR

---

## 13. Merge / Accept Checks

Before merge or acceptance, review at least:

- did scope remain singular
- is the PR title accurate
- does the PR description clearly state closed items
- does the carrier preserve Governance boundary
- does `repo_context.md` need sync
- does `system_map.md` need sync

If no meaningful repo-structure or mechanism availability change occurred, explicitly confirm that those index files were reviewed and did not need updates.

---

## 14. Recommended LOGH Cadence

### Small carrier rhythm

- Engineering pushes to `dev_v2.0`
- Governance reviews in chat
- repo becomes the working record

### Medium or larger carrier rhythm

- Engineering creates a scoped branch
- Engineering pushes to that branch
- Engineering opens PR into `dev_v2.0`
- Governance reviews in chat and, when useful, against the PR
- Human decides whether and when to merge

This is the current recommended balance for LOGH:

- small document carriers can stay fast
- structure-sensitive carriers get explicit review space

---

## 15. Working Standard

Keep the following read explicit:

- contract clarification is not implementation authorization
- carrier clarity matters more than batching many ideas together
- repo is the shared working base
- Governance reviews boundary and phase identity
- Engineering does not use PR structure as a reason to widen scope

One-line standard:

- small docs may direct-push; structure and implementation-adjacent carriers should prefer one-PR-per-carrier review into `dev_v2.0`

## 16. Human-Readable Evidence Reminder

For substantive runtime modifications, Engineering should leave at least one minimal human-readable validation artifact.

Preferred default is the lightest useful form:

- short animation sample or frame sample when practical
- small plot / chart
- tick-level CSV
- short targeted trace
- before / after comparison

Default preference is minimal size.

Do not expand into heavier artifacts unless the human asks for them or the lighter artifact is insufficient.
