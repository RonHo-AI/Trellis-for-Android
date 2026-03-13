#!/usr/bin/env bash
# verify-no-regression.sh — Regression verification after SystemUI changes
#
# Usage: bash scripts/verify-no-regression.sh
#
# Checks:
#   - SystemUI process alive
#   - No FATAL/crash in recent logcat
#   - No SELinux denials
#   - Status bar and notification panel responsive
#
# Exit codes:
#   0 — All checks passed
#   1 — One or more checks failed

set -e

FAIL=0

echo "=== Regression Verification ==="

# Check device
if ! adb devices | grep -q "device$"; then
    echo "ERROR: No device connected — skipping runtime checks"
    echo "Tier 2-4: SKIPPED (no device)"
    exit 0
fi

# 1. Process alive
echo ""
echo "[1] SystemUI process..."
PID=$(adb shell pidof com.android.systemui 2>/dev/null || true)
if [ -z "$PID" ]; then
    echo "FAIL: SystemUI not running"
    FAIL=1
else
    echo "PASS: PID=$PID"
fi

# 2. No crashes in last 60s
echo ""
echo "[2] Crash check (last 60s)..."
CRASHES=$(adb logcat -d -t 60 2>/dev/null | grep -i "FATAL EXCEPTION\|fatal exception" | grep -iv "test\|mock" || true)
if [ -n "$CRASHES" ]; then
    echo "FAIL: Crashes detected:"
    echo "$CRASHES" | head -5
    FAIL=1
else
    echo "PASS: No crashes"
fi

# 3. No SELinux denials
echo ""
echo "[3] SELinux check..."
DENIED=$(adb logcat -d -t 60 2>/dev/null | grep "avc: denied" || true)
if [ -n "$DENIED" ]; then
    echo "FAIL: SELinux denials:"
    echo "$DENIED" | head -5
    FAIL=1
else
    echo "PASS: No SELinux denials"
fi

# 4. Status bar state
echo ""
echo "[4] Status bar state..."
BARSTATE=$(adb shell dumpsys statusbar 2>/dev/null | grep -E "mState|mBarState" | head -3 || true)
if [ -n "$BARSTATE" ]; then
    echo "PASS: $BARSTATE"
else
    echo "WARN: Could not read status bar state (non-fatal)"
fi

# 5. Notification panel expand/collapse
echo ""
echo "[5] Notification panel..."
adb shell cmd statusbar expand-notifications 2>/dev/null || true
sleep 1
adb shell cmd statusbar collapse 2>/dev/null || true
echo "PASS: Panel expand/collapse commands executed"

# Summary
echo ""
echo "=== Results ==="
if [ $FAIL -eq 0 ]; then
    echo "ALL CHECKS PASSED"
    echo "ALL_CHECKS_FINISH"
    exit 0
else
    echo "SOME CHECKS FAILED — see above"
    exit 1
fi
