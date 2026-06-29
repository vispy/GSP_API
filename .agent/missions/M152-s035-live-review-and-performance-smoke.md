# M152 - S035 live review and performance smoke

## Stage

S035 - Retained View2D Navigation and Pan/Zoom

## Status

Ready.

## Summary

Add a live pan/zoom review example and performance smoke after protocol and backend retained-update
paths are in place.

## Deliverables

- Live review example where drag/wheel native events adapt to S035 semantic navigation actions.
- Matplotlib and Datoviz review commands where supported.
- Performance smoke that records frame/update counts and verifies stable visual-buffer upload counts
  during navigation.
- Documentation for supported and unsupported live-input paths.

## Stop Condition

Stop before claiming interactive support if the Datoviz retained-update proof is absent.
