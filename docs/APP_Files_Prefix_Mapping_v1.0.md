# APP Files Prefix Mapping v1.0

Authority: Governance Core alignment  
Scope: Documentation organization only  
Mode: Mapping / APP mirror policy only

This file defines the current APP-side flat mirror policy.
The repository remains the authoritative source with structured paths.

## Active APP Mirror Policy

The APP-side repo-backed active governance working set is intentionally narrowed to 10 markdown files.
Those 10 files are the only active repo-backed APP mirror set at present.

`repo_context.md` and `system_map.md` are no longer maintained as full APP local mirror files.
APP-side orientation may instead rely on a local `REPO_INDEX_POINTER` workflow that directs Governance back to the repo-side authoritative paths.

Everything else remains repo-side authoritative, reference, or archival material.
It may still be retained in the repository, but it is not part of the APP active governance working set.

## Prefix Classes

- `00_`: Governance / protocol canonical
- `10_`: Structural / mechanism boundary core
- `40_`: Governance operations / playbook layer
- `50_`: Working context / orientation
- `90_`: Archive / historical / repo-retained only

## APP Active Mirror Set

| APP flat mirror filename | VS authoritative source path | Class | Status |
| --- | --- | --- | --- |
| `00_Sandbox_Governance_Canonical_v1.1.md` | `canonical/Sandbox_Governance_Canonical_v1.1.md` | 00 | active |
| `00_Sandbox_CrossThread_Protocol_v1.4.md` | `canonical/Sandbox_CrossThread_Protocol_v1.4.md` | 00 | active |
| `00_Baseline_Replacement_Protocol_v1.0.md` | `docs/governance/Baseline_Replacement_Protocol_v1.0.md` | 00 | active |
| `10_Formation_Geometry_Doctrine_v1.0.md` | `docs/architecture/Formation_Geometry_Doctrine_v1.0.md` | 10 | active |
| `10_Ten_Parameters_Personality_to_Battlefield_Behavior_Mapping_Canonical_Draft.md` | `canonical/Ten_Parameters_Personality_to_Battlefield_Behavior_Mapping_Canonical_Draft.md` | 10 | active |
| `10_Ten_Parameters_Canonical_Index_v1.1.md` | `canonical/Ten_Parameters_Canonical_Index_v1.1.md` | 10 | active |
| `10_Engine_v2.0_Skeleton_Canonical.md` | `canonical/Engine_v2.0_Skeleton_Canonical.md` | 10 | active |
| `10_Engine_v2.0_Skeleton_Freeze_Declaration.md` | `canonical/Engine_v2.0_Skeleton_Freeze_Declaration.md` | 10 | active |
| `40_Phase_Transition_Governance_Playbook_v1_0.md` | `docs/governance/Phase_Transition_Governance_Playbook_v1_0.md` | 40 | active; governance operations / playbook layer; non-canonical |
| `40_Legality_First_Bounded_Baseline_Hardening_Working_Charter_v1.0.md` | `docs/engineering/Legality_First_Bounded_Baseline_Hardening_Working_Charter_v1.0.md` | 40 | active; phase working charter; bounded hardening mode only |

## Pointer-Based Orientation Rule

APP-side local orientation may use a local `REPO_INDEX_POINTER` workflow instead of full mirror copies of:

- `repo_context.md`
- `system_map.md`

The repo remains authoritative for those two files.
APP-side local pointer/orientation files are not treated as repo-backed semantic mirrors.

## Removed From APP Active Mirror

The following files are not part of the APP active governance mirror anymore:

- `canonical/Strategic_Archetype_Layer_v1.5.md`
- `canonical/archive/Ten_Parameters_Three_Class_Mapping_Essay_v1.1.md`
- `docs/parameter_mapping/archive/Mapping_Snapshot_v1.1_PursuitDrive.md`
- `canonical/Cohesion_v2_Canonical_Mechanism_v1.0.md`

They remain repo-side reference or historical material as applicable.
They must not be treated as part of the APP active governance working set.

## Repo-Retained Historical Examples

These remain repository-side historical materials and are not part of the APP active mirror:

- `canonical/archive/`
- `docs/archive/governance_specs/`
- `docs/parameter_mapping/archive/`
- `docs/phase_chronicles/`

Examples include:

- `docs/archive/governance_specs/Engagement_Drag_B1_Advisory_v1.0.md`
- `docs/archive/governance_specs/Return_Probability_Geometry_Spec_v1.0.md`
- `docs/archive/governance_specs/ODW_Posture_Bias_Prototype_Spec_v1.0.md`

## Separation Rule (APP vs VS)

APP-side repo-backed mirror includes only the 10-file active governance working set listed above.

APP-side local pointer/orientation files may still exist outside that repo-backed mirror set.

APP-side mirror does not include:

- analysis standards/templates
- mapping snapshots
- archive governance specs
- runtime output artifacts
- engineering report outputs
- full mirror copies of `repo_context.md` / `system_map.md`

Those remain VS-side only under their authoritative repository paths.
