# AOSP SystemUI Customization Rules

## Core Principle: Overlay First

**ALWAYS evaluate RRO before source modification.**

Runtime Resource Overlays are:
- Safer — no AOSP merge conflicts
- Reversible — remove overlay to revert
- Easier to maintain across Android versions

Direct source modification is only justified when:
- Logic changes are required (not just visual values)
- New UI components need to be added
- AOSP APIs must be called in custom ways
- The resource genuinely doesn't exist in AOSP

## Overlay Structure Rules

```
vendor/custom/overlay/
└── OverlaySystemUI/
    ├── Android.bp                # Soong build rule
    ├── AndroidManifest.xml       # Overlay manifest with targetPackage
    └── res/
        ├── values/
        │   ├── colors.xml        # Color overrides
        │   └── dimens.xml        # Dimension overrides
        └── drawable/             # Drawable overrides
```

### AndroidManifest.xml Requirements
- `android:targetPackage` MUST exactly match the target app's package
- SystemUI: `com.android.systemui`
- Framework: `android`
- Use `android:isStatic="true"` for compile-time overlays

### Android.bp Requirements
- Module type: `runtime_resource_overlay`
- `sdk_version: "current"`
- Module registered in product packages

## Coding Standards

| Rule | Value |
|------|-------|
| Indentation | 4 spaces |
| Line length | ≤ 120 characters |
| Language | Kotlin preferred, Java acceptable |
| Dependencies | AOSP only, no third-party |
| Scope | Minimal — only change what's necessary |

## Build Commands

```bash
# Full SystemUI build
m SystemUI

# Overlay only
m OverlaySystemUI

# Quick syntax check
m -j1 SystemUI 2>&1 | grep "error:" | head -10
```

## Verification Requirements

All changes must pass the 4-tier verification:

1. **Build** (`m SystemUI` exits 0)
2. **Runtime** (no crash/FATAL/SELinux denial in 60s)
3. **Visual** (screenshot matches design tokens)
4. **Regression** (status bar + notification panel functional)

## SELinux Policy

Any new file access, IPC, or service interaction requires SELinux policy updates.

Signs you need a policy update:
- `avc: denied` in logcat after deployment
- Feature works in permissive mode (`adb shell setenforce 0`) but not enforcing

Read `.trellis/spec/guides/selinux-troubleshooting.md` for the fix process.

## Forbidden Operations

- No `git commit` by agents (human commits after testing)
- No third-party libraries (use AOSP APIs only)
- No changes to `.gitignore` or CI configuration
- No hardcoded device paths (use `${DEVICE_TARGET}` variable)
