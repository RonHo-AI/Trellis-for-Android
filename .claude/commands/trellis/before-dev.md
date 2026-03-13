Read the relevant Android AOSP development guidelines before starting your task.

Execute these steps:

1. **Get current Android context**:
   ```bash
   python3 ./.trellis/scripts/get_context.py
   ```

2. **Read the Android spec indexes relevant to your task**:
   ```bash
   # For implementation work:
   cat .trellis/spec/implementation/index.md

   # For verification:
   cat .trellis/spec/verification/index.md

   # For design token extraction:
   cat .trellis/spec/design-analysis/index.md

   # For deployment:
   cat .trellis/spec/deployment/index.md
   ```

3. **Always read the shared guides index**:
   ```bash
   cat .trellis/spec/guides/index.md
   ```

4. **Make the overlay-vs-source decision** (mandatory before any code change):
   - Can this be done with a Runtime Resource Overlay (RRO)?
   - YES → overlay path in `vendor/custom/overlay/`
   - NO → source modification in `packages/SystemUI/` or `frameworks/base/`

5. **Check for existing design tokens**:
   ```bash
   cat specs/design/design-tokens.md 2>/dev/null || echo "No design tokens yet"
   ```

6. **Understand the AOSP build target**:
   ```bash
   echo "Build target: ${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}"
   echo "AOSP root: ${AOSP_ROOT:-not set}"
   ```

This step is **mandatory** before writing any AOSP code.
