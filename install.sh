#!/usr/bin/env bash
set -euo pipefail
cd "$(dirname "$0")"
docker compose version >/dev/null
docker compose build
# Recréer le réseau pour permettre les téléchargements initiaux.
docker compose down
docker compose -f compose.yaml -f compose.install.yaml up -d --wait ollama
trap 'docker compose -f compose.yaml -f compose.install.yaml down' EXIT
docker compose -f compose.yaml -f compose.install.yaml exec -T ollama ollama pull qwen3:4b
docker compose -f compose.yaml -f compose.install.yaml run --rm --no-deps -e HF_HUB_OFFLINE=0 app python -c 'from faster_whisper import WhisperModel; WhisperModel("small", device="cpu", compute_type="int8", download_root="/models")'
docker compose -f compose.yaml -f compose.install.yaml down
trap - EXIT
docker compose up -d
echo 'Prêt : http://localhost:8501 (sur le serveur, ou via tunnel SSH).'
