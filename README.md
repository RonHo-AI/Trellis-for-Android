# Android Trellis Template

AI-assisted AOSP customization workflow built on [Trellis](https://github.com/tinyfish-io/agentwork).

Specialize Claude Code for Android SystemUI customization with multi-model routing, overlay-first implementation, and 4-tier verification.

## Features

- **Multi-model routing** — Opus for design/planning/debug, Sonnet for verification, with Codex integration scaffold
- **Overlay-first principle** — RRO preferred over source modification (safer, reversible)
- **4-tier verification** — Build → Runtime → Visual → Regression
- **Design token pipeline** — Screenshot → tokens → Android resources → overlay XML
- **8 specialized agents** — dispatch, plan, ui-designer, implement, apply-diff, check, debug, research
- **Android context injection** — Device info, build target, model routing in every session
- **Memory system** — Cross-session patterns, pitfalls, and progress tracking

## Prerequisites

| Requirement | Version |
|-------------|---------|
| Claude Code | Latest |
| AOSP source tree | Android 12+ |
| Android SDK platform-tools (`adb`) | Latest |
| Python | 3.9+ |
| bash | For scripts |

## Setup

### 1. Clone this template into your project

```bash
# Use as standalone harness alongside your AOSP tree
git clone <this-repo> /path/to/my-project
```

### 2. Configure `config.yaml`

Edit `.trellis/config.yaml`:

```yaml
packages:
  systemui:
    path: packages/SystemUI       # Path relative to AOSP root
  overlay:
    path: vendor/custom/overlay   # Your overlay directory

android:
  aosp_root: "${AOSP_ROOT}"       # Set via environment variable
  device_target: "${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}"
  build_command: "m SystemUI"
```

### 3. Set environment variables

```bash
export AOSP_ROOT=/path/to/aosp/source
export DEVICE_TARGET=your_device-userdebug
```

### 4. Initialize developer identity

```bash
python3 ./.trellis/scripts/init_developer.py <your-name>
```

### 5. Start Claude Code

```bash
cd /path/to/my-project
claude
```

Then run `/trellis:start` to begin.

---

## Usage

### Typical Workflow

```
1. /trellis:start          — Get context and understand current state
2. /trellis:analyze-design — Extract design tokens from screenshots
3. /trellis:before-dev     — Read Android spec guidelines
4. [implement changes]     — Edit overlay XML or AOSP source
5. /trellis:build          — m SystemUI
6. /trellis:deploy         — Push to device
7. /trellis:verify-4tier   — Run full verification
8. /trellis:finish-work    — Pre-commit checklist
9. /trellis:commit         — Commit changes
10. /trellis:record-session — Record session
```

### Multi-Agent Pipeline (for complex tasks)

Use the dispatch agent for automated multi-step execution:

```
Task(subagent_type: "dispatch", prompt: "Execute the pipeline for current task")
```

Pipeline flow: `design-analysis → implement → check → deploy-verify`

### Model Routing

Edit `.trellis/config.yaml` to change which model handles each stage:

```yaml
model_routing:
  implementation: opus      # Change to "codex" when available
  verification: sonnet
  debugging: opus
```

---

## Codex Integration (Future)

When `codeagent-wrapper` becomes available:

1. Install: `cp codeagent-wrapper ~/.claude/bin/`
2. Edit `config.yaml`: change `implementation: opus` to `implementation: codex`
3. The dispatch agent will automatically use the Codex path

The `apply-diff` agent enforces **Code Sovereignty** — Codex generates diffs, Claude applies them.

---

## Directory Structure

```
android-trellis-template/
├── CLAUDE.md                   # Project instructions for Claude
├── .trellis/
│   ├── config.yaml             # Project configuration
│   ├── workflow.md             # Development workflow
│   └── spec/                   # Android spec layers (index.md files)
├── .claude/
│   ├── agents/                 # 8 specialized agents
│   ├── commands/trellis/       # 14 slash commands
│   ├── hooks/                  # Context injection, session start
│   └── rules/aosp-systemui.md  # AOSP coding rules
├── specs/design/
│   └── design-tokens.md        # Design token values
├── memory/                     # Cross-session memory
├── baselines/                  # Visual regression baselines
├── scripts/                    # Android bridge scripts
└── context/                    # Session history and decisions
```

---

## License

MIT
