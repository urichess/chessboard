#!/bin/bash

function activate_zephyr {
  local venv=~/zephyrproject/.venv/bin/activate
  if [ ! -f "$venv" ]; then
    echo "❌ Virtual environment not found at $venv"
    return 1
  fi

  # Activate Zephyr virtual environment
  source "$venv"
  export ZEPHYR_BASE=~/zephyrproject/zephyr

  # Determine BOARD_ROOT
  local target_dir=${1:-$PWD}
  # Convert to absolute path (resolves symlinks and relative paths)
  local abs_path
  abs_path=$(realpath "$target_dir" 2>/dev/null || readlink -f "$target_dir" 2>/dev/null || echo "$target_dir")
  export BOARD_ROOT="$abs_path"

  # Add script directory to PATH
  local script_dir
  script_dir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
  export PATH="$script_dir:$PATH"

  echo "✅ Zephyr environment activated"
  echo "ZEPHYR_BASE=$ZEPHYR_BASE"
  echo "BOARD_ROOT=$BOARD_ROOT"
  echo "PATH updated: $script_dir added"
}

activate_zephyr

