# Lifecycle and transport API

Initialization negotiates protocol 0.2 and returns an immutable capability snapshot. Commands are
sequenced, acknowledgements are structured, and a closed in-process transport rejects later work.
Production network framing is outside the current implementation claim.

::: gsp.protocol.transports
    options:
      members: true
      show_source: false

::: gsp.protocol.commands
    options:
      members: true
      show_source: false

::: gsp.protocol.capabilities.CapabilitySnapshot
    options:
      show_source: false
