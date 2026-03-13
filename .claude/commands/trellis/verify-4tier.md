# Verify 4-Tier — Sequential Android Verification

Run the full 4-tier Android verification sequence: Build → Runtime → Visual → Regression.

Execute these steps:

## Tier 1: Build Verification

```bash
source build/envsetup.sh
lunch ${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}
m SystemUI 2>&1 | tail -20
BUILD_EXIT=$?
echo "Tier 1 exit: $BUILD_EXIT"
```

- [ ] Exit code 0?
- [ ] No `error:` lines?

**If Tier 1 fails**: Stop. Fix build errors before continuing. Run `/trellis:break-loop` if needed.

---

## Tier 2: Runtime Verification

**Prerequisites**: Tier 1 passed, device connected.

```bash
# Deploy
adb root && adb remount
APK=$(find out/target/product -name "SystemUI.apk" -path "*/priv-app/*" | head -1)
adb push "$APK" /system/priv-app/SystemUI/
adb shell am force-stop com.android.systemui
sleep 3

# Check alive
adb shell pidof com.android.systemui && echo "ALIVE" || echo "DEAD"

# Check crashes
adb logcat -d -t 60 | grep -i "fatal\|crash" | grep -i systemui

# Check SELinux
adb logcat -d -t 60 | grep "avc: denied"
```

- [ ] SystemUI process alive?
- [ ] No crash logs?
- [ ] No SELinux denials?

---

## Tier 3: Visual Verification

```bash
# Capture after-screenshot
bash scripts/capture-screenshot.sh after

# Show token expectations
cat specs/design/design-tokens.md
```

- [ ] Screenshot saved to `baselines/after/`?
- [ ] Colors match design tokens?
- [ ] Dimensions match design tokens?

---

## Tier 4: Regression Verification

```bash
# Status bar functional
adb shell dumpsys statusbar | grep -E "mState|mBarState" | head -5

# Notification panel
adb shell cmd statusbar expand-notifications
sleep 1
adb shell cmd statusbar collapse
echo "Panel expand/collapse: OK"

# No ANR
adb logcat -d | grep "ANR in" | grep -i systemui
```

- [ ] Status bar state is normal?
- [ ] Notification panel expands and collapses?
- [ ] No ANR detected?

---

## Summary

Report the result of each tier:

```
Tier 1 (Build):    PASS / FAIL
Tier 2 (Runtime):  PASS / FAIL / SKIPPED (no device)
Tier 3 (Visual):   PASS / FAIL / SKIPPED (no device)
Tier 4 (Regression): PASS / FAIL / SKIPPED (no device)
```

If all tiers pass: proceed to `/trellis:finish-work`.
If any tier fails: run `/trellis:break-loop` for deep analysis.
