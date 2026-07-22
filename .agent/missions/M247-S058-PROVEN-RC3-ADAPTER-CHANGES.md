# M247 - S058 proven RC3 adapter changes

## Stage

S058 - Datoviz v0.4-dev Rolling Compatibility And RC3 Feedback

## Status

Completed on 2026-07-22 after the field-slot sampling trigger landed.

## Summary

Implement narrowly proven GSP adapter and capability changes selected by M246 evidence.

## Result

Datoviz commits `f8b75b5e6`, `711ab20dd`, and `be7f2a803` added, runtime-tested, and documented
public field-slot texture sampling. GSP commits `e2008b1`, `fd0710a`, `290e8a7`, and `2c41b80`
implemented the bounded nearest-only Texture2D adapter, capability promotion, current-protocol
example, S051 reconciliation, and repeatable checkpoint.

The checkpoint at Datoviz `be7f2a80354c25e85bab88c85f5ea7340975b569` rendered five of five
Texture2D cases and passed 236 focused tests. Linear GSP filtering remains paused behind P036;
canonical mesh-triangle identity and rich image query payloads remain separate deferred triggers.
