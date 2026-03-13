# Design Analysis Spec — Index

> **Stage**: Design & Token Extraction
> **Model**: Opus (deepest visual reasoning)
> **Agent**: ui-designer

This stage analyzes reference screenshots and ROM captures to extract Design Tokens and produce structured UI specifications.

---

## Guideline Files

| File | Purpose | Status |
|------|---------|--------|
| `design-token-extraction.md` | Methodology for extracting Design Tokens from screenshots | To fill |
| `ui-spec-format.md` | Standard format for UI specification output | To fill |
| `android-resource-mapping.md` | Token → `@color/`, `@dimen/` Android resource mapping rules | To fill |

---

## Pre-Development Checklist

Before starting design analysis:

- [ ] Reference screenshots / ROM captures have been placed in `baselines/before/`
- [ ] `specs/design/design-tokens.md` template is ready for output
- [ ] Read `design-token-extraction.md` (when available)
- [ ] Read `android-resource-mapping.md` (when available)

---

## Quality Check

After design analysis:

- [ ] Design tokens are fully documented in `specs/design/design-tokens.md`
- [ ] All tokens have Android resource name mappings (`@color/`, `@dimen/`, etc.)
- [ ] Light/dark mode variants are covered if applicable
- [ ] Material You / Dynamic Color tokens are noted where used
- [ ] Output can be handed directly to the implementation stage
