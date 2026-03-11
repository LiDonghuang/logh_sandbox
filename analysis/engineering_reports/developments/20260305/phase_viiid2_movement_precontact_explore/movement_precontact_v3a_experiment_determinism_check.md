# Movement Pre-contact V3A Experiments Determinism Check

- Case: FR8_MB8_PD5 vs first opponent
- Runtime decision source fixed: `v2`

| model | v3a_experiment | rep1 | rep2 | pass |
| --- | --- | --- | --- | --- |
| v3a | base | `a1cd03c6c7635003806c9988b1b97382e28aa69cfcc7f8c06706a57e144a948e` | `a1cd03c6c7635003806c9988b1b97382e28aa69cfcc7f8c06706a57e144a948e` | True |
| v3a | exp_a_reduced_centroid | `0a080c0efa899fa9fa2d10d464308e64c1be794411e824577ed212bb02802dcf` | `0a080c0efa899fa9fa2d10d464308e64c1be794411e824577ed212bb02802dcf` | True |
| v3a | exp_b_distance_capped | `313279471c87ee8916ec17f6abc79d4e08b188fca89183a2278f226c308863d7` | `313279471c87ee8916ec17f6abc79d4e08b188fca89183a2278f226c308863d7` | True |
| v3a | exp_c_frame_translation | `17f85ee9dc74e4cbcedb9a8922da498cac038c6fbc4a5222572730bc0657a0bc` | `17f85ee9dc74e4cbcedb9a8922da498cac038c6fbc4a5222572730bc0657a0bc` | True |