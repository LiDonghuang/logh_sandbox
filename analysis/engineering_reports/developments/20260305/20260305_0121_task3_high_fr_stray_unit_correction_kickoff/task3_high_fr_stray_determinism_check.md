# Task3 High-FR Stray Determinism Check

- Case: `FR8_MB8_PD5_DET`
- Fixed opponent: `first6[0]` = `reinhard` (assumption for deterministic repeatability)
- Rule: identical config repeated runs must produce identical digest within each model

## Results
- v1: PASS
  - `task3_FR8_MB8_PD5_DET_vs_reinhard_v1_det01` -> `7139147e3db2c894223cde657eee5bfcfeaff08be6fbff2ea3d0e99a8617ccef`
  - `task3_FR8_MB8_PD5_DET_vs_reinhard_v1_det02` -> `7139147e3db2c894223cde657eee5bfcfeaff08be6fbff2ea3d0e99a8617ccef`
- v3a: PASS
  - `task3_FR8_MB8_PD5_DET_vs_reinhard_v3a_det01` -> `9a4a15a7ec44521309d990cf7dc4d315d79717d97c079297670e3362405a868e`
  - `task3_FR8_MB8_PD5_DET_vs_reinhard_v3a_det02` -> `9a4a15a7ec44521309d990cf7dc4d315d79717d97c079297670e3362405a868e`
