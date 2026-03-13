# Design Tokens — Android Resources

> **Status**: Template — populate via `/trellis:analyze-design` or manually
> **Last updated**: —
> **Source**: —

## How to Use

1. Run `/trellis:analyze-design` to extract tokens from screenshots or design specs
2. Reference these tokens in `prd.md` when describing implementation requirements
3. The implement agent uses these values to populate overlay XML files

---

## Colors

| Token Name | Hex Value | ARGB | Android Resource | AOSP Override Target |
|------------|-----------|------|-----------------|---------------------|
| _(add tokens here)_ | | | | |

## Dimensions

| Token Name | Value | Android Resource | AOSP Override Target |
|------------|-------|-----------------|---------------------|
| _(add tokens here)_ | | | |

## Typography

| Token Name | Value | Android Resource | Usage |
|------------|-------|-----------------|-------|
| _(add tokens here)_ | | | |

## Booleans

| Token Name | Value | Android Resource | Effect |
|------------|-------|-----------------|--------|
| _(add tokens here)_ | | | |

---

## Token Naming Convention

| Component | Prefix Pattern | Example |
|-----------|---------------|---------|
| Status bar | `status_bar_*` | `status_bar_background` |
| Quick Settings | `qs_*` | `qs_tile_background_active` |
| Notification | `notification_*` | `notification_bg_color` |
| Lock screen | `lockscreen_*` | `lockscreen_clock_color` |
| Navigation bar | `navigation_bar_*` | `navigation_bar_color` |
