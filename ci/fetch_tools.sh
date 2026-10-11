#!/usr/bin/env bash
# Fetch the pinned boot-image tools into $1 (default: ./tools).
set -euo pipefail

MAGISK_VERSION=v30.7
MAGISK_APK_SHA256=e0d32d2123532860f97123d927b1bb86c4e08e6fd8a48bfc6b5bee0afae9ebd5
MKBOOTIMG_COMMIT=d2bb0af5ba6d3198a3e99529c97eda1be0b5a093
AVB_COMMIT=761178607206f4cb2af79ed9eec52d8cbd814adb

dir=${1:-tools}
mkdir -p "$dir/mkbootimg" "$dir/avb"
cd "$dir"

case "$(uname -m)" in
  x86_64) abi=x86_64 ;;
  aarch64) abi=arm64-v8a ;;
  *) echo "unsupported arch $(uname -m)" >&2; exit 1 ;;
esac

curl -fsSL --retry 3 -o magisk.apk \
  "https://github.com/topjohnwu/Magisk/releases/download/$MAGISK_VERSION/Magisk-$MAGISK_VERSION.apk"
echo "$MAGISK_APK_SHA256  magisk.apk" | sha256sum -c -
unzip -o -q magisk.apk "lib/$abi/libmagiskboot.so"
install -m755 "lib/$abi/libmagiskboot.so" magiskboot

curl -fsSL --retry 3 \
  "https://android.googlesource.com/platform/system/tools/mkbootimg/+archive/$MKBOOTIMG_COMMIT.tar.gz" \
  | tar -xz -C mkbootimg
curl -fsSL --retry 3 \
  "https://android.googlesource.com/platform/external/avb/+archive/$AVB_COMMIT.tar.gz" \
  | tar -xz -C avb avbtool.py

# recorded in MANIFEST.json by refresh_ramdisk.py
cat > versions.json <<JSON
{"magiskboot": "Magisk $MAGISK_VERSION", "mkbootimg_commit": "$MKBOOTIMG_COMMIT", "avbtool_commit": "$AVB_COMMIT"}
JSON
