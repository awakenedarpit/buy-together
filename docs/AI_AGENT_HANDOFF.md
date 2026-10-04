# AI Agent Continuity & Handoff Protocol

## Project: Buy Together
**Purpose**: Ensure seamless, zero-loss continuity when developer models switch, session tokens expire, or a new agent takes over development.

---

## 1. Golden Rules of Continuity

1. **The Repository is the Single Source of Truth**:
   Never assume chat memory persists across sessions or models. Everything you need to know about the current project state is stored within the repository files.
2. **Never Overwrite Existing Work Blindly**:
   Always inspect existing files using directory listings or file view tools before writing new code.
3. **Never Redo Completed Work**:
   If a task is marked completed in [TASKS.md](file:///Users/user/PYDATA/TASKS.md) and verified in the repository, do not recreate it just because you were not the model that wrote it.
4. **Zero Trust on Model Output**:
   Maintain the architectural boundaries: AI produces extraction JSON; Python validates and enforces all business rules.

---

## 2. Mandatory Step-by-Step Onboarding Protocol for New Agents

When you first enter this repository, execute the following sequence:

### Step 1: Read the Operating Rules
Read [AGENTS.md](file:///Users/user/PYDATA/AGENTS.md). This establishes the coding standards, zero-trust AI rules, and security guidelines.

### Step 2: Read Current Project State
Read [MEMORY.md](file:///Users/user/PYDATA/MEMORY.md). Pay specific attention to:
- **Current Status** (Active Phase, Current Task, Next Task).
- **Known Problems** (Bugs, blockers, missing tools).
- **AI Integration Status** (Model configuration, prompt version).

### Step 3: Read Task Roadmap
Read [TASKS.md](file:///Users/user/PYDATA/TASKS.md). Look for the first unchecked item `[ ]` under the current active phase.

### Step 4: Inspect Git & Disk State
Run:
```bash
git status
git log -n 5 --oneline
```
Verify that the files on disk match what is documented in `MEMORY.md`.

### Step 5: Read Relevant Architecture & Specs
Depending on the task you are undertaking:
- Modifying endpoints? Consult [docs/API.md](file:///Users/user/PYDATA/docs/API.md).
- Modifying models or queries? Consult [docs/DATABASE.md](file:///Users/user/PYDATA/docs/DATABASE.md).
- Modifying AI pipelines? Consult [docs/AI.md](file:///Users/user/PYDATA/docs/AI.md).
- Modifying security or auth? Consult [docs/SECURITY.md](file:///Users/user/PYDATA/docs/SECURITY.md).

### Step 6: Execute the Single Next Coherent Task
Implement the next task cleanly and modularly. Write automated tests to verify your implementation.

---

## 3. Mandatory Session Exit Protocol

Before concluding your session or responding to the user:
1. **Update MEMORY.md**: Record your completed tasks, active work, and precise next steps.
2. **Update TASKS.md**: Mark finished items with `[x]`.
3. **Update CHANGELOG.md**: Document changes under `Added`, `Changed`, `Fixed`, or `Security`.
4. **Update ADRs** if you made any major architectural deviations.
5. Create a clean git commit with conventional commit messages (e.g. `feat(auth): add JWT login endpoint`).
