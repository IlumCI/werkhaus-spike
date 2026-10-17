#!/usr/bin/env bash
# Install Ollama and serve it as the runner user, models in $OLLAMA_MODELS so
# actions/cache can save and restore them. Prints how long each part took.
set -euo pipefail
: "${OLLAMA_MODELS:?set OLLAMA_MODELS}"
mkdir -p "$OLLAMA_MODELS"

t0=$(date +%s)
curl -fsSL https://ollama.com/install.sh | sh >/dev/null
sudo systemctl stop ollama 2>/dev/null || true
t1=$(date +%s)
echo "install_s=$((t1 - t0))" >> "$GITHUB_OUTPUT"

nohup ollama serve > "$RUNNER_TEMP/ollama.log" 2>&1 &
for _ in $(seq 1 60); do
  curl -sf http://127.0.0.1:11434/api/version >/dev/null && break
  sleep 1
done
ollama --version
