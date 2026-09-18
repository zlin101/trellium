## Mode Decision

Choose one mode before editing:

- **New project initialization**: use when the target is empty, disposable, or explicitly asks for a new Agent-ready scaffold.
- **Existing project adoption**: use when the target already has source code, dependencies, tests, build files, deployment files, CI, or project docs.

If uncertain, choose existing project adoption. It is safer because it only adds or merges the Agent collaboration layer by default.

## Install And Upgrade (Bundled Script First)

This package bundles a deterministic installer/upgrader at `assets/trellium.py`; prefer it, and layer Agent-driven semantic migration on top.

- New or existing project adoption: `python3 assets/trellium.py adopt <target>`. It only adds missing files by default; an existing `AGENTS.md` gets a marked section appended, never overwritten. When languages are known, repeat `--profile go-backend=<root>` / `--profile python-backend=<root>`; this generates one project engineering policy with a one-hop AGENTS route and never guesses languages automatically.
- Protocol-content updates do not require reinstalling this Skill: add `--fetch` to any command to fetch the latest tagged release from GitHub and run it with that release's script and templates (cached under `~/.cache/trellium/`; downgrades are refused). Reinstall the Skill only when the SKILL workflow or the script itself changes.
- Upgrading an adopted project:
  1. `python3 assets/trellium.py diff <target>` — read-only report of what would change, what is never touched, and pending migration playbook entries.
  2. `python3 assets/trellium.py upgrade <target> --apply` — executes the safe subset; conflicts produce proposals under the target's `vault/.upgrade/<version>/`.
  3. The agent merges each proposal semantically (preserving every local customization); the user confirms item by item.
  4. `python3 assets/trellium.py upgrade <target> --complete` — finalizes the round.
- Projects without a stamp (missing `vault/.agent-init.json`): run `python3 assets/trellium.py baseline <target>` first.
- Validating a project: `python3 assets/trellium.py check <target>` (add `--format json` for stable JSON) is a fully read-only, deterministic validation of the minimal state layer — `trellium-task-state` blocks in Level B/C task files, the `trellium-policy` block in `vault/index.md`, the runtime projection of task lifecycles, hot-file budget measurements, and TASK storage versus Git. Exit codes: `2` on any error finding, `0` with warnings only (warnings are always shown, never an unconditional PASS), `1` for operational failures. It never auto-fixes or writes anything; legacy task files without a state block are reported as unresolved, never guessed. Create new task files from the bundled template (which carries the state block) and add a block when re-activating an old task; do not batch-migrate history. In `local` projects, a runtime row whose task file is absent (fresh clone or local loss) is reported as a clone-safe warning that grants no authority, and closed local tasks must not keep a runtime row.
- Data protection: project data (runtime, handoff, decisions, tasks, and friends) is read-only to the script and is never replaced by templates; format migrations run semantically per `references/protocol-source/init/MIGRATIONS.md`, carrying content over without dropping facts.
- Version check: propose an upgrade when the target's `vault/.agent-init.json` `protocol_version` is older than `references/protocol-source/init/VERSION`.
- When the script cannot run (no python3, restricted sandbox), fall back to the agent-driven flow of this skill: merge templates and run migrations by hand per `references/protocol-source/`, honoring the same data-protection boundary.

## Task Contract

Before editing, state:

- Objective
- Mode
- In scope and out of scope
- Files expected to change
- Authority level and user confirmations needed
- Acceptance criteria
- Verification commands

If the project already has `vault/tasks/`, create or update a task file. If not, keep the contract in working notes until the vault exists, then write it to `vault/tasks/`.

## New Project Initialization

Create the smallest useful project:

1. Add Agent entry files such as `AGENTS.md`; add tool-specific companions only when useful.
2. Add the required `vault/` files.
3. Add `skills/agent-task/SKILL.md`.
4. Add source, tests, dependencies, and README only if the user requested a concrete project type.
5. Run the smallest meaningful check.
6. Record current state in `vault/runtime.md` and durable choices in `vault/decisions.md`.

Do not add frameworks, services, databases, CI, deployment, LLM SDKs, or credentials until the project genuinely needs them.

## Existing Project Adoption

Preserve the existing project:

1. Read-only scan first: root files, Agent entry files, README/docs, source layout, dependency files, tests, build/deploy/CI files, existing memory or decision records, and dirty worktree state.
2. Present an adoption plan listing only Agent collaboration layer changes.
3. Merge existing Agent entry rules instead of overwriting them.
4. Create or merge `vault/` files and `skills/agent-task/SKILL.md`.
5. Record in `vault/project.md` that this is adoption into an existing project.
6. Record adoption state, risks, and next steps in `vault/runtime.md`.

Without explicit user approval, do not modify business source, tests, dependency files, lock files, build files, deployment files, CI, database migrations, environment files, or large existing docs.