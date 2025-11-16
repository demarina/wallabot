FROM python:3.11-slim-bookworm

WORKDIR /app

RUN mkdir /app/data

COPY ner.py ner.py
COPY ner_cli.py ner_cli.py
#COPY data /app/data

RUN apt-get update && apt-get install -y build-essential gcc -y

VOLUME /app/data

RUN python -m pip install tqdm
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY delivery/entrypoint.sh entrypoint.sh

ENTRYPOINT ["./entrypoint.sh"]
