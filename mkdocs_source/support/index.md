# Reading support tables

Protocol acceptance, producer support, rendering, and queries are separate questions.

1. **Protocol:** Is the record and its validation contract accepted?
2. **Producer:** Can VisPy2 emit it?
3. **Renderer:** Can this backend execute the exact requested scope?
4. **Query:** Can the backend return the requested payload?

The tables summarize repository evidence, but a live session's `CapabilitySnapshot` is the final
authority. “Strict” applies only to the scope stated in a row.
