# Governance Report: TL Boundary Discussion Request

Date: 2026-03-13
Status: Engineering report for governance discussion
Authority requested: Governance review and human-governance discussion
Scope: Fleet-level direction-surrogate responsibility boundary relative to future `TL`

## 1. Purpose

This report does **not** request implementation authorization.

Its purpose is narrower:

- notify governance that the current post-contact low-level symmetry audit has reached a topic that materially overlaps with future `TL` responsibility
- request that governance discuss this boundary with the human architect before engineering is directed further

## 2. Current trigger

During the mirrored close-contact symmetry audit, engineering traced an important part of early contact-entry asymmetry to the current fleet-level direction surrogate used in `evaluate_target()`.

Current diagnostic evidence indicates:

- raw `nearest-enemy` is too sharp for mirrored diagnostic neutrality
- smoother local surrogates, especially `nearest-5 centroid`, appear more neutral in the audited mirrored window
- fully global `enemy centroid` is cleaner on pure symmetry, but likely too global to be assumed correct without a design decision

This raises a responsibility question:

> Who should legitimately own the choice of fleet-level enemy-reference logic?

Engineering judgment is:

- semantically, that responsibility is much closer to future `TL`
- but low-level runtime still needs some default surrogate today

## 3. Why governance should discuss this with human first

This is not just a local implementation tweak.

It has implications for:

- authority allocation
- substrate neutrality
- future `TL` semantics
- the boundary between low-level diagnostic defaults and later personality-controlled targeting behavior

If engineering moves too far alone, there is risk of:

- silently predesigning `TL`
- silently reallocating targeting authority
- or choosing a default surrogate that later constrains future `TL` design

That decision should not be made implicitly inside a low-level symmetry audit.

## 4. Engineering position

Engineering does **not** propose opening `TL` now.

Engineering also does **not** propose freezing any one surrogate as the future permanent answer.

Engineering instead proposes the following discussion framing:

1. Future `TL` should own targeting-preference semantics.
2. Current low-level audit may still judge whether the present default surrogate is too sharp and too symmetry-sensitive to remain a neutral pre-TL default.
3. Therefore the current work should be understood as substrate preparation, not early `TL` activation.

## 5. Question for governance + human discussion

Engineering asks governance to discuss with the human architect the following boundary question:

> Should the current post-contact low-level audit be allowed to identify and recommend a more neutral default fleet-level direction surrogate for mirrored diagnostics, while explicitly stopping short of defining future `TL` behavior?

Related sub-questions:

1. Is it acceptable for engineering to continue bounded comparison among surrogate families purely as pre-TL substrate audit?
2. Should mirrored-diagnostic default surrogate neutrality be treated as a legitimate low-level concern, distinct from future `TL` semantics?
3. Does governance want a formal rule that future `TL` remains the owner of targeting-preference semantics, even if low-level default surrogate cleanup proceeds earlier?

## 6. Current requested governance action

Requested action is only:

- discuss this boundary with the human architect
- then return guidance on how far engineering may continue this surrogate-family audit without crossing into premature `TL` design

No implementation request is being made at this stage.

## 7. Bottom line

Current engineering judgment is:

- this is a real architecture-boundary issue
- not a minor local coding detail
- and it should be discussed by governance and human before engineering is directed further

That is why this report is being raised now.
