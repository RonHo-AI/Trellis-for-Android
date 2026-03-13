# Verification Spec — Index

> **Stage**: 4-Tier Verification
> **Model**: Sonnet (code review + checklist execution)
> **Agent**: check

This stage verifies code changes through four tiers: build, runtime, visual, and regression.

---

## Guideline Files

| File | Purpose | Status |
|------|---------|--------|
| `4-tier-verification.md` | Complete 4-tier verification methodology | To fill |
| `visual-regression.md` | Screenshot baseline comparison approach | To fill |
| `logcat-analysis.md` | Logcat pattern matching (crash / SELinux / ANR) | To fill |

---

## The 4-Tier Verification Framework

| Tier | Check | Tools |
|------|-------|-------|
| **Tier 1** Build | `m SystemUI` compiles without errors | Soong/Make |
| **Tier 2** Runtime | adb deploy succeeds, logcat clean (no FATAL/crash/SELinux denied) | adb, logcat |
| **Tier 3** Visual | Screenshot matches design spec (color, size, layout) | adb screencap |
| **Tier 4** Regression | Status bar + notification panel basic functionality intact | adb dumpsys |

---

## Pre-Development Checklist

Before running verification:

- [ ] Implementation changes are staged
- [ ] Device is connected (`adb devices`)
- [ ] Baseline screenshots in `baselines/before/` are available
- [ ] Read `4-tier-verification.md` (when available)

---

## Quality Check

Verification is complete when:

- [ ] Tier 1: `m SystemUI` exits 0
- [ ] Tier 2: SystemUI process alive, logcat shows no FATAL, no `avc: denied`
- [ ] Tier 3: After-screenshots captured in `baselines/after/`, match design tokens
- [ ] Tier 4: Status bar and notification panel remain functional
