# M021-QUERY-PLANNER-AXIS-COMPOSITION - Query planner and axis-provider composition

## Mission

M021

## Goal

Compose typed query capabilities with selected axis-provider capabilities for S015 query planning.

## Acceptance

- Data-scope planning remains possible when visible guides are non-queryable.
- Guide-scope planning rejects providers without `supports_guide_query`.
- Guide text query planning rejects providers without `supports_text_query`.
- All-rendered planning with visible guides rejects providers without guide query support.
- Axis query-scope requirements map to `QueryScope`.
- Rejections include actionable diagnostics naming the missing provider capability.

## Stop conditions

Stop before Matplotlib scoped query execution routing, broad scene planner implementation, or Datoviz
runtime query support.
