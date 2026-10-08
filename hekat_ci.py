#!/usr/bin/env python3
"""CI gate for HEKAT × JEV.

Runs the adversarial suite and exits non-zero if any case fails, so the gate's
behavior is checked on every push/PR. Deterministic and offline — the live
agent probes skip cleanly without an OPENROUTER_API_KEY, so CI needs no secrets.

Usage:  python3 hekat_ci.py
Exit:   0 all passed · 1 a case failed
"""

import sys

from hekat_eval import run_suite


def main() -> int:
    res = run_suite()
    s = res["summary"]
    print("HEKAT × JEV adversarial gate")
    print(f"  openrouter_live = {s['openrouter_live']}")
    for r in res["gate"] + res["probes"]:
        mark = "PASS" if r["passed"] else "FAIL"
        if r["got"] == "SKIPPED":
            mark = "SKIP"
        print(f"  [{mark}] {r['name']:<24} expect={r['expected']:<12} got={r['got']}")
    print(f"  {s['passed']}/{s['total']} passed")
    if not s["all_passed"]:
        print("GATE REGRESSION — a composition the gate must block (or must allow) changed.")
        return 1
    print("OK — gate fails closed on every adversarial case and allows every legitimate one.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
