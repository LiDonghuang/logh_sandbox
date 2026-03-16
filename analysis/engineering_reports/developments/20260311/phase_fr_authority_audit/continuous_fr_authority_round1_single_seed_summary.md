# Continuous FR Authority Shaping Round 1 Single-Seed DOE

- Scope: single-seed expanded continuous shaping screen on the locked v3a centroid-restoration suspect path.
- Frozen layer impact: none.
- Independence: this batch is isolated from the aborted multi-seed partial outputs.
- Baseline anchor: `fr_authority_doe_run_table.csv` filtered to the round-1 cells and `SP01` only.
- Candidate count: `126`.
- Candidate runs written: `2772`.
- Hard-constraint passes: `0`.
- Seeds: `SP01`.
- Candidate C keeps `beta=1.5` fixed.
- Ranking status: `advisory-only`; no automatic finalist decision is made by this script.

## Output Files
- `continuous_fr_authority_round1_single_seed_run_table.csv`
- `continuous_fr_authority_round1_single_seed_candidate_summary.csv`
- `continuous_fr_authority_round1_single_seed_ranked_candidates.csv`
- `continuous_fr_authority_round1_single_seed_hard_constraints.csv`
- `continuous_fr_authority_round1_single_seed_summary.md`

## Resume Behavior

- `continuous_fr_authority_round1_single_seed_run_table.csv` also serves as the checkpoint file.
- Re-running the script resumes from existing `run_id` rows in the single-seed family only.
- The aborted multi-seed run table is not read by this script and does not participate in scoring.

## Expanded Grid
- Family A: `a x sigma x q = 6 x 3 x 3 = 54`
- Family B: `a x sigma x beta = 6 x 3 x 2 = 36`
- Family C: `a x sigma x gamma = 6 x 3 x 2 = 36`
- Total: `126` candidates

## Top Ranked Candidates

| Rank | Candidate | Pass | Sentinel dWin | ODW dFireEff | PD Selectivity | MB Shoulder | Smoothness |
| --- | --- | --- | --- | --- | --- | --- | --- |
| 1 | A_a065_s010_q3 | False | 50.00 | -0.0510 | 50.00 | 0.00 | -0.5500 |
| 2 | C_a055_s020_g08_b15 | False | 50.00 | -0.0642 | 33.33 | -50.00 | -0.4600 |
| 3 | A_a065_s015_q3 | False | 50.00 | -0.1038 | 83.33 | 0.00 | -0.5000 |
| 4 | B_a065_s010_b15 | False | 50.00 | -0.0719 | 16.67 | -50.00 | -0.5800 |
| 5 | A_a035_s015_q3 | False | 50.00 | -0.0728 | 66.67 | -100.00 | -0.2000 |
| 6 | A_a015_s010_q2 | False | 50.00 | -0.0879 | 0.00 | 50.00 | -0.0500 |
| 7 | B_a025_s010_b15 | False | 0.00 | -0.0525 | 0.00 | 0.00 | -0.1800 |
| 8 | B_a045_s015_b15 | False | 0.00 | -0.0567 | 33.33 | 0.00 | -0.3300 |
| 9 | B_a045_s010_b15 | False | 0.00 | -0.0597 | 33.33 | -50.00 | -0.3800 |
| 10 | C_a045_s010_g08_b15 | False | 0.00 | -0.0687 | 16.67 | 0.00 | -0.4600 |

## Reproduction Command

```powershell
python analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_continuous_fr_authority_round1_single_seed_doe.py
```
