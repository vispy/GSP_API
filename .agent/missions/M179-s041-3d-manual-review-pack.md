# M179 - S041 3D manual review pack

## Stage

S041 - 3D Manual Review Pack

## Status

Completed by local-main-codex.

## Summary

Add a focused review pack for manual Matplotlib-vs-Datoviz inspection of the current public 3D
stack, including lit meshes and Matplotlib arcball-style View3D navigation.

## Deliverables

- New numbered 3D review example covering a richer lit mesh with S039/S040 Lambert semantics.
- Review README updates for Matplotlib/Datoviz 3D comparison commands.
- Clear boundary wording for public GSP orbit navigation versus native Datoviz arcball demos.
- Focused validation that the new example renders through Matplotlib and reports structured Datoviz
  status.

## Acceptance

- Manual reviewer can launch Matplotlib and Datoviz side by side for the lit mesh.
- Matplotlib live mode supports orbit/pan/zoom/reset through existing View3D navigation.
- Datoviz review path uses public View3D plus CPU-resolved Lambert, not native lighting.
- Documentation no longer says Datoviz Lambert is unsupported after S040.

## Stop Condition

Stop if the review pack would require exposing native Datoviz arcball or lighting APIs as public GSP
semantics.

## Result

Completed. Added the lit View3D mesh review example, updated S040 Lambert review wording, documented
3D side-by-side and arcball-style Matplotlib review commands, and recorded the local Datoviz camera
binding gap as structured unsupported review status.
