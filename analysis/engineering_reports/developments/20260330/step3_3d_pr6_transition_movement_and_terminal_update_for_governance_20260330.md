# Step 3 3D PR #6 Transition-Movement and Terminal Update for Governance

Status: governance update / review memo  
Scope: PR `#6` branch-only bounded carrier update  
Layer read: `test_run` harness-only candidate evolution plus viewer-side supporting visual update  
Authority requested: discussion / review only, not merge approval, not default switch approval

---

## I. Purpose

This note updates Governance after the latest local rounds on PR `#6`.

The purpose is not to claim that the current branch has solved formation transition.

The purpose is to report, clearly and honestly:

1. what engineering tried after the reference-only carrier failure read
2. what improved
3. what failed
4. what Human observed directly
5. what this now teaches about both the system problem and the limits of the recent AI-assisted method

This update should be read together with:

- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_reference_only_carrier_failure_review_request_20260330.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_banded_surface_followup_governance_review_request_20260330.md`
- `analysis/engineering_reports/developments/20260330/step3_3d_pr6_round0_formation_transition_carrier_redefinition_note_20260330.md`

---

## II. Working Methodology in This Round

After Governance accepted that PR `#6` had reached the limit of a reference-only carrier, engineering did **not** move into runtime-core rewrite.

Instead, the work stayed bounded to the `test_run` harness candidate line and proceeded as a sequence of small local carrier experiments:

### 1. Formation-reference re-read

The carrier was progressively moved away from:

- exact rigid slot holding
- then strong band-center ownership

toward:

- continuous morphology state
- continuous per-unit material phase
- minimal movement-realization seams

### 2. Movement seam exploration

Two bounded movement-realization seams were then opened locally:

- `shape_vs_advance_strength`
- `heading_relaxation`

These were not treated as a full movement rewrite.
They were treated as the smallest possible test of whether formation transition requires explicit movement budgeting and non-instant heading realization.

### 3. Terminal / arrival seam isolation

Once Human observed that both `1 -> 4` and `4 -> 1` were still failing in the terminal window, engineering explicitly separated:

- transition quality
from
- terminal / arrival correctness

That produced a later bounded terminal-stage / hold-await correction.

### 4. Validation posture

Throughout this period, validation remained:

- local
- harness-only
- human-readable first

The decisive control surface was not scalar cleanliness alone.
It was repeated Human animation read, especially where the visual read contradicted the apparent neatness of local metrics or logic.

---

## III. Human Interaction and Control-Surface Role

Human interaction was not auxiliary in this round.
It was the control surface that repeatedly corrected engineering drift.

The key Human interventions were:

### 1. Human rejected false-positive metric comfort

Several intermediate local candidates looked cleaner in:

- expected-position RMS
- front extent behavior
- shape-error traces
- hold semantics

But Human observed motion that still read as:

- rigid plate behavior
- sparse stray movers
- lateral rupture
- shell-like external success with chaotic interior
- late-stage collapse / rotation / wrong-direction turning

This repeatedly forced engineering to abandon superficially cleaner but behaviorally wrong reads.

### 2. Human explicitly reframed the true requirement

Human made clear that the real requirement is not merely:

- holding a target shape when initial and reference already match

The real requirement is:

- forming the target shape continuously from a different initial shape

The critical examples were:

- `1 -> 4`
- `4 -> 1`

That reframing materially changed the carrier read.

### 3. Human explicitly called out AI method limits

Human correctly pointed out that recent AI-assisted iterations were repeatedly optimizing:

- local logical cleanliness
- cleaner reference logic
- apparently tidy scalar readouts

without sufficiently owning the coupled nature of:

- target morphology
- transport / topology continuity
- movement realization

This criticism is accepted in the engineering read.

Current honest summary:

> Human visual judgment exposed several cases where AI produced locally coherent but behaviorally inadequate intermediate carriers.

That is an important methodological lesson from this branch.

---

## IV. What Engineering Tried After the Carrier Redefinition

After the carrier was redefined away from "better reference surface, then runtime follows it," engineering tried the following bounded local seams.

### A. Continuous morphology quantities

The candidate now uses continuous morphology-level quantities rather than treating exact slots as first semantics.

The relevant local state now includes:

- `morphology_axis_current`
- `morphology_center_current`
- `forward_extent_current`
- `lateral_extent_current`
- continuous per-unit material phase

### B. Minimal movement-realization seams

The candidate also now includes:

- `shape_vs_advance_strength`
- `heading_relaxation`

These were opened because Human correctly observed that real formation change cannot be understood without at least:

- slowing / budgeting
- turning / heading realization

### C. Terminal / hold-await correction

After Human observed persistent arrival failure and late chaotic reorganization, engineering added a bounded terminal fix:

- a morphology-level terminal stage
- post-move terminal capture
- morphology-level hold-await entry at terminal capture

This was deliberately kept harness-only and did not touch `runtime/engine_skeleton.py`.

---

## V. What Improved

The current engineering read is that several bounded gains are now real.

### 1. PR `#6` still retains genuine value

The branch still carries valuable bounded assets:

- expected/reference spacing legitimacy
- physical minimum spacing split
- restore-line legitimacy
- battle-side restore-line visibility
- human-readable evidence line
- explicit failure learning from the reference-only carrier

### 2. `4 -> 1` now reads more like a continuous transition than before

Human explicitly observed that `4 -> 1` improved relative to earlier branch states.

Although still not good enough, it now reads more like:

