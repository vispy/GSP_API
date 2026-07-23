# S065 decision - camera and visual release boundary

Date: 2026-07-23

Status: accepted by explicit project-owner direction.

## Decision

Before the first experimental release, prioritize a powerful high-level 3D camera and broad visual
coverage. Implement pixel, sphere, straight vector, bounded generic primitive, and hardened text.
Keep low-level glyph and volume support deferred. Add only the minimal durable public query entry
point; comprehensive picking is not a release blocker.

The implementation contract is `.agent/S065_TECHNICAL_BASELINE.md`. This decision supersedes the
earlier assumption that the migrated 2D producer slice was feature-complete enough to proceed
directly to release preparation.

## Consequences

- S065 is a feature-completeness stage before the product-quality/release audit.
- Datoviz remains the flagship GPU target; Matplotlib remains the reference/adaptation target.
- New GSP visual records remain semantic and backend-neutral.
- Release work stays separately authorized after human gallery and camera review.

