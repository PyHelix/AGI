FROM python:3.10-slim

# System deps
RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

# Heavy ML libs (CPU wheels)
RUN pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu

# Core Python deps
RUN pip install requests cryptography rich

WORKDIR /app
COPY . /app

CMD ["python", "-m", "your_entrypoint"]
