FROM python:3.10-slim

ENV PIP_FIND_LINKS=/worker/wheelhouse \
    PIP_NO_INDEX=1

WORKDIR /worker
COPY wheelhouse /worker/wheelhouse

# Install minimal dependencies and GPU optimized torch
RUN apt-get update && apt-get install -y git && rm -rf /var/lib/apt/lists/*
RUN pip install --no-cache-dir torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cu118
RUN pip install --no-cache-dir requests cryptography

COPY . /worker

CMD ["bash"]
