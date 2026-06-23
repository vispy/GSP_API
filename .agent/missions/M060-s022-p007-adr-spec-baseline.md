# M060 - S022 P007 ADR/spec baseline

## Stage

S022 - Remote source family selection and consultation

## Status

Pending.

## Summary

Consume the P007 ChatGPT Pro response and translate the accepted HTTP single-resource `.npy` array
direction into durable ADR and spec updates before implementation begins.

## Planned Deliverables

- ADR accepting HTTP single-resource as the first access architecture test.
- Spec updates for array source contract, `format`, `decoder_id`, materialization target, resolver
  policy, capability fields, diagnostics, cache policy, and fixture strategy.
- Mission Control records for the next no-network/mock implementation missions.

## Stop Condition

Do not implement HTTP fetch, URL parsing, credentials, decoders, network I/O, dynamic loading, or
production remote-source behavior in this mission.
