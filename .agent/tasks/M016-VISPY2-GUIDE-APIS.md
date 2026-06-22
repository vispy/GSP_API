# M016-VISPY2-GUIDE-APIS - VisPy2 guide API surface

## Mission

M016

## Goal

Add public VisPy2 APIs for labels, title, explicit ticks, and grid intent.

## Acceptance

- Public methods emit semantic `AxisGuide`, `TickSpec`, and `PanelTextGuide` state.
- Matplotlib reference rendering consumes that state.
- Guide APIs do not add generated guide visuals to `Figure.visuals()`.

## Stop conditions

Stop before exposing backend-provider details or broad Matplotlib compatibility.
