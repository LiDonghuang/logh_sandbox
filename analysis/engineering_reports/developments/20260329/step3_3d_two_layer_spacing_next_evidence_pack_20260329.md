Engine Version: dev_v2.0
Modified Layer: Analysis / documentation only
Affected Parameters: diagnostic read only for `expected/reference spacing = 2.0` vs `runtime low-level floor = 2.0 / 1.0`
New Variables Introduced: none in runtime; one fixed comparison seed `20260329` for reproducible evidence
Cross-Dimension Coupling: yes; current maintained battle path still couples spawn/reference spacing and runtime low-level floor unless decoupled harness-locally for diagnosis
Mapping Impact: none
Governance Impact: provides the next battle-relevant evidence step for the open two-layer spacing line
Backward Compatible: yes

Summary
- This pack adds one bounded battle-path-relevant comparison beyond the earlier neutral-transit fixture probes.
- The comparison keeps spawn/reference spacing at `2.0` and contrasts a coupled `2.0 / 2.0` read with a harness-local decoupled `2.0 / 1.0` read.
- The spacing split remains materially important in a maintained battle-path-relevant context.
- The result still reads as pre-implementation evidence, not as silent mechanism authorization.

## 1. Purpose

This note records the next missing evidence step requested before any implementation opening could be recommended for the two-layer spacing line.

The goal is narrow:

- stay battle-path-relevant
- stay diagnostic-first
- stay pre-implementation
- avoid geometry hardcoding

## 2. Comparison Path

Comparison path:

- source settings: repo `HEAD` battle path settings
- effective movement model: `v4a`
- fixed comparison seed: `20260329`
- fleets: maintained `reinhard` vs `yang`
- fleet sizes: `100` vs `100`
- aspect ratios: `4.0` vs `4.0`
- bounded run length: `120` ticks

Compared cases:

1. coupled baseline read
   - spawn/reference spacing: `2.0`
   - runtime low-level floor: `2.0`
2. decoupled diagnostic read
   - spawn/reference spacing: `2.0`
   - runtime low-level floor: `1.0`

Important boundary:

- no runtime code was changed
- no public parameter was added
- the split remained harness-local / diagnostic-only

## 3. Human-Readable Artifact

Artifact:

- `analysis/engineering_reports/developments/20260329/step3_3d_two_layer_spacing_battle_compact_comparison_20260329.csv`

This compact CSV records, for both fleets at ticks `0 / 20 / 50 / 100`:

- width/depth ratio
- front extent ratio
- rear / middle / front forward-slot error
- projection pairs count
- corrected-unit ratio

## 4. Main Readout

The decoupled read remains materially better than the coupled read on the battle-relevant path.

Representative `tick 100` comparison:

Fleet `A`
- coupled:
  - width/depth `0.896`
  - front extent `5.157`
  - rear / mid / front forward-slot error `-6.208 / -0.552 / +6.561`
- decoupled:
  - width/depth `2.392`
  - front extent `2.242`
  - rear / mid / front forward-slot error `-3.076 / -0.209 / +3.189`

Fleet `B`
- coupled:
  - width/depth `0.609`
  - front extent `7.733`
  - rear / mid / front forward-slot error `-6.608 / -1.758 / +8.119`
- decoupled:
  - width/depth `1.909`
  - front extent `2.981`
  - rear / mid / front forward-slot error `-4.418 / -0.569 / +4.840`

Projection/correction breadth also drops strongly:

- `tick 100` projection pairs:
  - coupled `108`
  - decoupled `16`
- `tick 100` corrected-unit ratio:
  - coupled `0.58`
  - decoupled `0.135`

## 5. Interpretation

This pack supports four bounded conclusions.

### A. The spacing split still matters outside the earlier fixture-only frame

Yes.
The effect remains strong on a maintained battle-path-relevant comparison and is not confined to `neutral_transit_v1`.

### B. The overloaded spacing radius still reads as a major amplifier

Yes.
The decoupled read does not merely produce a small improvement.
It materially reduces early stretch, front overextension, rank split, and projection/correction breadth.

### C. The result does not mean spacing is the sole deep cause

Correct.
Battle-path deformation still remains under the decoupled read.
So the current best read remains:

- movement-vs-restore asymmetry is primary
- overloaded spacing is a major amplifier / operational lever

### D. The result is stronger than implementation-prep-only concept discussion

Yes.
This evidence is now strong enough to justify asking Governance for bounded implementation authorization next.

That recommendation should still remain narrow:

- no silent rollout
- no public parameter expansion by stealth
- no geometry locking
- no broad movement rewrite

## 6. What Remains Closed

Still closed:

- committed two-layer spacing runtime implementation in this turn
- new public spacing parameter rollout
- geometry hardcoding / rectangle locking
- legality redesign
- viewer ownership widening
- default switch by stealth
- broad movement rewrite

## 7. Bottom Line

The missing battle-relevant evidence step is now in place.

Current engineering read:

- the two-layer spacing split remains materially important outside the earlier fixture-only frame
- the overloaded low-level spacing radius continues to read as a major amplifier
- the line is now strong enough to support a bounded implementation-authorization request next
- implementation itself remains closed until Governance explicitly opens it
