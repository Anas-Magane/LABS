# BlueOffice Breach - Challenge: AI Vault, prompt-injection (port 7000)
# Isolated, non-root Flask service backed by two genuine local,
# open-weights models, both GGUF, both running fully offline via
# llama.cpp: Qwen2.5-1.5B-Instruct (the chat assistant) and
# all-MiniLM-L6-v2 (a small sentence-embedding model used as the
# semantic guard - see app.py). Both sets of weights are baked into the
# image at build time and inference runs entirely on-CPU inside the
# container - no external API, no internet egress at runtime, matching
# every other service in this repo.
#
# Multi-stage build: llama-cpp-python has no prebuilt wheel for every
# platform this repo targets, so stage 1 compiles it from source into a
# wheel (build-essential + cmake only exist in that stage) and stage 2
# installs the wheel into a clean, much smaller final image.

FROM python:3.11-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
        build-essential \
        cmake \
        git \
    && rm -rf /var/lib/apt/lists/*

RUN pip wheel --no-cache-dir --wheel-dir /wheels llama-cpp-python==0.3.35

FROM python:3.11-slim

LABEL challenge="blueoffice-ai-vault7000"

# libgomp1 is the OpenMP runtime the compiled llama.cpp shared library
# needs at load time (it's built with OpenMP support by default) - it
# must stay installed. curl/ca-certificates are only needed transiently
# to fetch the model weights and are purged again in this same layer.
RUN apt-get update && apt-get install -y --no-install-recommends curl ca-certificates libgomp1 \
    && mkdir -p /app/model \
    && curl -fL -o /app/model/qwen2.5-1.5b-instruct-q4_k_m.gguf \
        "https://huggingface.co/Qwen/Qwen2.5-1.5B-Instruct-GGUF/resolve/main/qwen2.5-1.5b-instruct-q4_k_m.gguf" \
    && curl -fL -o /app/model/all-MiniLM-L6-v2-Q8_0.gguf \
        "https://huggingface.co/second-state/All-MiniLM-L6-v2-Embedding-GGUF/resolve/main/all-MiniLM-L6-v2-Q8_0.gguf" \
    && apt-get purge -y curl \
    && apt-get autoremove -y \
    && rm -rf /var/lib/apt/lists/*

RUN groupadd -r aivault && useradd -r -g aivault -m -d /home/aivault -s /usr/sbin/nologin aivault

WORKDIR /app
COPY --from=builder /wheels /wheels
COPY requirements.txt .
RUN pip install --no-cache-dir /wheels/*.whl -r requirements.txt && rm -rf /wheels

COPY app.py /app/app.py
COPY templates/ /app/templates/

RUN chown -R aivault:aivault /app /home/aivault

USER aivault

ENV MODEL_PATH=/app/model/qwen2.5-1.5b-instruct-q4_k_m.gguf
ENV EMBED_MODEL_PATH=/app/model/all-MiniLM-L6-v2-Q8_0.gguf
ENV N_THREADS=2

EXPOSE 5000

HEALTHCHECK --interval=30s --timeout=10s --start-period=90s --retries=3 \
    CMD python3 -c "import urllib.request; urllib.request.urlopen('http://127.0.0.1:5000/', timeout=8)" || exit 1

# Single worker: the model is loaded once into that worker's memory.
# Multiple threads let requests queue behind the model lock in app.py
# instead of being dropped while one inference call is in flight.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "1", "--threads", "4", "--timeout", "120", "app:app"]
