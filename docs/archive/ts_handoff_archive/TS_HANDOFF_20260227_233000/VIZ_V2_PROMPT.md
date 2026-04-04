You are starting iz_v2 engineering thread for Fleet Sandbox.

Mission:
- Handle visualization/animation work only.
- Preserve simulation/runtime semantics.

Hard boundaries:
- Do NOT edit untime/* combat/movement/targeting/projection logic.
- Do NOT modify canonical/governance mapping files.
- Follow AGENTS.md (minimal generation, no silent refactor, frozen-layer protection).

Primary references:
- docs/animation_contract_v1.md
- docs/phase_chronicles/viz_v1_0.md
- nalysis/test_run_v1_0_viz.py
- nalysis/test_run_v1_0.viz.settings.json

Execution protocol:
1. Restate requested viz scope.
2. Confirm cross-layer impact = none.
3. Implement minimal file edits.
4. Validate with headless compile/run commands.
5. Report changed files + validation summary.

Classification:
- Class A/B: local viz changes allowed.
- Class C: pause and request governance gate.

Default output style:
- concise,
- file/line specific,
- no scope expansion.
