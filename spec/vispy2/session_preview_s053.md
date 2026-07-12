# VisPy2 experimental session preview boundary

Status: implementation-ready draft from S053 evidence; not implemented by M235.

The first session preview may expose only:

```python
with vp.open_session("datoviz") as session:
    plan = session.inspect(fig, operation="display")
    plan.require_executable()
    display = session.show(fig, block=True)
```

An explicit session may additionally expose a bounded `poll()` operation implemented through one
Datoviz frame per call. Non-blocking or polled execution must require explicit session ownership.
The preview must expose capabilities and immutable diagnostics, close idempotently, reject all
operations after close, and preserve native failures as backend execution errors.

The preview must not add backend selection to `subplots()`, store backend state on `Figure`, change
the default bare `Figure.show()`, expose native handles, or promise backend parity. It must not yet
expose retained visual-data mutation, user-close callbacks, generic `Display.update()`, or event-loop
embedding as stable behavior.
