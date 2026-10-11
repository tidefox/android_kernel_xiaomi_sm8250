# Fork notes: android_kernel_xiaomi_sm8250 (alioth)

> [!IMPORTANT]
> ### Statement from this fork maintainer
>
> **No AI was used to write or modify the kernel source code in this repository on my part.**
> Every kernel source change I have authored was written, reviewed and tested by me, a human.
>
> AI tooling has only been used, if at all, for supporting material outside the kernel source,
> such as CI configuration and documentation text. Those changes are reviewed by me before they land.
>
> AI tooling and agent **are allowed, only under human supervision**.

---

This is a fork of [PixelOS-Devices/android_kernel_xiaomi_sm8250](https://github.com/PixelOS-Devices/android_kernel_xiaomi_sm8250).

| Branch | What it is |
| --- | --- |
| `seventeen` | Clean mirror of upstream. Fetch/merge from upstream here. |
| `fork` | Default branch: `seventeen` plus only the CI workflows, `ci/` scripts and this README, so upstream merges stay trivial. |
| `seventeen-nomount` | `seventeen` + NoMount. More patch branches (SUSFS, KernelSU, ...) follow the same pattern. |
| `boot-assets` | Orphan data branch: the stock ramdisk used to build `boot.img`, with provenance. |

## Building

Actions → **build-alioth** → Run workflow, set `ref` to the kernel branch.
Artifacts: raw `Image`/`Image.gz`/`dtb`, an AnyKernel3 zip, and a `boot.img`.

The `boot.img` is the stock ROM ramdisk plus the freshly built `Image`
(header v3, so no dtb inside; the dtb comes from `vendor_boot`). Its file name
carries the ramdisk's ROM stamp and patch level. Do not flash one older than the
ROM you are running: keystore rollback protection can break the lock screen and
credentials.

## Updating the ramdisk when PixelOS ships a new release

Actions → **refresh-ramdisk** → paste the new
`https://download.pixelos.net/seventeen/alioth/recovery/boot-alioth_<stamp>.img`
URL. It commits `alioth/<stamp>/` to `boot-assets` and moves `alioth/latest`.

## Caveats

- A ramdisk from one ROM build may not match a later ROM's first-stage init.
- The dtb and vendor modules come from PixelOS's kernel tree; a mismatch with
  this tree can fail to boot even though the image is valid.
- Unlocked bootloader assumed: the AVB footer is unsigned (`Algorithm NONE`), as in stock.
