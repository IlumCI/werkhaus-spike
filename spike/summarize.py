"""Turn bench records into a markdown summary line set (for $GITHUB_STEP_SUMMARY)."""

from __future__ import annotations

import json
import statistics
import sys
from pathlib import Path


def summarize(label: str, records: list[dict]) -> str:
    valid = sum(1 for r in records if r.get("valid"))
    parses = sum(1 for r in records if r.get("parses"))
    tps = [r["output_tok_per_s"] for r in records if r.get("output_tok_per_s")]
    ptps = [r["prompt_tok_per_s"] for r in records if r.get("prompt_tok_per_s")]
    wall = [r["wall_s"] for r in records]
    out_tok = [r["output_tokens"] for r in records]
    errors: dict[str, int] = {}
    for r in records:
        for e in r.get("errors", []):
            key = e[:80]
            errors[key] = errors.get(key, 0) + 1
    lines = [
        f"### {label}",
        f"- runs: {len(records)}, parse as JSON: {parses}, pass full schema: {valid}",
        f"- output tok/s median {statistics.median(tps):.2f} (min {min(tps):.2f}, max {max(tps):.2f})" if tps else "- no timings",
        f"- prompt tok/s median {statistics.median(ptps):.1f}" if ptps else "",
        f"- wall per run median {statistics.median(wall):.1f}s, output tokens median {statistics.median(out_tok):.0f}",
        f"- first run load: {records[0]['load_s']:.1f}s" if records else "",
    ]
    if errors:
        lines.append("- schema failures: " + "; ".join(f"{n}× {e}" for e, n in sorted(errors.items(), key=lambda x: -x[1])[:5]))
    return "\n".join(line for line in lines if line) + "\n"


if __name__ == "__main__":
    print(summarize(sys.argv[1], json.loads(Path(sys.argv[2]).read_text())))
