"""Shared helpers for the negroni UniXNU device scripts: the board file, paths, tools."""
import os
import subprocess
import sys
import tomllib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]      # unixnu/
REPO = ROOT.parent                              # ios-sweet/
OUT = ROOT / "out"
INPUTS = ROOT / "inputs"
BOARD = tomllib.loads((ROOT / "board.toml").read_text())


def path(value):
    """A board-file path: ~ expanded, relative ones against the ios-sweet repository."""
    p = Path(os.path.expanduser(value))
    return p if p.is_absolute() else REPO / p


def tool(name):
    return str(path(BOARD["tools"][name]))


def win(p):
    """Windows path of a WSL file, for fastboot.exe / adb.exe."""
    return subprocess.check_output(["wslpath", "-w", str(p)], text=True).strip()


def run(cmd, **kw):
    print("+", " ".join(str(c) for c in cmd), flush=True)
    return subprocess.run([str(c) for c in cmd], check=True, **kw)


def die(msg):
    sys.exit(f"{Path(sys.argv[0]).name}: {msg}")
