# Android Trellis Template — Development Workflow

> Specialized for AOSP SystemUI customization with multi-model routing.

---

## Quick Start

### Step 1: Initialize Developer Identity (First Time Only)

```bash
python3 ./.trellis/scripts/init_developer.py claude-agent
```

### Step 2: Get Session Context

```bash
python3 ./.trellis/scripts/get_context.py
```

Shows: developer identity, git status, Android device info, model routing, current task.

### Step 3: Read AOSP Guidelines [MANDATORY]

```bash
# For implementation work
cat .trellis/spec/implementation/index.md

# Always read shared guides
cat .trellis/spec/guides/index.md
```

Follow the **Pre-Development Checklist** in each index.

---

## Workflow Overview

### Core Principles

1. **Overlay First** — Always evaluate RRO before source modification
2. **Read Before Write** — Read spec/guides before coding
3. **Design Tokens First** — Extract tokens before implementing visual changes
4. **4-Tier Verification** — Every change must pass Build → Runtime → Visual → Regression
5. **Record Promptly** — Update `memory/today.md` and `context/sessions/index.md`

### Multi-Model Routing

| Stage | Model | Rationale |
|-------|-------|-----------|
| Design analysis | opus | Deep visual understanding |
| Planning | opus | Complex architectural decisions |
| Implementation | opus (fallback) | AOSP source navigation |
| Apply diff | sonnet | File editing, no reasoning needed |
| Verification | sonnet | Checklist execution |
| Debugging | opus | AOSP diagnosis + repair |
| Research | sonnet | Source search and retrieval |

Model routing is automatic — configured in `.trellis/config.yaml` and applied by the `inject-subagent-context.py` hook.

---

## Development Process

### For Visual Changes (Color, Dimension, String)

```
1. Analyze design    /trellis:analyze-design
2. Read guidelines   /trellis:before-dev
3. Implement         (RRO overlay)
4. Build             /trellis:build
5. Deploy            /trellis:deploy
6. Verify            /trellis:verify-4tier
7. Finish            /trellis:finish-work
8. Commit            /trellis:commit
9. Record            /trellis:record-session
```

### For Logic Changes (New behavior, Java/Kotlin)

```
1. Research          (find which class controls the UI)
2. Read guidelines   /trellis:before-dev
3. Implement         (source modification)
4. Build             /trellis:build
5. Deploy            /trellis:deploy
6. Verify            /trellis:verify-4tier
7. Finish            /trellis:finish-work
8. Commit            /trellis:commit
9. Record            /trellis:record-session
```

### Using the Multi-Agent Pipeline

For complex tasks, use the dispatch agent:

```bash
# Create task directory
TASK_DIR=$(python3 ./.trellis/scripts/task.py create "Status bar color" --slug statusbar-color)

# Write prd.md, set up context
python3 ./.trellis/scripts/task.py init-context "$TASK_DIR" android
python3 ./.trellis/scripts/task.py start "$TASK_DIR"

# Dispatch runs: design-analysis → implement → check → deploy-verify
Task(subagent_type: "dispatch", prompt: "Execute the pipeline for the current task")
```

---

## File Structure

```
android-trellis-template/
├── .trellis/
│   ├── config.yaml          # Packages, model routing, Android config
│   ├── workflow.md          # This file
│   ├── scripts/             # Python tools (task.py, get_context.py)
│   ├── tasks/               # Task directories
│   └── spec/
│       ├── design-analysis/ # Token extraction stage
│       ├── implementation/  # Overlay + source patterns
│       ├── verification/    # 4-tier verification framework
│       ├── deployment/      # adb deployment procedures
│       └── guides/          # Cross-stage thinking guides
├── .claude/
│   ├── agents/              # 8 specialized agents
│   ├── commands/trellis/    # 14 slash commands
│   ├── hooks/               # 3 hooks (inject context, session start, ralph loop)
│   ├── prompts/codex/       # Codex role prompts (for future use)
│   └── rules/               # AOSP domain rules
├── specs/design/
│   └── design-tokens.md     # Extracted design tokens
├── memory/
│   ├── today.md             # Current session progress
│   ├── patterns.md          # Discovered patterns
│   └── pitfalls.md          # Known pitfalls
├── baselines/
│   ├── before/              # Pre-change screenshots
│   └── after/               # Post-change screenshots
├── scripts/                 # Android bridge scripts
│   ├── build-and-deploy.sh
│   ├── capture-screenshot.sh
│   ├── verify-no-regression.sh
│   ├── build-check.sh
│   └── device-info.sh
└── context/
    ├── sessions/index.md    # Session history
    └── decisions/           # Architecture decision records
```

---

## Commit Convention

```bash
git commit -m "type(scope): description"
```

| Type | When |
|------|------|
| `feat` | New overlay or feature |
| `fix` | Bug fix or crash resolution |
| `refactor` | Restructure without behavior change |
| `docs` | Documentation only |
| `chore` | Build system, config changes |

**Scope examples**: `statusbar`, `qs`, `lockscreen`, `overlay`, `selinux`

---

## Best Practices

### DO

- Always evaluate overlay option first
- Update `memory/today.md` at session start and end
- Capture before-screenshots before implementing changes
- Verify all 4 tiers, not just Tier 1 (build)
- Document new patterns in `memory/patterns.md`

### DON'T

- Don't skip reading spec index files
- Don't commit — let human verify and commit after testing
- Don't modify files outside `packages/SystemUI/`, `frameworks/base/`, `vendor/custom/`
- Don't introduce third-party dependencies
- Don't use hardcoded device paths (use `${DEVICE_TARGET}`)
