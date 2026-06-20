# GSP Resources - Draft

Resource kinds:

- buffer;
- texture;
- sampled field;
- virtual data source;
- parameter block;
- external/live resource handle.

A buffer resource should eventually carry:

- id;
- dtype;
- shape;
- byte length;
- usage;
- mutability;
- locality;
- update ranges;
- optional external source.

Open v0.1 question: whether to support arbitrary strides immediately or require contiguous buffers first.
