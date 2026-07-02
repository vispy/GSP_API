# M201 - S050 Datoviz query and readback parity scoping

## Stage

S050 - Post-S048 Implementation Roadmap And Datoviz Mesh-Pick Evidence

## Status

Completed by local-main-codex.

## Summary

After M200, scope the next Datoviz query/readback parity mission. Candidate targets include live
point/image payload completeness, guide/all-rendered query boundaries, `hit_policy=all`, extension
payload policy, and scientific/raw readback decisions.

## Stop Conditions

- Stop if M200 reports that Datoviz API work must happen first.
- Stop before introducing new query semantics without a ChatGPT Pro consultation packet.

## Result

Completed locally. See `.agent/S050_QUERY_READBACK_SCOPING.md`.

Decision: M200 blocks only mesh-triangle picking promotion. Datoviz query/readback work can continue
for documentation/status cleanup, capability-gated guide/all-rendered query clarity, and live
point/image payload evidence. New public query/readback semantics and scientific readback remain out
of scope without consultation.
