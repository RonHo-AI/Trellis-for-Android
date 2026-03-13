# Deploy — Push SystemUI to Device

Deploy the compiled SystemUI APK to a connected Android device and verify it starts cleanly.

Execute these steps:

1. **Verify device is connected**:
   ```bash
   adb devices
   ```
   If no device shown, remind user to connect device and enable USB debugging.

2. **Gain root and remount**:
   ```bash
   adb root && adb remount
   ```
   If `adb root` fails, the device may not be rooted. Deployment requires root access.

3. **Find the APK**:
   ```bash
   APK_PATH=$(find out/target/product -name "SystemUI.apk" -path "*/priv-app/*" 2>/dev/null | head -1)
   echo "APK: $APK_PATH"
   ```
   If empty, the APK hasn't been built yet. Run `/trellis:build` first.

4. **Push APK to device**:
   ```bash
   adb push "$APK_PATH" /system/priv-app/SystemUI/
   echo "Push exit: $?"
   ```

5. **Restart SystemUI**:
   ```bash
   adb shell am force-stop com.android.systemui
   sleep 3
   ```

6. **Verify process is alive**:
   ```bash
   PID=$(adb shell pidof com.android.systemui)
   echo "SystemUI PID: $PID"
   ```
   If empty, SystemUI failed to restart. Check logcat.

7. **Check for crashes (60s window)**:
   ```bash
   adb logcat -d -t 60 | grep -i "fatal\|crash\|FATAL" | grep -i systemui
   ```

8. **Check for SELinux denials**:
   ```bash
   adb logcat -d -t 60 | grep "avc: denied"
   ```

9. **Capture before/after screenshot**:
   ```bash
   bash scripts/capture-screenshot.sh after
   ```

10. **Report result**:
    - If process alive + no crashes + no SELinux denials: "Deployment PASSED ✓"
    - If issues found: show logcat lines and suggest running `/trellis:break-loop`

## Quick Deploy Script

```bash
bash scripts/build-and-deploy.sh
```

This script automates steps 2-9.
