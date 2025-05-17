FROM python:3.10-slim

# ── minimal system packages ───────────────────────────────────────────
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# ── offline wheel cache ───────────────────────────────────────────────
COPY wheelhouse /app/wheelhouse
ENV PIP_FIND_LINKS=/app/wheelhouse \
    PIP_NO_INDEX=1

# ── install all Python deps from the wheelhouse (no internet) ─────────
RUN pip install torch torchvision torchaudio \
    requests cryptography rich ruff pytest

# ── copy project & set entrypoint ─────────────────────────────────────
WORKDIR /app
COPY . /app

CMD ["python", "-m", "your_entrypoint"]

