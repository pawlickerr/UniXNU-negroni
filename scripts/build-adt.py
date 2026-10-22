#!/usr/bin/env python3
"""Build inputs/negroni.adt with the board's mkadt arguments (base ADT: the Apple D22AP one, never in git)."""
from board import BOARD, INPUTS, path, run

adt = BOARD["payload"]["adt"]
INPUTS.mkdir(parents=True, exist_ok=True)
run(["python3", path(adt["tool"]), INPUTS / "negroni.adt", *adt["args"]])
