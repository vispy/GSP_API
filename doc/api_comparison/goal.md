# What is a good API

## Target audience
- GSP api is for people using GSP as the backend for their scientific visualization library/application
- it is not for people trying to visualize their data.
- as a point of comparison, in matplotlib world
  - GSP is like the Agg backend
  - not like pyplot

## Goals
- being stable
- being robust
- being consistent
- being easy to understand
  - good documentation

- when it fails, it must fails early and loudly
- no syntaxic sugar
- being minimal
  - only the essential features
  - no convenience functions
- being explicit
- being flexible

## Non-goals
- no syntaxic sugar
- 