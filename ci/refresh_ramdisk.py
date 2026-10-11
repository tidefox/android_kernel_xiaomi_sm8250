#!/usr/bin/env python3
"""Extract the ramdisk from a stock boot.img into a boot-assets checkout.

Writes <assets>/<device>/<rom_stamp>/{ramdisk.img,MANIFEST.json} and points
<assets>/<device>/latest at it.
"""
import argparse
import datetime
import hashlib
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile


def sha256(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def run(*cmd, cwd=None):
    return subprocess.run(cmd, cwd=cwd, check=True, capture_output=True, text=True).stdout


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--img", required=True, help="stock boot.img")
    p.add_argument("--url", required=True, help="where it was downloaded from")
    p.add_argument("--assets", required=True, help="boot-assets checkout")
    p.add_argument("--tools", default="tools")
    p.add_argument("--device", default="alioth")
    p.add_argument("--rom", default="PixelOS")
    a = p.parse_args()

    tools = os.path.abspath(a.tools)
    img = os.path.abspath(a.img)
    name = os.path.basename(a.url.split("?")[0])
    m = re.search(r"_(\d{8}_\d{4})\.img$", name)
    if not m:
        sys.exit(f"cannot find a YYYYMMDD_HHMM stamp in {name!r}")
    stamp = m.group(1)

    hdr = run(sys.executable, f"{tools}/mkbootimg/unpack_bootimg.py", "--boot_img", img,
              "--out", tempfile.mkdtemp())
    field = lambda k: re.search(rf"^{k}: *(.*)$", hdr, re.M).group(1).strip()
    header_version = int(field("boot image header version"))
    if header_version != 3:
        sys.exit(f"expected header v3, got v{header_version}; make_boot.py needs updating")

    avb = run(sys.executable, f"{tools}/avb/avbtool.py", "info_image", "--image", img)
    props = dict(re.findall(r"Prop: (\S+) -> '(.*)'", avb))
    algorithm = re.search(r"^Algorithm: *(\S+)", avb, re.M).group(1)

    with tempfile.TemporaryDirectory() as tmp:
        run(f"{tools}/magiskboot", "unpack", "-n", img, cwd=tmp)
        ramdisk = os.path.join(tmp, "ramdisk.cpio")
        with open(ramdisk, "rb") as f:
            magic = f.read(4)
        fmt = "gzip" if magic[:2] == b"\x1f\x8b" else "lz4" if magic == b"\x02\x21\x4c\x18" else "unknown"

        out = os.path.join(a.assets, a.device, stamp)
        os.makedirs(out, exist_ok=True)
        shutil.copyfile(ramdisk, os.path.join(out, "ramdisk.img"))
        rd_sha = sha256(ramdisk)
        rd_size = os.path.getsize(ramdisk)

    with open(f"{tools}/versions.json") as f:
        versions = json.load(f)

    manifest = {
        "device": a.device,
        "rom": a.rom,
        "rom_stamp": stamp,
        "source": {"url": a.url, "filename": name, "size": os.path.getsize(img), "sha256": sha256(img)},
        "boot": {
            "header_version": header_version,
            "os_version": field("os version"),
            "os_patch_level": field("os patch level"),
            "cmdline": field("command line args"),
            "partition_size": os.path.getsize(img),
        },
        "ramdisk": {"file": "ramdisk.img", "format": fmt, "size": rd_size, "sha256": rd_sha},
        "avb": {"algorithm": algorithm, "props": props},
        "tools": versions,
        "extracted_at": datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
    }
    with open(os.path.join(out, "MANIFEST.json"), "w") as f:
        json.dump(manifest, f, indent=2)
        f.write("\n")
    with open(os.path.join(a.assets, a.device, "latest"), "w") as f:
        f.write(stamp + "\n")
    print(f"{a.device}/{stamp}: ramdisk {fmt} {rd_size} bytes sha256 {rd_sha}")


main()
