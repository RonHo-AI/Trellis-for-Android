#!/usr/bin/env bash
# build-and-deploy.sh — Build SystemUI and deploy to connected Android device
#
# Usage: bash scripts/build-and-deploy.sh [--skip-build]
#
# Prerequisites:
#   - AOSP environment set up (source build/envsetup.sh && lunch)
#   - adb device connected in root/remount state

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
REPO_ROOT="$(dirname "$SCRIPT_DIR")"
SKIP_BUILD=false

# Parse arguments
for arg in "$@"; do
    case $arg in
        --skip-build)
            SKIP_BUILD=true
            shift
            ;;
    esac
done

echo "=== Android Build & Deploy ==="
echo "Repo: $REPO_ROOT"
echo ""

# --- Step 1: Build ---
if [ "$SKIP_BUILD" = false ]; then
    echo "[1/4] Building SystemUI..."
    if ! m SystemUI 2>&1 | tee /tmp/systemui-build.log; then
        echo "ERROR: Build failed. Check /tmp/systemui-build.log"
        grep "error:" /tmp/systemui-build.log | head -10
        exit 1
    fi
    echo "Build: OK"
else
    echo "[1/4] Skipping build (--skip-build)"
fi

# --- Step 2: Find APK ---
echo "[2/4] Finding APK..."
APK_PATH=$(find out/target/product -name "SystemUI.apk" -path "*/priv-app/*" 2>/dev/null | head -1)
if [ -z "$APK_PATH" ]; then
    echo "ERROR: SystemUI.apk not found. Run build first."
    exit 1
fi
echo "APK: $APK_PATH"

# --- Step 3: Deploy ---
echo "[3/4] Deploying to device..."
if ! adb devices | grep -q "device$"; then
    echo "ERROR: No Android device connected (adb devices shows no device)"
    exit 1
fi

adb root
adb remount
adb push "$APK_PATH" /system/priv-app/SystemUI/
adb shell am force-stop com.android.systemui
echo "Waiting for SystemUI restart..."
sleep 3

# Verify process alive
PID=$(adb shell pidof com.android.systemui 2>/dev/null || true)
if [ -z "$PID" ]; then
    echo "WARNING: SystemUI process not found after restart. Checking logcat..."
    adb logcat -d -t 30 | grep -i "fatal\|crash" | grep -i systemui | head -5
    echo "Try: adb logcat | grep SystemUI"
else
    echo "SystemUI PID: $PID — ALIVE"
fi

# --- Step 4: Verify ---
echo "[4/4] Checking for issues..."
echo ""

# Check crashes
CRASHES=$(adb logcat -d -t 60 | grep -i "fatal\|FATAL" | grep -i "systemui" || true)
if [ -n "$CRASHES" ]; then
    echo "WARNING: Crash detected:"
    echo "$CRASHES"
else
    echo "Crashes: NONE"
fi

# Check SELinux
SELINUX=$(adb logcat -d -t 60 | grep "avc: denied" || true)
if [ -n "$SELINUX" ]; then
    echo "WARNING: SELinux denials:"
    echo "$SELINUX" | head -5
else
    echo "SELinux: CLEAN"
fi

echo ""
echo "=== Deploy Complete ==="
echo "Next: bash scripts/capture-screenshot.sh after"
