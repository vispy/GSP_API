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
- per vertex (it is an array equal to the number of vertex)

### How to mix that with groups for materials attributes ?
- in concepts **and** in codes