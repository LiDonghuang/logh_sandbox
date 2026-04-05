# PR6 Old-Family Retirement Round 3 - V3A Debug Context Narrowing

Status: bounded retirement record  
Date: 2026-04-05  
Scope: remove `v3a`-specific debug/export context from default active `v4a` launcher path  
Authority: engineering working record; not broad retirement approval

## 1. Intent

Current launcher-centered cleanup standard is:

- keep only what the current `dev_v2.0` launcher actually uses on the active
  current settings path
- gradually remove old-family human-facing residue from the default path

This round applies that rule to launcher debug/export context.

## 2. What changed

Updated:

- `test_run/test_run_entry.py`

The following fields are now exported into `render_debug_context` only when:

- `movement_model_effective == "v3a"`

Fields:

- `pre_tl_target_substrate`
- `continuous_fr_shaping_effective`
- `continuous_fr_shaping_mode_effective`
- `odw_posture_bias_enabled_effective`
- `odw_posture_bias_k_effective`
- `odw_posture_bias_clip_delta_effective`

They are no longer part of the default active `v4a` launcher debug surface.

## 3. Why this is valid retirement work

Under current active launcher settings:

- movement model is `v4a`
- these fields describe old-family `v3a` behavior or `v3a`-only effective
  mechanisms

So keeping them in the default `v4a` debug/export context would preserve
human-facing old-family noise without representing active behavior.

## 4. Honest classification

This round is:

- `Partial Cleanup`

Reason:

- current launcher-facing debug surface became narrower and more truthful
- no broad mechanism deletion happened yet

## Bottom Line

Round 3 keeps `v3a` support available where explicitly selected, but removes a
cluster of `v3a`-specific debug/export fields from the default active `v4a`
launcher path.
