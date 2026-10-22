# UniXNU-negroni

Bring-up repository for running the `ios-sweet` XNU kernel (xnu-8796, the iOS 16 kernel
of the sweet port, built for negroni) and the iPhone X iOS 16.7.16 userland on a
OnePlus 10 Pro 5G (negroni, SM8450) through Mu-Silicium UEFI and UniXNU/DarwinBoot.

`ios-sweet` remains the kernel/rootfs source. This repository owns the board file, the
`NEGRONIESP` payload and the Android boot image.

## Status

Hardware-verified on an NE2213:

- The ios-sweet shim starts Mu-Silicium (DEBUG); its UniXNU menu lists
  **"iOS 16 (negroni-ios XNU)"**.
- UniXNU mounts the 64 MiB `NEGRONIESP` FAT32 payload, reads
  `\EFI\UniXNU\unixnu.toml` and hands `Payloads\kernel.macho` plus the ADT to DarwinBoot.
- DarwinBoot validates the inputs and enters the iOS 16 XNU kernel in the Mu
  "Kernel RAM" window (ADT DRAM 0x840000000, 3 GiB).
- XNU mounts the iOS 16.7.16 root from userdata (UFS, read-write) and reaches
  SpringBoard on 8 cores, with touch, the hardware keys and a persistent console log.
- Sileo and the Procursus bootstrap are installed in the root.

Wi-Fi (QCA6490 on PCIe0) is not brought up yet.

## Layout

```
board.toml          board file: kernel args, payload, boot image
scripts/
  board.py          shared helpers (board file, paths, fastboot)
  fetch-kernel.py   download an ios-sweet negroni kernel from CI into inputs/
  build-adt.py      inputs/negroni.adt
  build-payload.py  out/esp.img: NEGRONIESP payload (UniXNU config + DarwinBoot inputs)
  build-bootimg.py  out/boot_a.img: Mu-Silicium + ios-sweet shim + payload
  flash.py          flash out/boot_a.img with fastboot
patches/            changes to external trees
inputs/             kernel Mach-O, ADT (ignored)
out/                build products (ignored)
```

## External trees

The build needs these next to this repository (paths in `board.toml`):

- `ios-sweet` (this repository's parent): the kernel is built there by the
  `negroni-ios` workflow from `xnu-8796.141.3` plus `negroni-ios/xnu/patches/`;
  `negroni-ios/tools/` holds `mkadt.py` and `mkdarwinboot.py`.
- `~/ios-work/Mu-Silicium`: Mu-Silicium with the negroni platform
  (`uefi/negroni/negroniPkg` in ios-sweet), built DEBUG by `uefi/negroni/shim-mu.sh`.

## Build

```sh
cd unixnu
scripts/fetch-kernel.py                 # newest green kernel build
scripts/build-payload.py                # boot args from board.toml
scripts/build-bootimg.py
scripts/flash.py --reboot               # phone in fastboot
```

A one-off boot arg without editing the board file:

```sh
scripts/build-payload.py --drop negronifb_clockshift= --arg negronifb_clockshift=80
```

## Build inputs

The kernel and the ADT come from `ios-sweet`:

- the `negroni-ios-kernel` CI artifact (`kernel.development.negroni`) -> `inputs/kernel.macho`
- `negroni-ios/tools/mkadt.py` -> `inputs/negroni.adt`

The iOS root stays on the phone. The Apple D22AP base ADT, vendor firmware, kernels
and images are kept out of git. The platform seed (`UNIQUE_CHIP_ID`) and
`ARTIFACT_KEY` live in CI secrets and `~/ios-work/unixnu-secrets`.
