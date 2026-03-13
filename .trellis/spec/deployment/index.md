# Deployment Spec — Index

> **Stage**: Device Deployment
> **Model**: Sonnet
> **Agent**: check (with [deploy] marker)

This stage handles pushing compiled APKs / overlays to the target device and verifying successful activation.

---

## Guideline Files

| File | Purpose | Status |
|------|---------|--------|
| `device-deployment.md` | adb push / sync / install deployment flows | To fill |
| `ota-packaging.md` | OTA packaging for distribution | To fill |

---

## Quick Reference

```bash
# Push and restart SystemUI
adb root && adb remount
adb push out/target/product/<device>/system/priv-app/SystemUI/SystemUI.apk \
  /system/priv-app/SystemUI/
adb shell am force-stop com.android.systemui
sleep 3

# Verify process alive
adb shell pidof com.android.systemui

# Check for crashes (last 60s)
adb logcat -d -t 60 | grep -i "fatal\|crash"

# Check SELinux
adb logcat -d -t 60 | grep "avc: denied"
```

---

## Pre-Development Checklist

Before deploying:

- [ ] Tier 1 (build) verification passed
- [ ] Device connected and in root/remount state
- [ ] Build output APK exists at expected path

---

## Quality Check

Deployment complete when:

- [ ] APK pushed without errors
- [ ] SystemUI process restarted and alive
- [ ] No crash logs in first 60s post-restart
- [ ] Screenshot captured to `baselines/after/`
