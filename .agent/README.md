# .agent

This directory is the repo-local state for the agent-centric workflow.

- `project.json`: project/workflow settings.
- `providers.json`: worker provider configs using `aisw` contexts.
- `status.json`: current stage, missions, questions, and recommendations.
- `missions/`: long autonomous work units.
- `tasks/`: atomic task descriptions.
- `consultations/`: prompts for ChatGPT Pro high-reasoning discussions.
- `runs/`: generated run logs and prompts, ignored by git.

The primary human interface is Codex in natural language. Codex should call `tools/agentctl` under the hood.