- a real compression-type transition

rather than:

- a simple shell collapse

### 3. `1 -> 4` also improved relative to earlier branch states

Human also observed that `1 -> 4` improved relative to older iterations.

The transition is still wrong, but it now at least shows:

- lateral expansion
- partial group separation

instead of only direct rigid locking or immediate collapse.

### 4. Terminal non-arrival bug was materially reduced

Before the latest terminal fix:

- both mismatch cases could fail to count as arrival
- or continue running to the hard cap / terminal chaos window

After the terminal-stage correction:

- the prior "cannot arrive at all" failure mode is substantially reduced
- both mismatch scenarios can now enter the terminal window and close out the run

This does **not** solve the shape-quality problem.
But it does solve one real independent bug:

- arrival / hold semantics were previously incorrect

---

## VI. What Still Fails

This is the most important part of the update.

### 1. `1 -> 1` and `4 -> 4` still read too rigid

Human observed that the matched cases still look like:

- mostly fixed plate-like translation
- with only a few individual slow movers

This means the branch still does **not** yet support a settled "living formation" read even in the easiest matched cases.

### 2. `1 -> 4` still does not form the target shape honestly

Human's latest read is:

- the formation expands laterally
- but does not compress forward in the intended coordinated way
- it behaves more like two lateral square-like groups
- the groups are not fully re-aligned or re-compressed along the movement axis

So the carrier still fails the core expansive-transition requirement.

### 3. `4 -> 1` still reads as too compressed, too slow, and not truly orderly

Human's latest read is:

- the compression remains too "pushy"
- many units still look squeezed rather than naturally reorganized
- the final stabilized shape is still not even enough

So although `4 -> 1` improved, it is still not yet a believable formation-transition result.

### 4. Arrival remains visually wrong even after the terminal fix

The specific non-arrival bug was reduced.

But Human still observes at arrival:

- forced regularization
- internal disorder
- partial unit reversal
- internal jitter

So terminal correctness and terminal plausibility are now separated:

- correctness improved
- plausibility is still not solved

---

## VII. Current Engineering Read

The current engineering read is now:

### 1. The direction is still broadly correct

The branch is moving away from:

- rigid slot logic
- explicit band-subformation overownership
- pure reference-only carrier assumptions

and toward:

- continuous morphology
- transition transport
- movement realization seams

That broad direction should still be considered valid.

### 2. But the system problem is more deeply coupled than the AI method initially respected

The real problem is still jointly owned by:

- target morphology
- transport/topology continuity
- movement realization

Recent AI-assisted work repeatedly underestimated how inseparable these three layers are.

### 3. Scalar cleanliness is still not a trustworthy success proxy here

Current hard lesson from the branch:

> locally cleaner reference logic, lower shape-error traces, or more orderly state transitions do not by themselves mean the formation behavior is correct

Human motion read remains the higher-authority signal.

### 4. The terminal bug was real but secondary

Fixing terminal semantics was necessary.
It was also correct to isolate it first.

But the branch now shows more clearly that the deeper remaining problem is:

- not terminal capture alone
- but the quality of transition movement itself

especially for:

- expansion
- coordinated compression
- final non-chaotic formation settling

---

## VIII. Methodological Lesson About AI Assistance

This round produced a useful engineering lesson that should be preserved explicitly.

### Accepted limitation exposed by this branch

The recent AI-assisted workflow was relatively good at:

- isolating local seams
- making coherent local state machines
- reducing some classes of bug
- cleaning up some metrics

But it was relatively weak at:

- recognizing when a logic-clean intermediate carrier still lacked believable motion semantics
- keeping transport continuity and movement realization fully co-owned from the start
- respecting how quickly a superficially neat discrete carrier can become:
  - rigid
  - internally split
  - or shell-correct but interior-chaotic

That limitation is now explicitly part of the engineering read.

### Required control-surface conclusion

For this class of problem:

- Human animation read must remain primary
- AI local cleanliness must remain subordinate

This is not just a preference.
It is now evidence-backed process knowledge from the branch.

---

## IX. Current Recommendation to Governance

Current recommendation is not:

- merge-read
- default-switch
- branch abandonment

Current recommendation is:

### 1. Preserve PR `#6` as the active bounded learning line

Because it now contains too much real bounded value and too much real failure learning to discard.

### 2. Continue to read the next carrier as a true formation-transition carrier

The branch should not return to:

- reference-surface tuning
- simple restore tuning
- band-surface tuning in isolation

### 3. Treat movement realization as first-class, not merely future realism

The latest local rounds support a stronger methodological read:

- turning / slowing / arrival / hold are not optional realism extras
- they are part of the formation-transition problem itself

### 4. Keep Human observation as the decisive review instrument

Especially for:

- `1 -> 4`
- `4 -> 1`
- terminal settle quality

---

## X. Bottom Line

The latest local rounds did produce real progress:

- terminal non-arrival was materially reduced
- mismatch transitions improved relative to earlier branch states
- the branch now has a more honest continuous-carrier read than before

But the branch also exposed a sharper truth:

> the real formation-transition problem remains more coupled, more motion-dependent, and more topologically delicate than the recent AI-assisted reference-first iterations were able to respect.

The current branch should therefore continue as:

- a valuable bounded learning line
- with Human motion read as the controlling review surface
- and with the next carrier continuing to co-own:
  - target morphology
  - transport/topology continuity
  - movement realization

not one of those layers in isolation.
