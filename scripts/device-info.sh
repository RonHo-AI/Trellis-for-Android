#!/usr/bin/env bash
# device-info.sh — Show connected Android device status
#
# Usage: bash scripts/device-info.sh

echo "=== Connected Devices ==="
adb devices 2>/dev/null || echo "(adb not available)"
echo ""

# If device connected, show details
if adb devices 2>/dev/null | grep -q "device$"; then
    echo "=== Device Info ==="
    echo "Model:   $(adb shell getprop ro.product.model 2>/dev/null)"
    echo "Android: $(adb shell getprop ro.build.version.release 2>/dev/null)"
    echo "Build:   $(adb shell getprop ro.build.display.id 2>/dev/null)"
    echo ""

    echo "=== SystemUI Status ==="
    PID=$(adb shell pidof com.android.systemui 2>/dev/null || true)
    if [ -n "$PID" ]; then
        echo "SystemUI: RUNNING (PID=$PID)"
    else
        echo "SystemUI: NOT RUNNING"
    fi

    echo ""
    echo "=== Recent Errors (last 30s) ==="
    adb logcat -d -t 30 2>/dev/null | grep -E "FATAL|avc: denied" | head -10 || echo "(none)"
fi
