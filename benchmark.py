#!/usr/bin/env python3
"""
Benchmark suite for regex2dfa.

Measures the cost of each stage of the pipeline (parse -> NFA -> DFA ->
minimize -> format), the end-to-end conversion, cache behaviour, and how
performance scales with pattern size. Pure standard library, no third-party
dependencies, matching the library itself.

Usage:
    python benchmark.py              # full run, human-readable tables
    python benchmark.py --quick      # fewer iterations, faster
    python benchmark.py --json       # emit machine-readable JSON
    python benchmark.py --stages     # only the per-stage breakdown
"""

import argparse
import gc
import json
import sys
import time
from typing import Callable, Dict, List

from regex2dfa import (
    regex2dfa,
    clear_cache,
    parse_regex,
    build_nfa,
    nfa_to_dfa,
    minimize_dfa,
    format_att,
)


# --------------------------------------------------------------------------- #
# Timing helpers
# --------------------------------------------------------------------------- #

_TARGET_WINDOW = 0.02   # aim for ~20ms per timing window
_BUDGET = 1.0           # hard wall-clock cap per measurement (seconds)


def measure(fn: Callable[[], object], repeats: int = 5) -> float:
    """
    Return the best per-call time in seconds for ``fn``.

    Picks a loop count so one window is ~``_TARGET_WINDOW`` long, then takes the
    minimum across up to ``repeats`` windows (minimum is the most stable
    estimator: it filters out scheduling/GC noise). A per-measurement wall-clock
    budget keeps expensive patterns from making the whole run open-ended.
    """
    # One calibration call to size the loop count.
    start = time.perf_counter()
    fn()
    single = time.perf_counter() - start
    loops = max(1, int(_TARGET_WINDOW / single)) if single > 0 else 1000

    best = float("inf")
    deadline = time.perf_counter() + _BUDGET
    gc_was_enabled = gc.isenabled()
    gc.disable()
    try:
        for _ in range(repeats):
            start = time.perf_counter()
            for _ in range(loops):
                fn()
            elapsed = time.perf_counter() - start
            best = min(best, elapsed / loops)
            if time.perf_counter() > deadline:
                break
    finally:
        if gc_was_enabled:
            gc.enable()
    return best


def fmt_time(seconds: float) -> str:
    """Human-readable time with adaptive units."""
    if seconds < 1e-6:
        return f"{seconds * 1e9:7.1f} ns"
    if seconds < 1e-3:
        return f"{seconds * 1e6:7.2f} us"
    if seconds < 1.0:
        return f"{seconds * 1e3:7.2f} ms"
    return f"{seconds:7.3f} s"


# --------------------------------------------------------------------------- #
# Benchmark patterns
# --------------------------------------------------------------------------- #

# Representative patterns spanning the supported feature set. Each exercises a
# different mix of parser/NFA/DFA/minimizer work.
FEATURE_PATTERNS: Dict[str, str] = {
    "literal_short": "abc",
    "literal_long": "the_quick_brown_fox_jumps",
    "alternation": "(cat|dog|bird|fish|snake)",
    "kleene_star": "a*",
    "kleene_plus": "(ab)+",
    "optional_chain": "colou?r",
    "char_class": "[a-z]+",
    "any_char_star": ".*",
    "negated_class": "[^0-9]+",
    "digits_words": r"\d+\w*",
    "nested_groups": "((a|b)(c|d))+",
    "email_like": r"\w+@\w+",
    "ipv4_octet": r"(\d\d\d|\d\d|\d)",
    "phone_like": r"\d\d\d-\d\d\d-\d\d\d\d",
}


def scaling_patterns() -> Dict[str, Dict[str, str]]:
    """
    Families of patterns that grow in size, for measuring how each algorithm
    scales. Returns {family: {size_label: regex}}.
    """
    families: Dict[str, Dict[str, str]] = {}

    # Long alternation of distinct literals: stresses NFA build + subset states.
    families["alternation_N"] = {
        str(n): "(" + "|".join(f"w{i}" for i in range(n)) + ")"
        for n in (5, 10, 25, 50, 100)
    }

    # Long concatenation: stresses NFA state count (2 states per literal).
    families["concat_N"] = {
        str(n): "a" * n for n in (10, 50, 100, 250, 500)
    }

    # Repeated group with alternation: (a|b|c){...} unrolled via concat of star
    # blocks; stresses subset construction (state explosion pressure).
    families["nested_star_N"] = {
        str(n): "(a|b)*" * n for n in (2, 4, 8, 16, 32)
    }

    # Wide char classes chained: each '.' contributes 256 transitions, so this
    # stresses large-alphabet subset construction hard.
    families["dot_chain_N"] = {
        str(n): "." * n for n in (2, 4, 8, 16, 32)
    }

    return families


# --------------------------------------------------------------------------- #
# Benchmarks
# --------------------------------------------------------------------------- #

def bench_stages(patterns: Dict[str, str], repeats: int) -> List[dict]:
    """Per-stage timing + automaton sizes for each pattern."""
    rows = []
    for name, regex in patterns.items():
        # Pre-build inputs for each stage (all stage fns are pure).
        postfix = parse_regex(regex)
        nfa = build_nfa(postfix)
        dfa = nfa_to_dfa(nfa)
        min_dfa = minimize_dfa(dfa)

        t_parse = measure(lambda r=regex: parse_regex(r), repeats)
        t_nfa = measure(lambda p=postfix: build_nfa(p), repeats)
        t_dfa = measure(lambda n=nfa: nfa_to_dfa(n), repeats)
        t_min = measure(lambda d=dfa: minimize_dfa(d), repeats)
        t_fmt = measure(lambda m=min_dfa: format_att(m), repeats)

        # End-to-end, cache cleared each call to force real work.
        def e2e(r=regex):
            clear_cache()
            return regex2dfa(r)
        t_e2e = measure(e2e, repeats)

        rows.append({
            "name": name,
            "regex": regex,
            "parse": t_parse,
            "build_nfa": t_nfa,
            "nfa_to_dfa": t_dfa,
            "minimize": t_min,
            "format": t_fmt,
            "end_to_end": t_e2e,
            "nfa_states": len(nfa.states),
            "dfa_states": len(dfa.states),
            "min_states": len(min_dfa.states),
        })
    return rows


