#!/usr/bin/env bash
# capture-screenshot.sh — Capture screenshot from connected Android device
#
# Usage:
#   bash scripts/capture-screenshot.sh before   # Capture baseline before changes
#   bash scripts/capture-screenshot.sh after    # Capture after changes
#
# Output: baselines/<phase>/<timestamp>.png

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"

PHASE="${1:-after}"
if [[ "$PHASE" != "before" && "$PHASE" != "after" ]]; then
    echo "Usage: $0 [before|after]"
    echo "  before  — Capture baseline before implementing changes"
    echo "  after   — Capture after deploying changes"
    exit 1
fi

# Check device
if ! adb devices | grep -q "device$"; then
    echo "ERROR: No Android device connected"
    exit 1
fi

TIMESTAMP=$(date +%Y%m%d-%H%M%S)
OUTDIR="$REPO_ROOT/baselines/$PHASE"
OUTFILE="$OUTDIR/$TIMESTAMP.png"

mkdir -p "$OUTDIR"

echo "Capturing screenshot ($PHASE)..."
adb shell screencap -p /sdcard/trellis_screen.png
adb pull /sdcard/trellis_screen.png "$OUTFILE"
adb shell rm /sdcard/trellis_screen.png

echo "Saved: $OUTFILE"
echo ""

# Show file size
SIZE=$(du -h "$OUTFILE" | cut -f1)
echo "Size: $SIZE"

# List recent baselines
echo ""
echo "Recent $PHASE baselines:"
ls -lt "$OUTDIR" | head -5
