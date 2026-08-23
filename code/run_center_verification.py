#!/usr/bin/env python3
"""One-command wrapper for the checkpointed center verifier."""
from __future__ import annotations
import argparse, json, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
CHECKER = HERE / "verify_center_chunked.py"
STATE = HERE / "iv_state_direct3_45.json"


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--resume", action="store_true", help="keep an existing checkpoint")
    args = ap.parse_args()
    if not args.resume and STATE.exists():
        STATE.unlink()
    while True:
        cp = subprocess.run([sys.executable, str(CHECKER)], cwd=str(HERE))
        if cp.returncode != 0:
            return cp.returncode
        if STATE.exists():
            st = json.loads(STATE.read_text())
            if not st.get("stack"):
                return 0

if __name__ == "__main__":
    raise SystemExit(main())
