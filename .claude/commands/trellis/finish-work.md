# Finish Work - Android AOSP Pre-Commit Checklist

Before committing Android AOSP changes, use this checklist.

**Timing**: After code is written and device-tested, before commit

---

## Checklist

### 1. Tier 1: Build Verification

```bash
source build/envsetup.sh
lunch ${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}
m SystemUI
```

- [ ] `m SystemUI` exits with code 0?
- [ ] No compilation errors?
- [ ] No `undefined symbol` or `error:` lines?

### 2. Overlay-First Principle

- [ ] Could this change have been done with an RRO? If yes, is it using RRO?
- [ ] If source modification was used, is the reason documented in prd.md?
- [ ] No third-party dependencies introduced?

### 3. Code Standards

- [ ] Indentation: 4 spaces (not tabs) for Java/Kotlin/XML?
- [ ] Line length: ≤ 120 characters?
- [ ] Kotlin preferred over Java for new files?
- [ ] Change scope is minimal (only modified what's necessary)?

### 4. Build System

- [ ] Android.bp updated if new overlay module created?
- [ ] Overlay manifest has correct `android:targetPackage`?
- [ ] Resource names exactly match AOSP source (case-sensitive)?

### 5. Tier 2: Runtime Check (if device connected)

```bash
adb root && adb remount
adb push out/target/product/*/system/priv-app/SystemUI/SystemUI.apk \
  /system/priv-app/SystemUI/
adb shell am force-stop com.android.systemui
sleep 3
adb shell pidof com.android.systemui
adb logcat -d -t 60 | grep -i "fatal\|crash"
adb logcat -d -t 60 | grep "avc: denied"
```

- [ ] SystemUI process alive after restart?
- [ ] No FATAL/crash in first 60s?
- [ ] No `avc: denied` SELinux errors?

### 6. Visual Check (if device connected)

```bash
bash scripts/capture-screenshot.sh after
```

- [ ] Screenshot captured to `baselines/after/`?
- [ ] Visual change matches design tokens in `specs/design/design-tokens.md`?
- [ ] No unintended visual regressions?

### 7. Spec Sync

- [ ] Does `.trellis/spec/implementation/` need updates for new patterns discovered?
- [ ] Does `specs/design/design-tokens.md` have all the tokens used?

---

## Quick Check Flow

```bash
# 1. Build
m SystemUI && echo "BUILD OK"

# 2. View changes
git status
git diff --name-only

# 3. Deploy and check (if device connected)
bash scripts/build-and-deploy.sh
```

---

## Common Oversights

| Oversight | Consequence | Fix |
|-----------|-------------|-----|
| Wrong resource name | Build error or no effect | Cross-check with AOSP source |
| Missing Android.bp | Overlay not included in build | Add to product packages |
| SELinux denial | Feature broken silently | Run `adb logcat \| grep avc` |
| No baselines/after/ screenshot | No visual proof | Run capture-screenshot.sh |
| Overlay targets wrong package | No visual effect | Check `android:targetPackage` in manifest |

---

## Development Flow

```
Implement → Build (m SystemUI) → Deploy (adb) → Verify (logcat + screenshot)
  → /trellis:finish-work → git commit → /trellis:record-session
```
