# Step 3 3D Legality Execution Order Decision Note (2026-03-28)

Engine Version: `dev_v2.0`
Modified Layer: Step 3 legality line local pre-implementation execution-order decision
Affected Parameters: none
New Variables Introduced: none
Cross-Dimension Coupling: fixes the minimum stage-order relationship for legality between mapping output and downstream feasible-outcome consumption without freezing exact hook locations or algorithms
Mapping Impact: preserves mapping ownership by forcing mapping output completion before legality intake begins
Governance Impact: advances legality from placement and data-surface decisions to a bounded order decision that is still smaller than implementation and hook design
Backward Compatible: yes

Summary
- This turn fixes the minimum stage-order relationship for legality only.
- The correct bounded order is: mapping output ready -> legality intake -> legality-owned resolution -> feasible-outcome handoff -> first downstream consumer.
- Observer/report echo belongs only after handoff and outside the core execution chain.
- No internal projection/collision/boundary sub-order is frozen here.
- Exact hook location, call path, and execution-order mechanics remain later decisions.

## 1. Decision Scope

This carrier decides only:

- the minimum stage-order relationship around legality

It does not decide:

- exact function order
- exact loop placement
- exact call-path structure
- exact internal sub-order for projection / collision / boundary work

## 2. Core Order Decision

The minimum bounded order should now be read as:

1. mapping-produced reference outcome becomes available
2. legality intake begins
3. legality-owned resolution runs as one bounded middle stage
4. legality-resolved feasible outcome is handed off
5. first downstream consumer may consume that post-legality feasible outcome

This is the smallest order decision that makes legality operationally readable without freezing implementation details.

## 3. Upstream-First Rule

The upstream-first rule is:

- legality may not begin until mapping output is already available

This prevents:

- mapping/legality interleaving
- mapping redesign by stealth
- legality consuming a partly-formed mapping surface

The bounded answer is:

- mapping finishes its output surface first
- legality reads that completed surface second

## 4. Single Middle-Stage Rule

The legality-owned work should remain a single middle stage at order-decision level.

That middle stage owns:

- downstream feasibility resolution
- weak projection scope
- weak collision / boundary scope

This rule does not freeze how internal sub-questions are sequenced.

It only fixes that:

- legality-owned resolution stays between intake and handoff

## 5. Handoff-Before-Consumption Rule

The feasible-outcome handoff must happen before the first downstream consumer.

This means:

- downstream consumer may not read pre-legality reference intent as if it were post-legality feasible outcome
- legality ownership must complete before downstream consumption begins

The bounded answer is:

- handoff first
- downstream consumption second

## 6. Observer / Report Echo Order Rule

Observer/report echo should remain outside the core order chain.

The safest bounded reading is:

- observer/report echo may read from the post-handoff side only
- observer/report echo may not sit inside legality-owned resolution
- observer/report echo may not define the core order of legality itself

This keeps diagnostics secondary and avoids turning report/readout concerns into control flow.

## 7. What The Order Decision Explicitly Does Not Freeze

This note does not freeze:

- exact projection-before-collision ordering
- exact collision-before-boundary ordering
- exact within-stage loop order
- exact module/function boundaries
- exact downstream consumer identity

Those are later implementation decisions.

## 8. Bottom Line

The minimum order decision is:

- mapping output ready
- legality intake
- legality-owned resolution
- feasible-outcome handoff
- first downstream consumption
- optional observer/report echo only after handoff and outside the core chain

That is sufficient for this carrier.
