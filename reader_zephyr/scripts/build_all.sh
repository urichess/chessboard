#!/usr/bin/env bash
# Build script for MCUboot + application
# -------------------------------------
# Usage:
#   ./build.sh [-clean]
#
# Options:
#   -clean       Perform a pristine (clean) build
#   --help, -h   Show this help message and exit
# ==============================================================

set -euo pipefail

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
BOARD="chessboard_l431_v1"
MCUBOOT_DIR="bootloader/mcuboot/boot/zephyr"
APP_DIR="app"
MCUBOOT_BUILD_DIR="build/mcuboot"
APP_BUILD_DIR="build/app"
KEY_FILE="/home/elotro/keys/mykey.pem"

# Default West parameter
PRISTINE="auto"

# ---------------------------------------------------------------------
# Colors for better UX
# ---------------------------------------------------------------------
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No color

# ---------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------
function show_help() {
    echo -e "${CYAN}Usage:${NC} ./build.sh [options]\n"
    echo "Options:"
    echo "  -clean        Perform a pristine (clean) build"
    echo "  --help, -h    Show this help message and exit"
    echo ""
    echo "Examples:"
    echo "  ./build.sh             # Incremental build"
    echo "  ./build.sh -clean      # Force full rebuild of MCUboot + App"
    exit 0
}

# ---------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------
for arg in "$@"; do
    case "$arg" in
        -clean)
            PRISTINE="always"
            ;;
        --help|-h)
            show_help
            ;;
        *)
            echo -e "${YELLOW}Warning:${NC} Unknown argument '$arg' (ignored)"
            ;;
    esac
done

# ---------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------

function build_target() {
    local name=$1
    local dir=$2
    local src=$3
    shift 3
    echo ""
    echo -e "\n${CYAN}🚀 Building ${name}...${NC}"
    west build -p "$PRISTINE" -b "$BOARD" -d "$dir" "$src" "$@"
}

# ---------------------------------------------------------------------
# Builds
# ---------------------------------------------------------------------

# MCUboot
build_target "MCUboot" "$MCUBOOT_BUILD_DIR" "$MCUBOOT_DIR" \
    -DCONFIG_BOOT_SIGNATURE_KEY_FILE="\"$KEY_FILE\"" --extra-conf /home/elotro/work/chessApps/chessboard/reader_zephyr/bootloader/config_overrides.conf

# Application
build_target "Application" "$APP_BUILD_DIR" "$APP_DIR" \
    -DCONFIG_MCUBOOT_SIGNATURE_KEY_FILE="\"$KEY_FILE\""

# ---------------------------------------------------------------------
# Summary
# ---------------------------------------------------------------------
echo ""
echo -e "\n${GREEN}✅ Build complete!${NC}"
echo "MCUboot build: $MCUBOOT_BUILD_DIR"
echo "App build:     $APP_BUILD_DIR"

