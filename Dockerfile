FROM python:3.10-slim

# Minimal system deps
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# Offline wheels
COPY wheelhouse /app/wheelhouse
ENV PIP_FIND_LINKS=/app/wheelhouse \
    PIP_NO_INDEX=1

# Install packages from wheelhouse (no internet)
RUN pip install torch torchvision torchaudio \
    requests cryptography rich ruff pytest

WORKDIR /app
COPY . /app

CMD ["python", "-m", "your_entrypoint"]
]
