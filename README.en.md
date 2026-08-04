# Agent Native Init

English | [简体中文](README.md)

Agent Native Init is a portable Agent collaboration initialization protocol.

Its goal is not to generate a fixed tech-stack application template, but to give any project a stable layer of Agent collaboration capability: entry rules, project memory, task governance, acceptance gates, handoff, reusable workflows, and a collaboration profile.

## What this project solves

When developing with AI Agents over the long term, the common problems are rarely "the Agent can't write code". They are:

- A new session does not know the project's current state;
- The Agent has no clear authorization boundary;
- A task can't be handed off mid-way;
- Tests pass, but acceptance is never closed;
- Important decisions are scattered across chat logs;
- Context breaks when switching between multiple Agents or tools;
- Every project has to re-negotiate a set of collaboration rules from scratch.

Agent Native Init converges these conventions into a single project-level initialization protocol, so that once an Agent enters a project it knows:

- What context to read first;
- How to judge task level and authorization level;
- Which files carry runtime state, decisions, and handoff;
- When a task file must be created;
- How to verify that a task is complete;
- Which collaboration preferences can be captured, and which must not override hard rules.

## Core artifacts

The truly portable core of this repo falls into two categories:

```text
init/
skills/
```

`init/` is the protocol source directory. It maintains the complete design and initialization flow of Agent Native Init.

`skills/` contains self-contained, directly installable Skill packages. Distilled from the `init/` protocol source, each package bundles the main workflow, a condensed protocol reference, the auto-synced authoritative protocol snapshot, and copy-ready templates. It does not depend on this repo's local path.

The `AGENTS.md`, `vault/`, `app/`, `tests/`, etc. in the repo root are validation artifacts that the current sandbox generates according to the protocol — they are not the migration source.

If you only want to install a self-contained Skill rather than migrate the full protocol source, use:

```text
skills/agent-native-init/
skills/agent-native-init-zh/
```

`agent-native-init` is the English version, `agent-native-init-zh` is the Chinese version.

## Directory structure

```text
init/
  INIT.md                         # initialization entry checklist
  protocol/
    README.md                     # protocol module overview
    00-overview.md                # positioning and layering
    10-vault.md                   # project memory system
    20-governance.md              # task governance, authorization, acceptance
    30-agent-entry.md             # Agent entry file rules
    40-skills.md                  # reusable workflows
    50-engineering-constraints.md # engineering constraints
    60-initialization-flow.md     # new-project initialization flow
    70-adoption-flow.md           # existing-project adoption flow
    80-execution-patterns.md      # agentic execution patterns
    90-collaboration-profile.md   # evolvable collaboration profile
    profiles/
      go-backend.md               # Go backend profile
      python-backend.md           # Python backend minimal profile
skills/
  agent-native-init/               # self-contained open-source Skill package
  agent-native-init-zh/            # self-contained open-source Skill package (Chinese)
scripts/
  agent-init.py                    # helper script for adopting a target project
  sync-skills.py                   # mirrors init/ into the Skill distribution packages
.github/workflows/
  skill-sync.yml                   # checks that the protocol source and Skill snapshots agree
```

## Usage

### New project initialization

In the target project, have the Agent read:

```text
init/INIT.md
init/protocol/README.md
init/protocol/60-initialization-flow.md
```

If the project type is already known, also read the matching profile, for example:

```text
init/protocol/profiles/python-backend.md
init/protocol/profiles/go-backend.md
```

The Agent should generate its own, according to the protocol, in the target project:

- Agent entry file, e.g. `AGENTS.md`;
- `vault/` project memory system;
- `vault/governance.md` collaboration governance rules;
- `vault/tasks/` task-contract rules;
- `skills/` reusable workflows;
- project source, tests, and dependency files as needed.

### Adopting an existing project

If the target project already exists and you only want to add the Agent collaboration layer, have the Agent read:

```text
init/INIT.md
init/protocol/README.md
init/protocol/70-adoption-flow.md
```

Adoption mode creates or updates only the Agent collaboration layer by default:

- Agent entry file;
- `vault/`;
- `skills/`;
- an optional, very short README collaboration note.

Do not modify business source, dependencies, tests, build, deployment, or CI configuration unless the user explicitly authorizes it.

### Using the open-source Skill packages

If your Agent environment supports installing Skills, you can install or copy one of these directories as a Skill package:

```text
skills/agent-native-init/
skills/agent-native-init-zh/
```

When the Skill is used, the Agent generates or merges the following into the target project according to the package's references and templates:

- Agent entry file;
- `vault/` project memory;
- task-contract governance;
- handoff and collaboration profile;
- `skills/agent-task/SKILL.md` starter workflow.

This Skill is suited for cross-project reuse; the full `init/protocol/` is better suited for continuing to design and maintain the protocol itself. Each Skill's `references/protocol-source/` is an authoritative snapshot generated from `init/` — do not edit it directly.

### Installing the Skill via Codex

The recommended approach is to use Codex's built-in `skill-installer` to install this Skill directly from the GitHub repository. You do not need to clone this repo — you only need Codex installed locally and access to GitHub.

