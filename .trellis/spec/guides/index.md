# Thinking Guides — Index

> **Purpose**: Cross-stage guides that expand thinking to catch issues before they occur.

---

## Available Guides

| Guide | Purpose | When to Use |
|-------|---------|-------------|
| `overlay-vs-source-decision.md` | Decision tree: overlay or source modification? | Before every implementation task |
| `systemui-architecture.md` | SystemUI component map and entry points | When unsure which component owns a feature |
| `selinux-troubleshooting.md` | SELinux denial diagnosis and resolution | When `avc: denied` appears in logcat |

---

## Quick Reference: Thinking Triggers

### When to Read overlay-vs-source-decision.md
- [ ] You are about to implement a visual change
- [ ] You are unsure whether to use RRO or modify source
- [ ] The change involves colors, dimensions, strings, or drawables

### When to Read systemui-architecture.md
- [ ] You need to find which Java/Kotlin file controls a UI element
- [ ] You are navigating the AOSP source tree for the first time
- [ ] A feature spans multiple SystemUI components

### When to Read selinux-troubleshooting.md
- [ ] `avc: denied` appears in logcat after deployment
- [ ] A new system service is being added
- [ ] Custom overlay modules have unexpected access restrictions

---

## Core Principle

> **Overlay first, source last.**
>
> Always evaluate whether a Runtime Resource Overlay (RRO) can achieve the goal
> before modifying Java/Kotlin source code. Overlays are:
> - Safer (no AOSP merge conflicts)
> - Easier to update
> - Reversible without recompile
