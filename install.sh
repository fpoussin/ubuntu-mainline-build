#!/bin/sh

set -e

if [ $# -ne 1 ]; then
    echo $0: usage: VERSION
    exit 1
fi

VER=$1;
LONG_VER=${VER}-mainline
MODULES_DIR=/lib/modules/${LONG_VER}
PREFIX=/var/lib/shim-signed/mok

sudo dpkg -i linux-headers-${LONG_VER}_${VER}-1_amd64.deb linux-image-${LONG_VER}_${VER}-1_amd64.deb

sudo sbsign --key ${PREFIX}/MOK.priv --cert ${PREFIX}/MOK.pem /boot/vmlinuz-${LONG_VER} --output /boot/vmlinuz-${LONG_VER}.tmp

sudo mv /boot/vmlinuz-${LONG_VER}.tmp /boot/vmlinuz-${LONG_VER}
