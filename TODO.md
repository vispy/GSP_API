- implement path in matplotlib + datoviz
  - issue to mix the multiple paths and the groups attributes
- test dynamic group in datoviz pixels
- for each example, `_matplotlib` `_datoviz` and `_both`
  - have a test_runner ?
- when datoviz core dump, DVZ_LOG_LEVEL=0
  - when creating a datoviz app with 350 pixel, there is a segfault
- DONE implement points in datoviz
- handle the animation loop
  - API from datoviz
  - API from matplotlib
  - GSP API common

---
# Groups are bogus
- find a way to make that regular
- was supposed to be 'one opengl call per group'
  - isnt that collection ?
  - what if we do `visual` and `visualCollection` ?


## Implemented 'all material' are expressed by group
- issue with paths
- path(positions, path_sizes, colors, line_widths, groups)
  - colisions between `path_sizes` and `groups`
  - `path_sizes` is not a material attribute tho. 


## set_attribute suppose to be
the attribute can be set (QUESTION)
- individually (like single value)
- per group (it is an array equal to the number of group)
- per vertext (it is an array equal to the number of vertex)

### How to mix that with groups for materials attributes ?
- in concepts **and** in codes