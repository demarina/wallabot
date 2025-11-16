#!/bin/bash
set -e

echo "Generating dataset..."

python ner_cli.py --task generate --data-folder-path /app/data
python ner_cli.py --task train --data-folder-path /app/data --nlp-model-path /app/data

exec "$@"
