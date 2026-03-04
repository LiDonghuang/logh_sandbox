# Phase VII-3 Mismatch Root Cause - FR5_MB2_PD5 side B

## Case Facts
- case_id: `FR5_MB2_PD5`
- side: `B`
- first_contact_tick: `107`
- cut_tick_geom: `83`
- cut_tick_tactical: `N/A`
- threshold/sustain: `theta_split=1.715`, `S=20`

## Post-contact Sustain Check
- split condition true count after contact: `40` ticks
- max tactical sustain after contact: `14`
- does split remain true for >=S ticks after contact: `false`
- post-contact in_contact gate-open ratio: `1.000`

## Root-cause Label
`RC2: split did not persist long enough after contact (sustain not met)`

## Supporting Tick Window
| tick | split_cond | sustain_geom | in_contact_count | sustain_tactical |
| --- | --- | --- | --- | --- |
| 108 | 1 | 45 | 13 | 2 |
| 109 | 1 | 46 | 21 | 3 |
| 110 | 1 | 47 | 27 | 4 |
| 111 | 1 | 48 | 41 | 5 |
| 112 | 1 | 49 | 49 | 6 |
| 113 | 1 | 50 | 62 | 7 |
| 114 | 1 | 51 | 76 | 8 |
| 115 | 1 | 52 | 85 | 9 |
| 116 | 1 | 53 | 89 | 10 |
| 117 | 1 | 54 | 104 | 11 |
| 118 | 1 | 55 | 107 | 12 |
| 119 | 1 | 56 | 105 | 13 |
| 120 | 1 | 57 | 107 | 14 |
| 121 | 0 | 0 | 106 | 0 |
| 122 | 0 | 0 | 102 | 0 |
| 123 | 0 | 0 | 106 | 0 |
| 124 | 1 | 1 | 105 | 1 |
| 125 | 1 | 2 | 109 | 2 |
| 126 | 1 | 3 | 111 | 3 |
| 127 | 1 | 4 | 111 | 4 |
| 128 | 0 | 0 | 116 | 0 |
