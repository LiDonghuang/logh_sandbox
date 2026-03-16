# FR Authority DOE Determinism Check

- Expected runs: `972`
- Actual runs: `972`
- Seed profiles: `18`
- Fixed-seed discipline: `random_seed`, `background_map_seed`, and `metatype_random_seed` are explicit for every run.
- Duplicate `(FR, MB, PD, ODW, seed_profile_id)` combos: `0`
- Unique DOE cells: `54`
- Unique final-state digests: `54`
- Digest interpretation: `Unique digests equal unique DOE cells, which indicates seed profile variation is behaviorally inert under this controlled synthetic setup.`
- Interpretation: this is a fixed-seed coverage check, not a repeated-rerun determinism proof.

## Reproduction Command

```powershell
python analysis/engineering_reports/developments/20260311/phase_fr_authority_audit/run_fr_authority_doe.py
```
