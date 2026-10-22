#!/usr/bin/env python3
"""Build out/boot_a.img: Mu-Silicium (DEBUG, negroniPkg) wrapped by the ios-sweet shim, with out/esp.img appended
as the UniXNU payload (uefi/negroni/shim-mu.sh noflash). Prints the SHA-256."""
import os
import shutil

from board import BOARD, OUT, REPO, die, path, run

esp = OUT / "esp.img"
if not esp.exists():
    die("missing out/esp.img (build-payload.py)")
env = dict(os.environ, ESP=str(esp), MU=str(path(BOARD["firmware"]["tree"])))
run(["bash", path(BOARD["firmware"]["shim"]), "noflash"], env=env)
shutil.copy(REPO / "shim/out/negroni-uefi/shim-mu-debug-v4.img", OUT / "boot_a.img")
run(["sha256sum", OUT / "boot_a.img"])
