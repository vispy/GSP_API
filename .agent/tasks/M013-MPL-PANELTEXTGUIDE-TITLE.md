# M013-MPL-PANELTEXTGUIDE-TITLE - Render semantic panel title

## Mission

M013

## Goal

Render `PanelTextGuide(role=title)` as a Matplotlib title.

## Acceptance

- Title text comes from `PanelTextGuide`.
- No pixel-perfect font/layout assertions are introduced.
- Existing point/image rendering still works.

## Stop conditions

Stop if title behavior requires a general layout engine.

