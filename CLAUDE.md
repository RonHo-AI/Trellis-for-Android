# Android Trellis Template — Project Instructions

This is an Android AOSP customization template built on the Trellis AI development framework.

## Project Purpose

Customize Android SystemUI and related AOSP components using:
- Runtime Resource Overlays (RRO) for visual changes
- Direct source modifications for logic changes
- Multi-model AI pipeline (Opus → Sonnet → adb verification)

## Setup

### Prerequisites

1. AOSP source tree checked out at `$AOSP_ROOT`
2. Android SDK platform-tools (`adb`) in PATH
3. Target device connected and in root/remount state (for deployment)

### Environment Variables

```bash
export AOSP_ROOT=/path/to/aosp
export DEVICE_TARGET=aosp_cf_x86_64_phone-userdebug  # or your device target
```

### Initialize Developer Identity

```bash
python3 ./.trellis/scripts/init_developer.py <your-name>
```

---

## Core Principle: Overlay First

**ALWAYS prefer Runtime Resource Overlay (RRO) over source modification.**

| What to change | Approach |
|---------------|----------|
| Color, background | RRO → `res/values/colors.xml` |
| Dimensions, sizes | RRO → `res/values/dimens.xml` |
| Strings, labels | RRO → `res/values/strings.xml` |
| Logic, behavior | Source → `packages/SystemUI/src/` |

---

## Available Commands

| Command | Purpose |
|---------|---------|
| `/trellis:start` | Begin a session, get context |
| `/trellis:before-dev` | Read guidelines before coding |
| `/trellis:analyze-design` | Extract design tokens from screenshots |
| `/trellis:build` | Build SystemUI (`m SystemUI`) |
| `/trellis:deploy` | Push APK to device via adb |
| `/trellis:screenshot` | Capture device screenshot to baselines/ |
| `/trellis:verify-4tier` | Run full 4-tier verification |
| `/trellis:check` | Code review against Android standards |
| `/trellis:finish-work` | Pre-commit checklist |
| `/trellis:commit` | Commit changes |
| `/trellis:record-session` | Record session progress |
| `/trellis:break-loop` | Deep analysis when stuck |
| `/trellis:brainstorm` | Clarify requirements |
| `/trellis:parallel` | Run multi-agent pipeline |

---

## 4-Tier Verification (Required for All Changes)

| Tier | Check | Tool |
|------|-------|------|
| 1 Build | `m SystemUI` exits 0 | Soong |
| 2 Runtime | No crash/FATAL/SELinux denial | adb logcat |
| 3 Visual | Screenshot matches design tokens | adb screencap |
| 4 Regression | Status bar + notification panel work | adb dumpsys |

---

## Domain Rules

Read `.claude/rules/aosp-systemui.md` for complete AOSP coding standards.

Key rules:
- 4-space indent, 120-char max line length
- Kotlin preferred over Java for new files
- No third-party dependencies (AOSP APIs only)
- No `git commit` by agents — human commits after device testing

---

## Model Routing

Configured in `.trellis/config.yaml`. Automatically applied by hooks:

| Stage | Model |
|-------|-------|
| design_analysis | opus |
| planning | opus |
| implementation | opus |
| apply_diff | sonnet |
| verification | sonnet |
| debugging | opus |
| research | sonnet |

---

## Key File Locations

| File | Purpose |
|------|---------|
| `.trellis/config.yaml` | Project config, model routing, Android config |
| `specs/design/design-tokens.md` | Design token values for current task |
| `memory/today.md` | Current session progress |
| `memory/patterns.md` | Discovered overlay patterns |
| `memory/pitfalls.md` | Known pitfalls to avoid |
| `baselines/before/` | Pre-change device screenshots |
| `baselines/after/` | Post-change device screenshots |
