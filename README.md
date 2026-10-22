# unixnu — negroni device repository

Bring-up of the `ios-sweet` XNU (xnu-8796 with the negroni patches) and the iPhone X iOS 16.7
userland on a **OnePlus 10 Pro 5G (negroni, SM8450)** through Mu-Silicium UEFI and
UniXNU/DarwinBoot: one board file, small scripts, nothing large in git.

`ios-sweet` stays the kernel/rootfs source (`negroni-ios/`), this directory owns the boot payload,
the boot image and the way they get onto the phone.

## Status (2026-10-22)

- Boots to SpringBoard on 8 cores with touch, keys, UFS root (read-write), persistent log.
- Wi-Fi (QCA6490 on PCIe0): read-only survey only.
- Sileo + Procursus installed in the root.

Details and history: `../NOTES.md`.

## Layout

```
board.toml          the board: kernel args, payload, boot image, storage layout
scripts/
  board.py          shared helpers (board file, paths, fastboot/adb)
  fetch-kernel.py   download a negroni-ios CI kernel into inputs/
  build-adt.py      inputs/negroni.adt with mkadt
  build-payload.py  out/esp.img (UniXNU config + DarwinBoot inputs) from board.toml
  build-bootimg.py  out/boot_a.img (Mu-Silicium + shim + payload)
  flash.py          fastboot boot_a / switch to OrangeFox / dd all iOS boot images
  pull-log.py       read and decode the persistent console log from OrangeFox
patches/            where changes to external trees live
inputs/  out/       kernels, ADT, images, logs (ignored)
```

## Usual cycle

```sh
cd unixnu
scripts/fetch-kernel.py                 # newest green kernel build
scripts/build-payload.py                # boot args from board.toml
scripts/build-bootimg.py
scripts/flash.py fastboot --reboot      # phone in fastboot, other partitions already iOS
```

From stock/OrangeFox, or to read the log:

```sh
scripts/flash.py recovery               # fastboot -> stock boot images -> OrangeFox
scripts/pull-log.py boot-NNNN "panic" "spawn FAIL"
scripts/flash.py dd --reboot            # write the iOS boot images back, reboot into iOS
```

A one-off boot arg without editing the board file:

```sh
scripts/build-payload.py --drop negronifb_clockshift= --arg negronifb_clockshift=80
```

Userdata (the iOS root) is never written by these scripts.

## Inputs that stay out of git

Vendor firmware, the Apple D22AP base ADT, kernels, images, logs. The platform seed (`UNIQUE_CHIP_ID`) and `ARTIFACT_KEY` live in CI secrets and
`~/ios-work/unixnu-secrets`.
