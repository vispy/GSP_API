# M252 - S059 Datoviz linear filter promotion

## Stage

S059 - Texture2D Nearest-Or-Linear Filtering Extension

## Status

Completed.

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

## Result

Mapped `MeshVisual.texture_filter` to matching Datoviz field-slot minification and magnification
filters and separately advertised `meshvisual.texture_filter.linear.v1`. The repeatable S059
checkpoint against local Datoviz `be7f2a80354c25e85bab88c85f5ea7340975b569` rendered all five
nearest regression cases and four linear cases. Eight numeric probes cover orientation, centers,
bilinear interpolation, clamp, multiplication, straight alpha over white, minification,
magnification, and a shared texture with distinct filters; every channel matched exactly (0/255
maximum error versus the allowed 2/255). The checkpoint's focused suite passed 241 tests.
