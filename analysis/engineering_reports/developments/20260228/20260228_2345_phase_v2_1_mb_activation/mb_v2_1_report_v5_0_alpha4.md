# Engineering Report v1.0 - Phase V2.1 Mobility Bias Canonical Mapping Activation
Engine Version: v5.0-alpha4
Modified Layer: Movement (`integrate_movement`, pre-normalization, non-cohesion maneuver only)
Affected Parameters: mobility_bias (archetype canonical mapping) + attack_range stage default anchor=5.0
New Variables: none
Cross-Dimension Coupling: none
Mapping Impact: mobility_bias promoted to Canonical-Active
Governance Impact: minor structural upgrade (movement-only)
Backward Compatible: yes (`mobility_bias=5` baseline-equivalent)

Validation Summary:
1. Determinism (all 9 cases): True
2. mobility_bias=5 bitwise regression vs alpha3 baseline: True
3. Mirror gate (<= +5%): False
4. Jitter gate (<= +10%): False
5. No new attractor proxy: True
6. Runtime overhead <= +10%: False (max 18.44%)

Matrix Snapshot (FR x MB on Fleet A; Fleet B neutral FR=5 MB=5):
- FR=2, MB=2: crossing=False, FFC mean/p90=0.2164/0.2696, orbit_ratio=0.2712, mirror=0.013214, jitter=4515, survivors A/B=37/31, first_contact=107
- FR=2, MB=5: crossing=False, FFC mean/p90=0.2353/0.3263, orbit_ratio=0.3069, mirror=0.320790, jitter=4048, survivors A/B=31/40, first_contact=107
- FR=2, MB=8: crossing=True, FFC mean/p90=0.2077/0.3058, orbit_ratio=0.3328, mirror=0.036364, jitter=5847, survivors A/B=25/30, first_contact=108
- FR=5, MB=2: crossing=False, FFC mean/p90=0.2269/0.3000, orbit_ratio=0.3297, mirror=0.283333, jitter=6391, survivors A/B=30/20, first_contact=104
- FR=5, MB=5: crossing=True, FFC mean/p90=0.2229/0.3098, orbit_ratio=0.3616, mirror=0.080000, jitter=6207, survivors A/B=26/24, first_contact=105
- FR=5, MB=8: crossing=False, FFC mean/p90=0.2281/0.3557, orbit_ratio=0.4037, mirror=0.089325, jitter=7230, survivors A/B=27/24, first_contact=102
- FR=8, MB=2: crossing=False, FFC mean/p90=0.2422/0.3185, orbit_ratio=0.3968, mirror=0.272370, jitter=8100, survivors A/B=15/34, first_contact=99
- FR=8, MB=5: crossing=True, FFC mean/p90=0.2448/0.3686, orbit_ratio=0.4133, mirror=0.478006, jitter=7070, survivors A/B=30/25, first_contact=101
- FR=8, MB=8: crossing=False, FFC mean/p90=0.2541/0.3784, orbit_ratio=0.4301, mirror=0.275349, jitter=7407, survivors A/B=25/32, first_contact=99

Artifacts:
- mb_v2_1_matrix_metrics_v5_0_alpha4.csv
- mb_v2_1_summary_v5_0_alpha4.json
