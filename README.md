# boot-assets

Data branch of this fork. It has no kernel source and shares no history with it.

Each `<device>/<rom_stamp>/` holds:

- `ramdisk.img`: the ramdisk of the ROM's stock `boot.img`, byte-for-byte as shipped (gzip).
- `MANIFEST.json`: where it came from (URL, file name, size, sha256 of the source
  `boot.img`), the boot header values (version, `os_version`, `os_patch_level`,
  cmdline, partition size), the ramdisk sha256, the AVB footer props, the pinned
  tool versions, and the extraction time.

`<device>/latest` names the stamp that builds use by default.

Contents are PixelOS / AOSP build output (mostly Apache-2.0), redistributed
only so `boot.img` can be rebuilt without downloading the 192 MiB stock image.
Commits here are made by the `refresh-ramdisk` workflow on the default branch;
the sign-off is only the bot's identity.
