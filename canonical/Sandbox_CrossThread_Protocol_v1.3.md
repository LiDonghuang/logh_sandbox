# Sandbox Cross-Thread Collaboration Protocol

## Version 1.3

Status: Active
Authority: Governance Core (App Layer)
Scope: All Engineering Phases
Mode: Repo-side working protocol update; APP-side local-file sync candidate

This version supersedes operational usage of v1.2 while preserving its core structure.

---

# I. Purpose

This protocol defines the information-exchange discipline between:

* Governance Thread (App Layer)
* Engineering Environment (VS Code / Codex)

The objective is to maintain:

* structural clarity
* parameter discipline
* architecture stability
* minimal context overhead

The protocol ensures that engineering execution remains fast while governance preserves structural integrity.

---

# II. Dual-Core System Model

The sandbox operates under a dual-core architecture.

### Governance Core (App Layer)

Responsibilities:

* architectural doctrine
* parameter semantics
* phase boundaries
* structural guardrails
* interpretation of experiment results

Governance does not implement mechanisms.

---

### Engineering Core (VS Code / Codex)

Responsibilities:

* runtime implementation
* simulation execution
* DOE experiments
* diagnostics
* engineering reports

Engineering does not reinterpret canonical semantics.

---

# III. Layer Separation

System structure must remain layered:

Archetype Layer
-> Runtime Engine
-> Observer Layer
-> Event Detection
-> Reporting / DOE
-> Governance Interpretation

Cross-layer shortcuts are prohibited.

---

# IV. Governance Authority

Governance owns:

* canonical documentation
* parameter meaning
* archetype semantics
* phase escalation decisions

Engineering owns:

* algorithm implementation
* experiment design
* diagnostics
* code architecture

Structural disputes are resolved by Governance.

---

# V. Engineering Autonomy

Engineering may independently perform:

* experiment configuration
* parameter sweeps
* diagnostic metric design
* DOE harness improvements
* movement micro-iterations

Governance approval is not required for routine experimentation.

Governance review is required when proposals involve:

* runtime baseline replacement
* parameter reinterpretation
* new personality parameters
* cross-layer architecture change
* phase escalation

---

# VI. Governance Directive Format

Governance directives for Engineering should be written as directly copyable markdown.

Each formal Governance directive must explicitly state:

* one action-mode tag
* whether workflow / protocol docs must be updated
* whether APP local-file sync is required

The only valid action-mode tags are:

* `[LOCAL ONLY]`
* `[DIRECT PUSH]`
* `[BRANCH + PR]`

Their meanings are:

* `[LOCAL ONLY]`
  * local work only
  * no commit
  * no push
  * no PR

* `[DIRECT PUSH]`
  * commit scoped work
  * push directly to `dev_v2.0`

* `[BRANCH + PR]`
  * commit scoped work
  * push to the named feature branch
  * open a PR into `dev_v2.0`

If a formal Governance directive does not specify an action-mode tag, Engineering must not guess remote actions.

Engineering must stop and report:

* `remote action not specified`

---

# VII. Mandatory Engineering Report Format

Engineering submissions to Governance must use the following structure:

Engine Version:
Modified Layer:
Affected Parameters:
New Variables Introduced:
Cross-Dimension Coupling:
Mapping Impact:
Governance Impact:
Backward Compatible:

Summary (<= 5 lines)

Reports must describe structure, not full derivations.

Standard path reporting must use repo-relative paths first.

Preferred report style:

* `analysis/engineering_reports/developments/...`
* `docs/engineering/...`
* `canonical/...`

Engineering should not use local-machine file hyperlinks as the primary reported path.

If a local-machine path is ever needed for a special reason, the repo-relative path must still be given first.

---

# VIII. Collaboration Routing Rule

Remote collaboration should stay proportionate to carrier size and review risk.

* small, low-risk, document-only carriers may use direct push
* medium or larger review-sensitive carriers should prefer branch + PR

This routing rule does not override the explicit action-mode tag on a Governance directive.

---

# IX. Canonical Discipline

Canonical documents define semantic authority.

Examples include:

* Governance Canonical
* Cross-Thread Protocol
* Parameter Canonical
* Archetype Layer
* Governance Doctrine Memos

Engineering must treat these as interpretive constraints, not casually editable specifications.

Any protocol or workflow-rule update that affects both Governance and Engineering workflow must be dual-anchored:

* committed into repo
* marked for APP local-file upload

---

# X. Context Minimization Rule

To prevent LLM context overload:

* Governance thread remains compact
* Engineering thread holds full math and code
* only structured summaries travel across threads
* canonical text should not be repeatedly copied

This preserves long-term system stability.

---

# XI. Phase Discipline

Sandbox evolution follows the cycle:

experiment
-> observe
-> analyze
-> governance review
-> runtime integration

Engineering exploration happens continuously.

Governance intervention occurs at integration gates.

---

# XII. Phase Escalation Trigger

Engineering must escalate when encountering:

* need for new personality dimension
* parameter semantic conflict
* architecture redesign
* canonical mapping change

In such cases, Engineering must halt structural changes and request Governance review.

---

# XIII. Operational Principle

The sandbox is designed as a deterministic experimental system.

Progress should come from:

* better observation
* better interpretation
* clearer mechanisms

not heavier governance.

Engineering execution should remain rapid.

Governance protects structural clarity.

---

End of Protocol
Sandbox Cross-Thread Collaboration Protocol v1.3
