# M201 - S050 Datoviz query and readback parity scoping

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Blocked pending Datoviz mesh triangle query API work.

## Summary

After M200, scope the next Datoviz query/readback parity mission. Candidate targets include live
point/image payload completeness, guide/all-rendered query boundaries, `hit_policy=all`, extension
payload policy, and scientific/raw readback decisions.

## Stop Conditions

- Stop if M200 reports that Datoviz API work must happen first.
- Stop before introducing new query semantics without a ChatGPT Pro consultation packet.

## Blocker

M200 reported that Datoviz upstream API work is required before GSP can implement or advertise
native View3D mesh triangle picking. See `.agent/S050_DATOVIZ_MESH_PICK_EVIDENCE.md` and
`.agent/S050_DATOVIZ_MESH_TRIANGLE_QUERY_HANDOFF.md`.
