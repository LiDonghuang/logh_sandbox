# APP Files Prefix Mapping v1.0

Authority: Governance Core alignment
Scope: Documentation organization only
Mode: Mapping (no forced bulk rename in VS repository)

This file defines the flattened APP-side filename mapping using numeric prefixes.
VS-side files remain authoritative with structured paths.

## Prefix Classes
- `00_`: Governance canonical (constitution-level)
- `10_`: Mechanism canonical (stable semantics)
- `20_`: Proposals/shadow systems (non-canonical active experiments)
- `30_`: Standards/templates (reusable reporting contracts)
- `90_`: Archive (historical/retired)

## Mapping Table
| APP flat mirror filename | VS authoritative source path | Class | Status |
| --- | --- | --- | --- |
| `00_Sandbox_Governance_Canonical_v1.1.md` | `canonical/Sandbox_Governance_Canonical_v1.1.md` | 00 | active |
| `90_Sandbox_Governance_Canonical_v1.0.md` | `canonical/archive/Sandbox_Governance_Canonical_v1.0.md` | 90 | historical |
| `00_Sandbox_CrossThread_Protocol_v1.2.md` | `canonical/Sandbox_CrossThread_Protocol_v1.2.md` | 00 | active |
| `90_Sandbox_CrossThread_Protocol_v1.1.md` | `canonical/archive/Sandbox_CrossThread_Protocol_v1.1.md` | 90 | historical |
| `90_Phase_Transition_Governance_Playbook_v1_0.md` | `docs/governance/Phase_Transition_Governance_Playbook_v1_0.md` | 90 | non-canonical active |
| `10_Cohesion_v2_Canonical_Mechanism_v1.0.md` | `canonical/Cohesion_v2_Canonical_Mechanism_v1.0.md` | 10 | active |
| `10_Strategic_Archetype_Layer_v1.5.md` | `canonical/Strategic_Archetype_Layer_v1.5.md` | 10 | active |
| `10_Ten_Parameters_Canonical_Index_v1.1.md` | `canonical/Ten_Parameters_Canonical_Index_v1.1.md` | 10 | active |
| `90_Ten_Parameters_Three_Class_Mapping_Essay_v1.1.md` | `canonical/archive/Ten_Parameters_Three_Class_Mapping_Essay_v1.1.md` | 90 | historical |
| `90_Mapping_Snapshot_v1.1_PursuitDrive.md` | `docs/parameter_mapping/archive/Mapping_Snapshot_v1.1_PursuitDrive.md` | 90 | historical |
| `90_Mapping_Snapshot_v1.0_PursuitThreshold.md` | `docs/parameter_mapping/archive/Mapping_Snapshot_v1.0_PursuitThreshold.md` | 90 | historical |
| `90_Mapping_Snapshot_v1.0_*.md` | `docs/parameter_mapping/archive/Mapping_Snapshot_v1.0_*.md` | 90 | historical |
| `10_Phase_V2_Mobility_Bias_Canonical_Activation_v5_0_alpha4.md` | `docs/phase_chronicles/phase_v_2_mobility_bias_canonical_activation_v5_0_alpha4.md` | 10 | active |
| `20_Cohesion_v3p1_Proposal.md` | `N/A (no canonical/docs proposal file currently published)` | 20 | reserved |
| `30_DOE_Report_Standard_v1.0.md` | `analysis/engineering_reports/_standards/DOE_Report_Standard_v1.0.md` | 30 | active |
| `30_BRF_Export_Standard_v1.0.md` | `analysis/engineering_reports/_standards/BRF_Export_Standard_v1.0.md` | 30 | active |
| `30_Analysis_Scripts_Index_v1.0.md` | `analysis/engineering_reports/_standards/Analysis_Scripts_Index_v1.0.md` | 30 | active |
| `30_BRF_Template_v1.0.md` | `analysis/engineering_reports/_standards/Battle_Report_Framework_v1.0.template.md` | 30 | active |
| `30_Behavior_Event_Layer_Spec_v1.0.md` | `analysis/engineering_reports/_standards/Behavior_Event_Layer_Spec_v1.0.template.md` | 30 | active |
| `90_Engagement_Drag_B1_Advisory_v1.0.md` | `docs/governance/Engagement_Drag_B1_Advisory_v1.0.md` | 90 | historical |
| `90_Return_Probability_Geometry_Spec_v1.0.md` | `docs/archive/governance_specs/Return_Probability_Geometry_Spec_v1.0.md` | 90 | historical |
| `90_cohesion_v2_geometry_exploitability_note.html` | `docs/archive/governance_specs/cohesion_v2_geometry_exploitability_note.html` | 90 | historical |
| `90_v5.0-alpha1_Contact_Hysteresis_Execution_Spec.md` | `docs/archive/governance_specs/v5.0-alpha1_Contact_Hysteresis_Execution_Spec.md` | 90 | historical |
| `90_v5.1-draft-FSR_Engineering_Execution_Spec.md` | `docs/archive/governance_specs/v5.1-draft-FSR_Engineering_Execution_Spec.md` | 90 | historical |
| `90_architecture_governance_submit.md` | `docs/archive/governance_specs/architecture_governance_submit.md` | 90 | historical |

## Separation Rule (APP vs VS)
APP-side mirror includes only canonical docs, standards, and templates.
APP-side mirror excludes runtime output artifacts, including:
- `csv`
- `json`
- timeline files
- event matrices
- digest tables

Those artifacts remain VS-side only under:
- `analysis/engineering_reports/`
- `analysis/exports/`

## Compliance Checklist
1. File renaming or mapping completed: PASS (mapping mode applied in this document).
2. `_standards` folder created or updated: PASS (`DOE_Report_Standard_v1.0.md`, `BRF_Export_Standard_v1.0.md`, `Analysis_Scripts_Index_v1.0.md` present; scripts index updated).
3. Documentation index updated: PASS (`docs/README.md` added).
