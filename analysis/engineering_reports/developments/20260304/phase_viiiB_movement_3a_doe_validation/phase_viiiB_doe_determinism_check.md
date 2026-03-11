# Phase VIII-B Determinism Check

- Case: FR8_MB8_PD5
- Pair: bittenfeld vs grillparzer

## Per-model digest equality
- v1 run1: `74dd0569e2823a9dcead4557794b78a7326248f8484a457c9c24e07c8754ac28`
- v1 run2: `74dd0569e2823a9dcead4557794b78a7326248f8484a457c9c24e07c8754ac28`
- v1 PASS: `True`
- v3a run1: `b05fa47c73dc4190c067cb1452a4669b57d378f0018dea5edee3f4fea922760a`
- v3a run2: `b05fa47c73dc4190c067cb1452a4669b57d378f0018dea5edee3f4fea922760a`
- v3a PASS: `True`

## Runtime code immutability during DOE
Hashes before vs after DOE execution:
- `runtime/engine_skeleton.py`: before=`7de7279338af0b6f8a71fe8620a3454bf47e50daf6069be41ccee8b5c214fdd9` after=`7de7279338af0b6f8a71fe8620a3454bf47e50daf6069be41ccee8b5c214fdd9` unchanged=`True`
- `analysis/test_run_v1_0.py`: before=`45ead81d7dfb2df65c18b0ec544dcdaa59e331c592b1610b882b05b7dc7f7d78` after=`45ead81d7dfb2df65c18b0ec544dcdaa59e331c592b1610b882b05b7dc7f7d78` unchanged=`True`
- `runtime_v0_1.py`: before=`35ded2c7c53c139bf68612491691bd85b6f1281873e270620c049795937eaf91` after=`35ded2c7c53c139bf68612491691bd85b6f1281873e270620c049795937eaf91` unchanged=`True`