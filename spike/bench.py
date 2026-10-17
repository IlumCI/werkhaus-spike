"""Fill a staking template's parameters with a local model, and measure it.

Usage: python spike/bench.py MODEL RUNS OUT.json [--seed N]

Talks to the Ollama on localhost, asks for output in the template's JSON
schema, and records for every run: tokens in and out, the server's own
timings, and whether the result passes the *full* schema (Ollama's grammar
enforces structure; whether it also enforces lengths and patterns is part of
what this measures).
"""

from __future__ import annotations

import json
import sys
import time
import urllib.request
from pathlib import Path

import jsonschema

IDEAS = [
    "A token for a community of amateur astronomers who share telescope time.",
    "A token for a Berlin cooperative bakery's regulars.",
    "A token for an open-source chess engine and the people who test it.",
    "A token for a podcast about East German industrial design.",
    "A token for a group of hikers mapping abandoned railway lines.",
    "A token for a mod community of an old racing game.",
    "A token for a neighbourhood tool library.",
    "A token for a collective of indie synth builders.",
    "A token for a weekly trivia night at a pub.",
    "A token for a dataset of public-domain botanical drawings.",
]

PROMPT = """You configure a staking-rewards template for a token launch.
Holders stake the token and share the ETH that the creator's fee share pays in.
Choose the parameters for this project and write the page copy.
Never state a rate, APY or expected return: say what the contract does, not
what anyone will earn.

Project: {idea}

Answer with JSON only."""

SCHEMA = json.loads((Path(__file__).parent / "params.schema.json").read_text())


def run(model: str, idea: str, seed: int) -> dict:
    body = {
        "model": model,
        "prompt": PROMPT.format(idea=idea),
        "format": SCHEMA,
        "stream": False,
        "think": False,
        "options": {"temperature": 0.8, "seed": seed, "num_ctx": 4096},
    }
    req = urllib.request.Request(
        "http://127.0.0.1:11434/api/generate",
        data=json.dumps(body).encode(),
        headers={"Content-Type": "application/json"},
    )
    started = time.monotonic()
    with urllib.request.urlopen(req, timeout=1800) as resp:
        out = json.load(resp)
    wall = time.monotonic() - started
    record = {
        "idea": idea,
        "seed": seed,
        "wall_s": round(wall, 2),
        "load_s": out.get("load_duration", 0) / 1e9,
        "prompt_tokens": out.get("prompt_eval_count", 0),
        "prompt_s": out.get("prompt_eval_duration", 0) / 1e9,
        "output_tokens": out.get("eval_count", 0),
        "output_s": out.get("eval_duration", 0) / 1e9,
    }
    record["output_tok_per_s"] = (
        round(record["output_tokens"] / record["output_s"], 2) if record["output_s"] else None
    )
    record["prompt_tok_per_s"] = (
        round(record["prompt_tokens"] / record["prompt_s"], 2) if record["prompt_s"] else None
    )
    try:
        params = json.loads(out["response"])
        record["parses"] = True
    except (json.JSONDecodeError, KeyError):
        record.update(parses=False, valid=False, error="not JSON", raw=out.get("response"))
        return record
    errors = [e.message for e in jsonschema.Draft202012Validator(SCHEMA).iter_errors(params)]
    record["valid"] = not errors
    record["errors"] = errors[:5]
    record["params"] = params
    return record


def main() -> None:
    model, runs, out_path = sys.argv[1], int(sys.argv[2]), Path(sys.argv[3])
    seed0 = int(sys.argv[5]) if len(sys.argv) > 5 and sys.argv[4] == "--seed" else 0
    records = []
    for i in range(runs):
        rec = run(model, IDEAS[(seed0 + i) % len(IDEAS)], seed0 + i)
        records.append(rec)
        print(json.dumps({k: rec[k] for k in ("seed", "wall_s", "output_tok_per_s", "valid")}), flush=True)
    out_path.write_text(json.dumps(records, indent=2))


if __name__ == "__main__":
    main()
