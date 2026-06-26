# S030 next stage scoping - Datoviz Guide Axis Proof

## Status

S030 opens after S029 closed the backend capability matrix and visual review pack with Datoviz guide
rows still unsupported.

## Selected direction

Run a bounded Datoviz guide-axis proof before changing the GSP capability matrix:

- keep Matplotlib as the strict reference for the semantic guide contract;
- use Datoviz native panel axes only where runtime behavior is directly rendered or probed;
- prove explicit tick values/labels and reversed `View2D` domains before any guide row promotion;
- keep guide/all-rendered query unsupported unless Datoviz exposes guide picking/query semantics;
- do not approximate panel titles, grid placement, or tick labels silently.

## Consultation policy

No ChatGPT Pro consultation is required for the initial proof. Create a consultation packet only if
the Datoviz API needs a public semantic redesign for axis layout, title layout, reversed domains, or
guide query.

## Immediate next missions

| Mission | State | Purpose |
|---|---|---|
| M120 | completed | Runtime proof completed; Datoviz axis APIs render with backend ticks, grid, labels, reversed domains, and explicit facade ticks when MoltenVK is configured. |
| M121 | draft | Wire an axis-only adapted Datoviz guide review path only if title/query gaps stay explicit and production explicit tick wiring is added. |
| M122 | draft | Regenerate review artifacts and promote/defer rows based on M120-M121 evidence. |
