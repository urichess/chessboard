#!/bin/bash

BOARD=chessboard_l431_v1

# Default West parameter
PRISTINE="auto"

# Check for -clean flag
for arg in "$@"; do
    if [ "$arg" = "-clean" ]; then
        PRISTINE="always"
    fi
done

#echo "Using West parameter: $PRISTINE"

echo "Building MCUboot..."
west build -p $PRISTINE $WEST_PARAM -b $BOARD -d build/mcuboot bootloader/mcuboot/boot/zephyr

echo "Building App..."
west build -p $PRISTINE -b $BOARD -d build/app app

echo "Done!"

