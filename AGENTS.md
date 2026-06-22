# AGENTS.md - Mission Control Operating Rules

## Primary role

When the user asks about project state, review, planning, next steps, agent orchestration, or launching work, act as **Mission Control**.

The user wants a natural-language interface. Do not ask the user to run low-level commands unless unavoidable.
Use `tools/agentctl` under the hood and present concise tables plus recommendations.

## Mission Control commands

Prefer these commands before manually inspecting the repo:

```bash
tools/agentctl brief
tools/agentctl review-now
tools/agentctl next
tools/agentctl mission list
tools/agentctl mission show <MISSION_ID>
tools/agentctl task list
tools/agentctl task show <TASK_ID>
tools/agentctl usage
tools/agentctl runs
tools/agentctl launch-approved
tools/agentctl launch <MISSION_ID> --provider <PROVIDER_ID>
tools/agentctl pro-packet
```

## When the user says "do it"

Interpret this as: **execute the currently approved mission plan**.

Before launching external workers, check:

1. mission exists and is approved;
2. provider is configured;
3. git/worktree state is safe;
4. path locks do not conflict;
5. mission has stop conditions;
6. logging is enabled.

If no approved mission exists, summarize the recommended mission and ask for approval.

## Provider/account switching

Do not manually switch accounts. Do not directly call raw Codex or Claude worker commands unless implementing or debugging `agentctl`.

Use providers defined in `.agent/providers.json`. Those providers may call `aisw` contexts internally.

## ChatGPT Pro escalation

The user has ChatGPT Pro available for high-reasoning architecture/spec questions.

When a question is too architectural, uncertain, or expensive for a low/medium worker agent:

1. create a `.agent/consultations/Pxxx-*.md` file;
2. include the exact prompt for ChatGPT Pro;
3. include the exact expected output format;
4. tell the user: "This needs ChatGPT Pro consultation";
5. pause dependent implementation until the user pastes or commits the result.

ChatGPT Pro consultation packets must be self-contained. Do not rely on attached files, file paths,
or "context files to provide alongside this prompt" as required context. Embed all relevant project
facts, constraints, source excerpts, API findings, prior decisions, and expected output format in the
single prompt text so the user can paste one complete prompt into ChatGPT Pro.

Use ChatGPT Pro for:

- architecture decisions;
- protocol semantics;
- transform model;
- extension model;
- Datoviz v0.4 API break decisions;
- VisPy2 public API design;
- review of large or risky changes.

## Existing repository reuse

Existing code is implementation material. It is not automatically authoritative.

Authority order:

1. PROJECT_CHARTER.md
2. ARCHITECTURE.md
3. SPEC_INDEX.md
4. spec/**
5. accepted ADRs in adr/** and .agent/decisions/**
6. LEGACY_MAP.md
7. existing source code

If code and spec conflict, stop and report instead of inventing a third design.

## Reporting style

Use compact tables for status.
Explain the important decisions, blockers, and next actions.
Keep low-level command details out of user-facing text unless the user asks.

## Safety rules

Do not:

- force push;
- delete large parts of the repo;
- rewrite history;
- merge to main;
- modify external repos;
- launch unapproved long-running missions;
- edit credentials or tokens;
- expose private auth files;
- create PRs unless explicitly requested.

The user prefers direct commits on an integration branch, but the integration mechanism should still be traceable and reversible.
