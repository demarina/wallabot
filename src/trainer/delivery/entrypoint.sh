#!/bin/bash
set -e

echo "Generating dataset..."
python ner_cli.py --task generate --data-folder-path /app/data
echo "Dataset generated"


echo "Start NER training..."
python ner_cli.py --task train --data-folder-path /app/data --nlp-model-path /app/data
echo "Finish NER training"

exec "$@"
