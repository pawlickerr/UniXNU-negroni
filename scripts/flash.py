#!/usr/bin/env python3
"""Flash out/boot_a.img to boot_a with fastboot (phone in fastboot).

  flash.py [--reboot]
"""
import argparse
import subprocess

from board import OUT, die, run, tool, win

ap = argparse.ArgumentParser()
ap.add_argument("--reboot", action="store_true")
a = ap.parse_args()
F = tool("fastboot")
if "fastboot" not in subprocess.run([F, "devices"], capture_output=True, text=True).stdout:
    die("phone is not in fastboot")
run([F, "flash", "boot_a", win(OUT / "boot_a.img")])
if a.reboot:
    run([F, "reboot"])
