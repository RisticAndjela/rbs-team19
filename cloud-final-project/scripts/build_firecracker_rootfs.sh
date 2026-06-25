#!/usr/bin/env bash
set -euo pipefail

# This helper documents the expected rootfs shape. It assumes you already have a Linux
# rootfs image that includes Python 3 and basic util-linux/busybox commands.
# Usage:
#   sudo scripts/build_firecracker_rootfs.sh ./base-rootfs.ext4 ./firecracker/rootfs.ext4

if [[ $# -ne 2 ]]; then
  echo "Usage: sudo $0 <base-rootfs.ext4> <output-rootfs.ext4>" >&2
  exit 2
fi

BASE_ROOTFS="$1"
OUTPUT_ROOTFS="$2"
MOUNT_DIR="$(mktemp -d)"

cp "$BASE_ROOTFS" "$OUTPUT_ROOTFS"
sudo mount -o loop "$OUTPUT_ROOTFS" "$MOUNT_DIR"
sudo mkdir -p "$MOUNT_DIR/sbin"
sudo cp firecracker/rootfs_overlay/sbin/oblak-init "$MOUNT_DIR/sbin/oblak-init"
sudo chmod +x "$MOUNT_DIR/sbin/oblak-init"
sudo sync
sudo umount "$MOUNT_DIR"
rmdir "$MOUNT_DIR"

echo "Prepared Oblak Firecracker rootfs at $OUTPUT_ROOTFS"
