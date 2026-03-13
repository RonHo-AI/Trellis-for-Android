# Build — Android SystemUI

Build the Android SystemUI module and check for errors.

Execute these steps:

1. **Verify AOSP environment**:
   ```bash
   echo "AOSP_ROOT: ${AOSP_ROOT:-NOT SET}"
   echo "DEVICE_TARGET: ${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}"
   ```
   If `AOSP_ROOT` is not set, remind the user to run:
   ```bash
   export AOSP_ROOT=/path/to/aosp
   cd $AOSP_ROOT
   ```

2. **Set up build environment**:
   ```bash
   source build/envsetup.sh
   lunch ${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}
   ```

3. **Build SystemUI**:
   ```bash
   m SystemUI 2>&1 | tee /tmp/systemui-build.log
   BUILD_EXIT=$?
   echo "Build exit code: $BUILD_EXIT"
   ```

4. **Check for errors**:
   ```bash
   # Show last 30 lines
   tail -30 /tmp/systemui-build.log

   # Count errors
   grep -c "error:" /tmp/systemui-build.log || echo "0 errors"
   ```

5. **If overlay module was added, also build it**:
   ```bash
   # Build specific overlay (replace OverlaySystemUI with your module name)
   m OverlaySystemUI 2>&1 | tail -10
   ```

6. **Report result**:
   - If exit 0: "Build PASSED ✓"
   - If non-zero: Show error lines and suggest running `/trellis:break-loop`

## Expected Output Path

```
out/target/product/<device>/system/priv-app/SystemUI/SystemUI.apk
```

## Common Build Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `error: cannot find symbol` | Wrong class/method name | Check AOSP source for correct API |
| `undefined symbol` | Missing import | Add import statement |
| `duplicate resource` | Resource name collision | Rename the overlay resource |
| `module not found` | Android.bp missing module | Add to Android.bp |
