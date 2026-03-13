#!/usr/bin/env bash
# build-check.sh — Lightweight build verification for ralph-loop
#
# Usage: bash scripts/build-check.sh
#
# Checks if SystemUI can be built (Tier 1 verification).
# Lighter than full build-and-deploy — used in check loop.

set -e

echo "=== Build Check ==="

# Check environment
if [ -z "$AOSP_ROOT" ]; then
    echo "WARN: AOSP_ROOT not set — attempting in current directory"
fi

# Set up environment if not already done
if ! command -v m &>/dev/null 2>&1; then
    if [ -f "build/envsetup.sh" ]; then
        source build/envsetup.sh
        lunch "${DEVICE_TARGET:-aosp_cf_x86_64_phone-userdebug}" 2>/dev/null || true
    else
        echo "ERROR: AOSP build environment not found"
        echo "Run: source build/envsetup.sh && lunch <target>"
        exit 1
    fi
fi

# Run build
echo "Building SystemUI..."
if m SystemUI 2>&1 | tee /tmp/build-check.log; then
    echo "Build: PASS"
    echo "TIER1_BUILD_FINISH"
    exit 0
else
    echo "Build: FAIL"
    echo ""
    echo "Errors:"
    grep "error:" /tmp/build-check.log | head -10
    exit 1
fi
