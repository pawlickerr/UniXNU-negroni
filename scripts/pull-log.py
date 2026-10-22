#!/usr/bin/env python3
"""Phone in OrangeFox: read the persistent console log (read only) and decode it to out/logs/NAME.txt.

  pull-log.py NAME [GREP ...]    prints the lines matching any GREP (e.g. "panic" "spawn FAIL")
"""
import re
import subprocess
import sys

from board import BOARD, OUT, REPO, die, run, tool, win

if len(sys.argv) < 2:
    die(__doc__)
name, patterns = sys.argv[1], sys.argv[2:]
A = tool("adb")
logs = OUT / "logs"
logs.mkdir(parents=True, exist_ok=True)
block = BOARD["storage"]["log_lun_block"]
run([A, "shell", f"dd if=/dev/block/sda of=/tmp/nlog.bin bs=4096 skip={block} count=1025 2>/dev/null"])
run([A, "pull", "/tmp/nlog.bin", win(logs / f"{name}.bin")], stdout=subprocess.DEVNULL)
run([A, "shell", "rm -f /tmp/nlog.bin"])
run(["python3", REPO / "negroni-ios/tools/negroni-log.py", logs / f"{name}.bin", logs / f"{name}.txt"])
if patterns:
    rx = re.compile("|".join(re.escape(p) for p in patterns))
    for n, line in enumerate((logs / f"{name}.txt").read_text(errors="replace").splitlines(), 1):
        if rx.search(line):
            print(f"{n}: {line[:220]}")
