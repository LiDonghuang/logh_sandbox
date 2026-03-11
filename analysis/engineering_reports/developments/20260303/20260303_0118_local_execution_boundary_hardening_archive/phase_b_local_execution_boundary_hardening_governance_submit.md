# Governance Submission - Phase B Local Execution Boundary Hardening (PowerShell Profile Guard)
Engine Version: v5.0-alpha5 (runtime baseline unchanged)
Modified Layer: Local execution boundary (host PowerShell profile, outside runtime)
Affected Parameters: None (no Archetype/mapping/runtime parameter touched)
New Variables Introduced: None in runtime; host-side guard function and policy constants only
Cross-Dimension Coupling: No
Mapping Impact: None
Governance Impact: Minor (local safety hardening; execution containment)
Stability Property: Runtime behavioral stability preserved (no engine path modification)
Backward Compatible: Yes (non-destructive development flow unchanged)

## Directive Anchor
- Governance Directive: LOGH Local Execution Boundary Hardening v1.0
- Thread Type: Governance Core
- Scope: Personal LOGH Sandbox Environment only (`E:\logh_sandbox\`)

## Phase A Audit Summary (Completed)
- VS Code: `1.109.5`
- Codex extension: `openai.chatgpt@0.4.79`
- Effective shell: Windows PowerShell `5.1`
- Workspace root mapping confirmed: `E:\logh_sandbox`
- Programmatic root validation confirmed feasible via resolved absolute path + prefix match.
- Audit deliverable: `logh_local_execution_environment_audit.md`

## Proposed Phase B Plan (For Approval)
### B.1 Preferred Implementation
PowerShell Profile Guard (minimal overhead, execution-layer enforcement):
1. Intercept destructive commands (`Remove-Item`, aliases `rm`, `del`, `rmdir`).
2. For commands with destructive intent (`-Recurse`, `-Force`, `-rf` equivalent patterns):
   - Resolve every target to absolute path.
   - Validate each target prefix starts with `E:\logh_sandbox\`.
3. If any target is outside root:
   - Abort.
   - Emit exact error: `Execution blocked: outside LOGH root`.
4. For recursive delete inside root:
   - Phase-1 preview list.
   - Phase-2 confirmation prompt.
   - Phase-3 execution.

### B.2 Enforcement Boundary
- Enforcement occurs in shell execution layer (PowerShell profile), not in prompt text.
- No changes to runtime engine, canonical, mapping, or governance docs.
- Non-destructive commands remain unmodified for speed.

### B.3 Verification Plan (Post-Implementation)
1. Test 1: attempt delete outside root -> must be blocked.
2. Test 2: delete inside `E:\logh_sandbox\archive\` -> must be allowed.
3. Test 3: runtime determinism sanity check -> unchanged digest behavior.

## Risk and Compatibility Assessment
- Primary risk: false positives on uncommon path syntaxes (mitigated by canonical path resolution).
- Developer velocity impact: low; constrained to destructive command paths only.
- Regression risk to LOGH runtime: none expected (host-only change).

## Governance Decision Request
Please approve one of the following:
1. Approve Option P (Recommended): implement PowerShell Profile Guard per B.1-B.3.
2. Approve Option W: use wrapper script `logh_safe_exec.ps1` instead of profile guard.
3. Hold: require additional safeguards before implementation.

## Explicit Assumptions
1. This request is scoped to this personal machine and this workspace root only.
2. Canonical/governance/runtime layers are out of scope for this change.
3. Approval here authorizes implementation work for Phase B only, not global policy changes.