def bench_cache(repeats: int) -> dict:
    """Compare a cold (uncached) conversion against a warm cache hit."""
    regex = "(a|b|c|d)+[0-9]*xyz"

    def cold():
        clear_cache()
        return regex2dfa(regex)

    clear_cache()
    regex2dfa(regex)  # prime the cache
    warm = measure(lambda: regex2dfa(regex), repeats)
    cold_t = measure(cold, repeats)
    return {"cold": cold_t, "warm": warm,
            "speedup": (cold_t / warm) if warm else float("inf")}


def bench_scaling(repeats: int) -> Dict[str, List[dict]]:
    """End-to-end timing across growing pattern families."""
    results: Dict[str, List[dict]] = {}
    for family, sizes in scaling_patterns().items():
        rows = []
        for label, regex in sizes.items():
            postfix = parse_regex(regex)
            nfa = build_nfa(postfix)
            dfa = nfa_to_dfa(nfa)
            min_dfa = minimize_dfa(dfa)

            def e2e(r=regex):
                clear_cache()
                return regex2dfa(r)

            rows.append({
                "size": label,
                "end_to_end": measure(e2e, repeats),
                "nfa_states": len(nfa.states),
                "dfa_states": len(dfa.states),
                "min_states": len(min_dfa.states),
            })
        results[family] = rows
    return results


# --------------------------------------------------------------------------- #
# Reporting
# --------------------------------------------------------------------------- #

def print_stages(rows: List[dict]) -> None:
    print("\n=== Per-stage breakdown (best per-call time) ===\n")
    header = (f"{'pattern':<18} {'parse':>10} {'nfa':>10} {'subset':>10} "
              f"{'minimize':>10} {'format':>10} {'e2e':>10}  "
              f"{'N/D/M states':>14}")
    print(header)
    print("-" * len(header))
    for r in rows:
        sizes = f"{r['nfa_states']}/{r['dfa_states']}/{r['min_states']}"
        print(f"{r['name']:<18} "
              f"{fmt_time(r['parse']):>10} "
              f"{fmt_time(r['build_nfa']):>10} "
              f"{fmt_time(r['nfa_to_dfa']):>10} "
              f"{fmt_time(r['minimize']):>10} "
              f"{fmt_time(r['format']):>10} "
              f"{fmt_time(r['end_to_end']):>10}  "
              f"{sizes:>14}")

    # Aggregate share of end-to-end time spent per stage.
    stages = ["parse", "build_nfa", "nfa_to_dfa", "minimize", "format"]
    totals = {s: sum(r[s] for r in rows) for s in stages}
    grand = sum(totals.values())
    print("\n--- Aggregate stage share (sum across patterns) ---")
    for s in stages:
        pct = (100.0 * totals[s] / grand) if grand else 0.0
        bar = "#" * int(pct / 2)
        print(f"  {s:<12} {fmt_time(totals[s])}  {pct:5.1f}%  {bar}")


def print_cache(info: dict) -> None:
    print("\n=== Cache ===\n")
    print(f"  cold (compute):  {fmt_time(info['cold'])}")
    print(f"  warm (cache hit):{fmt_time(info['warm'])}")
    print(f"  speedup:         {info['speedup']:.0f}x")


def print_scaling(results: Dict[str, List[dict]]) -> None:
    print("\n=== Scaling (end-to-end) ===")
    for family, rows in results.items():
        print(f"\n  {family}")
        print(f"    {'size':>6} {'e2e':>12} {'nfa':>8} {'dfa':>8} {'min':>8}")
        for r in rows:
            print(f"    {r['size']:>6} {fmt_time(r['end_to_end']):>12} "
                  f"{r['nfa_states']:>8} {r['dfa_states']:>8} "
                  f"{r['min_states']:>8}")


def throughput(rows: List[dict]) -> None:
    print("\n=== Throughput ===\n")
    avg = sum(r["end_to_end"] for r in rows) / len(rows)
    print(f"  mean end-to-end conversion: {fmt_time(avg)}")
    print(f"  ~{1.0 / avg:,.0f} conversions/sec (single core, cache cold)")


# --------------------------------------------------------------------------- #
# Main
# --------------------------------------------------------------------------- #

def main() -> int:
    parser = argparse.ArgumentParser(description="Benchmark regex2dfa")
    parser.add_argument("--quick", action="store_true",
                        help="fewer repeats for a faster run")
    parser.add_argument("--json", action="store_true",
                        help="emit machine-readable JSON")
    parser.add_argument("--stages", action="store_true",
                        help="only run the per-stage breakdown")
    args = parser.parse_args()

    repeats = 3 if args.quick else 7

    stage_rows = bench_stages(FEATURE_PATTERNS, repeats)
    payload: Dict[str, object] = {"stages": stage_rows}

    if not args.stages:
        payload["cache"] = bench_cache(repeats)
        payload["scaling"] = bench_scaling(repeats)

    if args.json:
        print(json.dumps(payload, indent=2))
        return 0

    print("regex2dfa benchmark")
    print(f"Python {sys.version.split()[0]}  |  repeats={repeats}")
    print_stages(stage_rows)
    throughput(stage_rows)
    if not args.stages:
        print_cache(payload["cache"])
        print_scaling(payload["scaling"])
    print()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
