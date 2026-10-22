#!/usr/bin/env python3
"""Put the negroni boot images on the phone. Userdata is never written here.

  flash.py fastboot [--reboot]   phone in fastboot: flash out/boot_a.img to boot_a only
                                 (vendor_boot/vbmeta/dtbo must already be the iOS ones)
  flash.py recovery              phone in fastboot: stock boot_a/vendor_boot_a/dtbo_a/vbmeta_a from the
                                 backup, slot a, reboot into OrangeFox, wait for adb
  flash.py dd [--reboot]         phone in OrangeFox: dd boot_a (out/boot_a.img), vendor_boot_a,
                                 vbmeta_a (flags 3) and a zeroed dtbo_a, each read back and compared
"""
import argparse
import hashlib
import subprocess
import time

from board import BOARD, OUT, die, path, run, tool, win

ap = argparse.ArgumentParser()
ap.add_argument("mode", choices=["fastboot", "recovery", "dd"])
ap.add_argument("--reboot", action="store_true")
a = ap.parse_args()
F, A = tool("fastboot"), tool("adb")
bi = BOARD["bootimg"]


def devices(cmd):
    return subprocess.run([cmd, "devices"], capture_output=True, text=True).stdout


def vbmeta():
    """The stock vbmeta_a with its flags word (bytes 120..123, big endian) set to disable verity + verification."""
    data = bytearray(path(bi["vbmeta_backup"]).read_bytes())
    data[120:124] = bi["vbmeta_flags"].to_bytes(4, "big")
    out = OUT / "vbmeta.img"
    out.write_bytes(data)
    return out


if a.mode == "fastboot":
    if "fastboot" not in devices(F):
        die("phone is not in fastboot")
    run([F, "flash", "boot_a", win(OUT / "boot_a.img")])
    if a.reboot:
        run([F, "reboot"])
elif a.mode == "recovery":
    if "fastboot" not in devices(F):
        die("phone is not in fastboot")
    backup = path(bi["stock_backup"])
    for p in ("boot_a", "vendor_boot_a", "dtbo_a", "vbmeta_a"):
        run([F, "flash", p, win(backup / f"{p}.img")])
    run([F, "set_active", "a"])
    run([F, "reboot", "recovery"])
    for _ in range(80):
        if "recovery" in devices(A):
            break
        time.sleep(3)
    else:
        die("OrangeFox did not come up")
    print("OrangeFox is up")
else:
    if "recovery" not in devices(A):
        die("phone is not in OrangeFox")
    images = {"vendor_boot": path(bi["vendor_boot"]), "vbmeta": vbmeta(), "boot": OUT / "boot_a.img"}
    for name, src in images.items():
        run([A, "push", win(src), f"/tmp/{name}.img"], stdout=subprocess.DEVNULL)
    script = "cd /tmp\n"
    for name, src in images.items():
        want = hashlib.sha256(src.read_bytes()).hexdigest()[:16]
        script += (f"d=/dev/block/by-name/{name}_a; n=$(stat -c %s {name}.img); "
                   f"dd if={name}.img of=$d bs=1M conv=fsync 2>/dev/null; "
                   f"b=$(head -c $n $d | sha256sum | cut -c1-16); "
                   f"[ \"$b\" = \"{want}\" ] && echo \"{name}_a OK $b\" || echo \"{name}_a MISMATCH\"\n")
    script += ("dd if=/dev/zero of=/dev/block/by-name/dtbo_a bs=1M 2>/dev/null; sync\n"
               "[ -z \"$(tr -d '\\000' < /dev/block/by-name/dtbo_a | head -c1)\" ] && echo 'dtbo_a erased'\n"
               "rm -f /tmp/*.img; echo battery $(cat /sys/class/power_supply/battery/capacity)%\n")
    out = subprocess.run([A, "shell", script], capture_output=True, text=True).stdout
    print(out, end="")
    if "MISMATCH" in out or out.count(" OK ") != 3:
        die("a partition did not read back as written")
    if a.reboot:
        run([A, "reboot"])
