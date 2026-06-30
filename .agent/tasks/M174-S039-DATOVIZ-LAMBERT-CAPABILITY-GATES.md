# M174 - S039 Datoviz Lambert Capability Gates

Add Datoviz capability gates and diagnostics for accepted S039 flat Lambert semantics.

## Required

- Reject or adapt `flat_lambert` explicitly when exact S039 support is unavailable.
- Keep unlit mesh rendering unchanged.
- Do not expose Datoviz material structs, shader slots, Vulkan state, or backend-native light names.
- Add focused tests for capability/diagnostic behavior.

## Stop Conditions

- Stop if strict support would require widening public S039 semantics.
- Stop if native Datoviz Lambert behavior cannot match S039 exactly and no adapted path is clearly
  diagnosed.
