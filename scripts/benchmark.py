"""Reproducible synthetic benchmark; report observations, never assert timing thresholds."""

import argparse
import json
import platform
import tempfile
import time

from opentruth import OpenTruth

parser = argparse.ArgumentParser()
parser.add_argument("--claims", type=int, default=5000)
args = parser.parse_args()
if args.claims < 100:
    parser.error("Use at least 100 claims")
with tempfile.TemporaryDirectory() as workspace:
    app = OpenTruth(workspace)
    started = time.perf_counter()
    for n in range(args.claims):
        app.add_claim(
            f"SYNTHETIC measurement {n}",
            subject=f"beam-{n % 100}",
            predicate="length",
            value=n,
            unit="m",
            context={"method": "synthetic"},
        )
    insert_seconds = time.perf_counter() - started
    app.close()
    started = time.perf_counter()
    app = OpenTruth(workspace)
    reopen_seconds = time.perf_counter() - started
    started = time.perf_counter()
    page = app.search_claims(subject="beam-0", limit=25, offset=0)
    search_seconds = time.perf_counter() - started
    assert len(page) == 25
    assert all("history" not in claim for claim in page)
    started = time.perf_counter()
    comparisons = app.check_conflicts(page[0]["id"], limit=100)
    comparison_seconds = time.perf_counter() - started
    print(
        json.dumps(
            {
                "synthetic": True,
                "python": platform.python_version(),
                "claims": args.claims,
                "insert_seconds": insert_seconds,
                "reopen_seconds": reopen_seconds,
                "search_page_seconds": search_seconds,
                "page_size": len(page),
                "comparison_seconds": comparison_seconds,
                "comparison_count": len(comparisons),
            },
            indent=2,
        )
    )
    app.close()
