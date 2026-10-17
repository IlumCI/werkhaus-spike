"""Turn bench records into a markdown summary line set (for $GITHUB_STEP_SUMMARY)."""

from __future__ import annotations

import json
import re
import statistics
import sys
from pathlib import Path


# The Phase 0 heuristic, kept identical so runs compare: words for features the
# staking template does not have, and any stated rate or return.
INVENTED = re.compile(r"\b(vot(e|ing)|governance|exclusive|early access|priority|nft|airdrop|discount|private|members?hip|perks?|additional \w+ tokens|daily|every day|weekly|monthly)\b", re.I)
RATE = re.compile(r"\b(apy|apr|\d+(\.\d+)?\s?%|guarantee\w*|passive income|\d+x)\b", re.I)


def claims(records: list[dict]) -> tuple[int, int]:
    invented = sum(1 for r in records if INVENTED.search(json.dumps(r.get("params", {}))))
    rates = sum(1 for r in records if RATE.search(json.dumps(r.get("params", {}))))
    return invented, rates


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
        "- flagged: {0}/{2} invent a feature, {1}/{2} state a rate".format(*claims(records), len(records)),
    ]
    if errors:
        lines.append("- schema failures: " + "; ".join(f"{n}× {e}" for e, n in sorted(errors.items(), key=lambda x: -x[1])[:5]))
    return "\n".join(line for line in lines if line) + "\n"


if __name__ == "__main__":
    print(summarize(sys.argv[1], json.loads(Path(sys.argv[2]).read_text())))
