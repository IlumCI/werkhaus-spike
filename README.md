# werkhaus-spike

Phase 0 of the Werkhaus pipeline plan: measurements, not product. Each
workflow answers one question about what a standard GitHub-hosted runner can
do. Results go back into `docs/PIPELINE.md` in the Werkhaus repo.

| Workflow | Question |
|---|---|
| `infer` | How fast and how schema-reliable are 3–7B local models on the runner's CPU, x64 and arm64, cold and cached? |
| `best-of-n` | Do 20 candidates really run in parallel, and how many survive the schema and a forge test? |
| `publish-gate` | Does an environment with a required reviewer hold a deploy until approved? |
| `attest` | Can template bytecode carry signed, verifiable build provenance? |
| `machine` | Can one job host SearXNG, an anvil fork of Robinhood Chain and Chromium? |
