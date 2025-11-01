#!/usr/bin/env bash
# Build script for MCUboot + application + upgrader
# --------------------------------------------------

set -euo pipefail

# ---------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------
BOARD="chessboard_l431_v1"
MCUBOOT_DIR="bootloader/mcuboot/boot/zephyr"
APP_DIR="app"
UPGRADER_DIR="upgrader"
MCUBOOT_BUILD_DIR="build/mcuboot"
APP_BUILD_DIR="build/app"
UPGRADER_BUILD_DIR="build/upgrader"
KEY_FILE="/home/elotro/keys/mykey.pem"

# Default West parameter
PRISTINE="auto"
TARGET="all"
EXTRA_PARAMS=""   
MENUCONFIG=""

# ---------------------------------------------------------------------
# Colors
# ---------------------------------------------------------------------
GREEN='\033[0;32m'
CYAN='\033[0;36m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m'

# ---------------------------------------------------------------------
# Help
# ---------------------------------------------------------------------
function show_help() {
    echo -e "${CYAN}Usage:${NC} ./build.sh [target] [-clean]\n"
    echo "Targets:"
    echo "  mcuboot       Build MCUboot only"
    echo "  app           Build main application only"
    echo "  upgrader      Build upgrader only"
    echo "  all           Build everything (default)"
    echo ""
    echo "Options:"
    echo "  -clean        Perform pristine clean build"
    echo "  -h, --help    Show this help message"
    exit 0
}

# ---------------------------------------------------------------------
# Parse arguments
# ---------------------------------------------------------------------
while [[ $# -gt 0 ]]; do
    case "$1" in
        mcuboot|app|upgrader|all)
            TARGET="$1"
            shift
            ;;
        -clean)
            PRISTINE="always"
            shift
            ;;
        -params)
            EXTRA_PARAMS="$2"   # Capture quoted string
            shift 2
            ;;
        --menuconfig)
            MENUCONFIG="-t menuconfig"
            shift
            ;;
        -h|--help)
            show_help
            ;;
        *)
            echo -e "${YELLOW}Warning:${NC} Unknown argument '$1' (ignored)"
            shift
            ;;
    esac
done

# ---------------------------------------------------------------------
# Helper
# ---------------------------------------------------------------------

function build_target() {
    local name=$1
    local dir=$2
    local src=$3
    shift 3

    echo -e "\n${CYAN}🚀 Building ${name}...${NC}"

    echo "Running command: west build -p \"$PRISTINE\" -b \"$BOARD\" -d \"$dir\" \"$src\" $MENUCONFIG $EXTRA_PARAMS $*"

    west build -p "$PRISTINE" \
               -b "$BOARD" \
               -d "$dir" \
               "$src" \
               $EXTRA_PARAMS \
               "$@" \
               $MENUCONFIG 
}

# ---------------------------------------------------------------------
# Conditional builds
# ---------------------------------------------------------------------
if [[ "$TARGET" == "mcuboot" || "$TARGET" == "all" ]]; then
    build_target "MCUboot" "$MCUBOOT_BUILD_DIR" "$MCUBOOT_DIR" \
        --extra-conf /home/elotro/work/chessApps/chessboard/reader_zephyr/bootloader/config_overrides.conf \
        --extra-dtc-overlay /home/elotro/work/chessApps/chessboard/reader_zephyr/bootloader/boards/chessboard_l431_v1.overlay
fi

if [[ "$TARGET" == "app" || "$TARGET" == "all" ]]; then
    build_target "Application" "$APP_BUILD_DIR" "$APP_DIR"
fi

if [[ "$TARGET" == "upgrader" || "$TARGET" == "all" ]]; then
    build_target "Upgrader" "$UPGRADER_BUILD_DIR" "$UPGRADER_DIR"
fi

# ---------------------------------------------------------------------
# Done
# ---------------------------------------------------------------------
echo -e "\n${GREEN}✅ Build complete!${NC}"
echo "Built target: $TARGET"