Chinese version:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zlin101/agent-init \
  --path skills/agent-native-init-zh
```

English version:

```bash
python3 "${CODEX_HOME:-$HOME/.codex}/skills/.system/skill-installer/scripts/install-skill-from-github.py" \
  --repo zlin101/agent-init \
  --path skills/agent-native-init
```

Restart Codex after installing so the new Skill takes effect.

An installed Skill does not auto-upgrade from the GitHub repository. After a new release, existing users must remove the old local Skill directory and reinstall; the Codex installer refuses to overwrite an existing directory by default. Before reinstalling, confirm the local Skill directory has no custom modifications you want to keep.

If the repository has not been pushed to GitHub yet, first push a commit that includes `skills/agent-native-init-zh/` or `skills/agent-native-init/`, then let Codex install it.

### Using the script to adopt a project

This repo also provides a lightweight script that adds the Agent collaboration layer to a target project straight from a local checkout. It does not install the Codex Skill.

To add the Agent collaboration layer to an existing project:

```bash
python3 scripts/agent-init.py adopt /path/to/project
```

`adopt` only adds Agent collaboration files that are missing, by default:

- `AGENTS.md`
- `vault/`
- `vault/tasks/README.md`
- `skills/agent-task/SKILL.md`

If the target project already has an `AGENTS.md`, the script appends a marked Agent Native Init section instead of overwriting the file. Existing `vault/*` and `skills/*` files are skipped by default; pass `--force` explicitly to replace them.

After adoption, have the Agent read the following in the target project:

```text
AGENTS.md
vault/index.md
vault/runtime.md
vault/governance.md
```

### Revising the protocol

To change Agent Native Init itself, modify only:

```text
init/INIT.md
init/protocol/*
```

The `vault/`, `app/`, and test scaffolding in the current repo can be used to validate that the protocol is sound, but they are not the protocol source. The root `skills/` are distributable Skill packages distilled from the protocol source; after modifying the protocol you should check that they still align with `init/`.

After modifying `init/`, regenerate the authoritative protocol snapshot inside both the Chinese and English Skill packages:

```bash
python3 scripts/sync-skills.py
```

Check for drift without writing files:

```bash
python3 scripts/sync-skills.py --check
```

This script is only for this repo's release maintenance; it is not an install-time dependency for Skill users. CI runs the same check. `references/protocol-source/` is maintained entirely by the script; `SKILL.md`, the condensed `references/protocol-model.md`, and `assets/templates/` still require manual review and adjustment when protocol behavior changes. The sync script guarantees the protocol source enters the install package, but it does not pretend to automatically complete Chinese↔English semantic translation or template design.

## Protocol philosophy

### Task contract first

An Agent earns trust not by identity, but by task contract: it is authorized by the contract and closes the task against acceptance criteria.

A task contract includes:

- Goal and scope;
- Explicit non-goals;
- Necessary context;
- Authorization level;
- Allowed and forbidden changes;
- Acceptance criteria;
- Required verification;
- Memory-update and handoff requirements.

### Vault as project memory

The protocol generates a `vault/` in the target project to carry:

- Project positioning;
- Current runtime state;
- Governance rules;
- Long-term decisions;
- Task records;
- Handoff information;
- Collaboration preferences.

This way, when a new Agent, a different model, or a different tool enters the project, it can recover context from files instead of depending on chat history.

### Portable, not copying the sandbox

Do not copy the current repo's generated artifacts wholesale into a new project.

When using the full protocol source, the correct flow is:

1. Migrate or reference `init/`;
2. Have the Agent read `init/INIT.md`;
3. Generate the project's own collaboration layer according to the protocol;
4. Update the `vault/`, `skills/`, and profile artifacts based on the target project's reality.

When using a Skill package, the correct flow is:

1. Install or copy `skills/agent-native-init-zh/` or `skills/agent-native-init/`;
2. Invoke the Skill in the target project;
3. Let the Skill generate the target project's own `AGENTS.md`, `vault/`, and `skills/agent-task/` from its built-in templates.

## Current status

This repository is still in the protocol-design and initialization-scaffolding iteration phase.

The current focus is refining `init/` and `skills/`: the former as the protocol source, the latter as the installable Skill distribution package. Other generated artifacts in the root exist mainly to validate that the protocol is sound.

## Local verification

The current sandbox carries a minimal Python scaffold to validate the initialization flow:

```bash
uv run pytest
```

This does not mean Agent Native Init is tied to Python. The Python and Go profiles are just examples of currently available project types.

## Commit boundary

If the goal is to release or migrate the Agent Native Init protocol, commits should preferably be limited to:

```text
init/
skills/
README.md
scripts/
```

Unless there is an explicit need to update the current sandbox state, do not commit artifacts such as `vault/`, `app/`, `tests/`, or a target project's generated `skills/agent-task/` as protocol source. The root `skills/agent-native-init*` packages are distribution artifacts and may be committed alongside protocol changes.
