#!/usr/bin/env python3
"""Download the kernel of a negroni-ios CI run into inputs/<run>/ and link inputs/kernel.macho to it.

  fetch-kernel.py [RUN_ID]      (default: the newest successful run of the workflow)
"""
import json
import subprocess
import sys

from board import BOARD, INPUTS, die, run

k = BOARD["kernel"]
if len(sys.argv) > 1:
    run_id = sys.argv[1]
else:
    runs = json.loads(subprocess.check_output(["gh", "run", "list", "-R", k["repo"], "-w", k["workflow"], "-L", "20",
                                               "--json", "databaseId,conclusion"], text=True))
    ok = [r for r in runs if r["conclusion"] == "success"]
    if not ok:
        die("no successful run")
    run_id = str(ok[0]["databaseId"])
dest = INPUTS / run_id
if not (dest / k["macho"]).exists():
    run(["gh", "run", "download", run_id, "-R", k["repo"], "-n", k["artifact"], "-D", dest])
run(["sha256sum", "-c", "SHA256SUMS"], cwd=dest)
link = INPUTS / "kernel.macho"
link.unlink(missing_ok=True)
link.symlink_to(dest / k["macho"])
print(f"inputs/kernel.macho -> {dest / k['macho']} (run {run_id})")
