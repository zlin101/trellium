# P1 candidate: Adoption completion contract (English skill insert — experiment material, not implementation)

Planned location: `skills/trellium/SKILL.md`, after the "Existing Project Adoption" section.

---

## Adoption Completion Contract

`adopt` performs the mechanical install only; "adoption complete" requires all of the following:

1. Semantic configuration is done: mode and storage chosen from real project facts, existing agent entries merged, nothing user-owned overwritten.
2. The collaboration core is durable: `AGENTS.md`, every required `vault/` file, `skills/agent-task/SKILL.md`, and the version stamp are committed to version-control history (present in Git `HEAD`). Neither adopt nor the agent ever runs `git add`/commit/push automatically — commits stay with the user or require their explicit authorization.
3. After the commit, `trellium.py check <target>` reports 0 errors: missing core paths in `HEAD` raise `CORE_STORAGE_UNCOMMITTED`; core paths captured by ignore rules raise `CORE_STORAGE_IGNORED`. Both are errors.
4. The final acceptance for local/production adoptions is a fresh clone of the repository passing check as well. A fresh clone is a one-time acceptance action, not a recurring cost of daily check.
5. Adoption status and risks are recorded in `vault/runtime.md`.

Generated files do not mean an adopted project. Do not claim adoption is complete while the core is uncommitted.
