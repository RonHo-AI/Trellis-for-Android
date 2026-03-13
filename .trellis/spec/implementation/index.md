# Implementation Spec — Index

> **Stage**: Code Implementation
> **Model**: Opus (or Codex when codeagent-wrapper is available)
> **Agent**: implement (fallback), dispatch → codeagent-wrapper (primary)

This stage implements design tokens as AOSP code changes — primarily via Runtime Resource Overlays (RRO), with direct source modifications where overlays are insufficient.

---

## Guideline Files

| File | Purpose | Status |
|------|---------|--------|
| `overlay-patterns.md` | RRO complete guide + decision tree (overlay vs source) | To fill |
| `source-modification.md` | AOSP source code modification scenarios and methods | To fill |
| `build-system.md` | Android.bp / Soong build rules | To fill |
| `coding-standards.md` | AOSP coding conventions (4-space, 120-char, Kotlin-first) | To fill |

---

## Pre-Development Checklist

Before implementing:

- [ ] Design tokens in `specs/design/design-tokens.md` are complete
- [ ] Overlay-vs-source decision has been evaluated for each change
- [ ] Read `overlay-patterns.md` (when available)
- [ ] Read `coding-standards.md` (when available)
- [ ] Target Android package path is confirmed (from `config.yaml`)

---

## Quality Check

After implementation:

- [ ] All changes follow overlay-first principle
- [ ] Android.bp updated if new overlay module created
- [ ] Code follows AOSP style (4-space indent, 120-char lines, Kotlin preferred)
- [ ] No third-party dependencies introduced
- [ ] Change scope is minimal (only modify what's necessary)
