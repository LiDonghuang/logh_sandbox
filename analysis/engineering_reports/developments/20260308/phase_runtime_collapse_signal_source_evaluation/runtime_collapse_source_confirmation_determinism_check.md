# Runtime Collapse Source Confirmation Determinism Check

- Representative case: `FR5_MB5_PD5` vs `reinhard`, seed `SP01`

| source | attempt | determinism_digest |
| --- | ---: | --- |
| v2 | 1 | `fc36ed4fc3d2cf8dc309a7b1d416e1a9cb80b38b0cd9f01b4ae4bd1583ac5b42` |
| v2 | 2 | `fc36ed4fc3d2cf8dc309a7b1d416e1a9cb80b38b0cd9f01b4ae4bd1583ac5b42` |
| v3_test | 1 | `b0ed0cc1c4597c4d2bc9d152bf828a9f9d0dacfb9161054588277807594b62e7` |
| v3_test | 2 | `b0ed0cc1c4597c4d2bc9d152bf828a9f9d0dacfb9161054588277807594b62e7` |

- `v2` equal: **True**
- `v3_test @ 1.1` equal: **True**