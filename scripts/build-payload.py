#!/usr/bin/env python3
"""Build out/esp.img (the NEGRONIESP FAT payload: UniXNU config + DarwinBoot inputs) from board.toml.

  build-payload.py [--arg EXTRA ...] [--drop PREFIX ...]

The kernel is inputs/kernel.macho (fetch-kernel.py), the ADT inputs/negroni.adt (build-adt.py, or
~/ios-work/negroni-ios-out/unixnu/negroni.adt). --arg adds boot args for one build, --drop removes
those starting with PREFIX (e.g. --drop negronifb_clockshift= --arg negronifb_clockshift=80).
"""
import argparse
from pathlib import Path

from board import BOARD, INPUTS, OUT, die, path, run, tool

ap = argparse.ArgumentParser()
ap.add_argument("--arg", action="append", default=[])
ap.add_argument("--drop", action="append", default=[])
a = ap.parse_args()

p = BOARD["payload"]
kernel = INPUTS / "kernel.macho"
adt = INPUTS / "negroni.adt"
if not adt.exists():
    adt = Path("~/ios-work/negroni-ios-out/unixnu/negroni.adt").expanduser()
for f in (kernel, adt):
    if not f.exists():
        die(f"missing {f}")
args = [x for x in p["kernel_args"] if not any(x.startswith(d) for d in a.drop)] + a.arg
OUT.mkdir(parents=True, exist_ok=True)
run([tool("python"), path(p["tool"]), kernel.resolve(), adt, OUT / "esp.img", "--cmdline", " ".join(args),
     "--size-mib", str(p["size_mib"]), "--timeout", str(p["timeout"])])
(OUT / "cmdline.txt").write_text(" ".join(args) + "\n")
print("cmdline:", " ".join(args))
