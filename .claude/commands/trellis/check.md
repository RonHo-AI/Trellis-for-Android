Check if the Android AOSP changes you made follow development guidelines and pass 4-tier verification.

Execute these steps:

1. **Identify changed files**:
   ```bash
   git diff --name-only HEAD
   ```

2. **Tier 1: Build verification** (always required):
   ```bash
   source build/envsetup.sh
   lunch ${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}
   m SystemUI 2>&1 | tail -20
   echo "Exit: $?"
   ```

3. **Code review against Android standards**:
   - Overlay-first: did you use RRO where possible?
   - AOSP style: 4-space indent, 120-char lines, Kotlin preferred
   - No third-party dependencies
   - Android.bp updated if new overlay module added

4. **Read the verification spec**:
   ```bash
   cat .trellis/spec/verification/index.md
   ```

5. **Tier 2-4 (if device connected)**:
   ```bash
   adb devices
   # If device connected, run /trellis:deploy then check logcat
   ```

6. **Report any violations** and fix them.
