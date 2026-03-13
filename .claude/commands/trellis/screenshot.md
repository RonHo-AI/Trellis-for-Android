# Screenshot — Capture and Compare Visual Baselines

Capture a screenshot from the connected Android device and save it to the baselines directory.

Execute these steps:

1. **Check device connection**:
   ```bash
   adb devices
   ```

2. **Determine capture phase** (before or after your changes):
   - Use `before` if you haven't implemented changes yet
   - Use `after` if you've deployed changes to the device

3. **Capture screenshot**:
   ```bash
   PHASE="after"  # or "before"
   TIMESTAMP=$(date +%Y%m%d-%H%M%S)
   FILENAME="baselines/${PHASE}/${TIMESTAMP}.png"

   mkdir -p "baselines/${PHASE}"
   adb shell screencap -p /sdcard/screen.png
   adb pull /sdcard/screen.png "$FILENAME"
   echo "Saved: $FILENAME"
   ```

4. **Or use the script**:
   ```bash
   bash scripts/capture-screenshot.sh [before|after]
   ```

5. **Compare with design tokens** (after phase):
   - Read `specs/design/design-tokens.md` for expected values
   - Visually verify the screenshot matches color and layout specs
   - Note any discrepancies

6. **Compare before vs after** (if both exist):
   ```bash
   ls -la baselines/before/ baselines/after/
   # View latest screenshots side by side in your image viewer
   ```

7. **Report**:
   - Screenshot path saved to
   - Visual match with design tokens: [yes / partially / no]
   - Any discrepancies noted

## Screenshot Directory Structure

```
baselines/
├── before/          # Screenshots before implementation
│   └── 20240313-143022.png
└── after/           # Screenshots after implementation
    └── 20240313-151045.png
```
