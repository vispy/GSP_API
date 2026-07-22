# M252 - S059 Datoviz linear filter promotion

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Draft; depends on M250 and M251.

## Summary

Map the protocol enum to matching Datoviz min/mag field-slot filters and advertise the new renderer
capability only after real offscreen conformance.

## Acceptance

Runtime evidence proves orientation, centers, bilinear interpolation, clamp, color/alpha
multiplication, minification, magnification, and two visuals sharing one texture with different
filters within `2/255`; all existing nearest fixtures remain green.

## Stop Conditions

On any native mismatch, retain the implementation behind an unadvertised capability; do not loosen
the rule, change color semantics, or silently fall back to nearest.
