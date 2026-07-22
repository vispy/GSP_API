# S058 Datoviz v0.4-dev rolling compatibility and RC3 feedback

Date: 2026-07-22

## Objective

Keep GSP aligned with the local Datoviz `v0.4-dev` branch while Datoviz advances from RC2 toward
RC3. Treat the exact sibling checkout revision as the runtime authority; do not substitute the RC2
wheel or require compatibility with the immutable RC2 artifact.

## Approved sequence

| Mission | State | Scope |
|---|---|---|
| M245 | in progress | Replay the maintained Datoviz probe, visual/query matrix, public session examples, and repeated lifecycle evidence against the exact local `v0.4-dev` revision. |
| M246 | draft | Classify unchanged, improved, regressed, and newly available behavior; prepare minimal Datoviz handoffs for failures. |
| M247 | draft | Implement narrowly proven GSP adapter or capability changes selected by M246 evidence. |
| M248 | draft | Add a repeatable rolling-development checkpoint and close the stage with the next RC3 recommendation. |

## Priorities after baseline

1. Texture2D mesh sampling semantics if the Datoviz RC3 candidate work lands.
2. Canonical mesh triangle identity queries.
3. Live image texel, displayed-color, and value payloads.
4. Guide/View2D strictness and crash-free offscreen execution.
5. Retained session lifecycle and update behavior.

## Guardrails

- Record the exact Datoviz commit and imported module path for every native evidence run.
- Do not edit the sibling Datoviz repository during M245.
- Do not promote a capability from symbol presence or synthetic ctypes evidence alone.
- Keep GSP 0.2 publication and Datoviz dependency pinning outside this stage.
- Stop on unisolated native crashes, provenance mismatch, or a protocol/spec conflict.

## Approval

The project owner approved this plan in the active Mission Control conversation on 2026-07-22.
