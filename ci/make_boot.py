#!/usr/bin/env python3
"""Build a header-v3 boot.img from a raw kernel Image and a boot-assets ramdisk."""
import argparse
import hashlib
import json
import os
import subprocess
import sys


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--assets", required=True, help="boot-assets checkout")
    p.add_argument("--device", default="alioth")
    p.add_argument("--stamp", help="ROM stamp to use (default: <device>/latest)")
    p.add_argument("--kernel", required=True, help="raw arm64 Image")
    p.add_argument("--out", required=True)
    p.add_argument("--tools", default="tools")
    a = p.parse_args()

    base = os.path.join(a.assets, a.device)
    stamp = a.stamp or open(os.path.join(base, "latest")).read().strip()
    d = os.path.join(base, stamp)
    with open(os.path.join(d, "MANIFEST.json")) as f:
        m = json.load(f)
    ramdisk = os.path.join(d, m["ramdisk"]["file"])
    got = hashlib.sha256(open(ramdisk, "rb").read()).hexdigest()
    if got != m["ramdisk"]["sha256"]:
        sys.exit(f"ramdisk sha256 mismatch: {got} != {m['ramdisk']['sha256']}")

    b = m["boot"]
    tools = os.path.abspath(a.tools)
    subprocess.run([
        sys.executable, f"{tools}/mkbootimg/mkbootimg.py",
        "--header_version", str(b["header_version"]),
        "--kernel", a.kernel, "--ramdisk", ramdisk,
        "--os_version", b["os_version"], "--os_patch_level", b["os_patch_level"],
        "--cmdline", b["cmdline"], "-o", a.out,
    ], check=True)

    cmd = [
        sys.executable, f"{tools}/avb/avbtool.py", "add_hash_footer",
        "--image", a.out, "--partition_name", "boot",
        "--partition_size", str(b["partition_size"]), "--algorithm", m["avb"]["algorithm"],
    ]
    for k, v in m["avb"]["props"].items():
        cmd += ["--prop", f"{k}:{v}"]
    subprocess.run(cmd, check=True)
    print(f"boot image: ROM {m['rom']} {stamp}, os_version {b['os_version']}, "
          f"patch level {b['os_patch_level']}")


main()
