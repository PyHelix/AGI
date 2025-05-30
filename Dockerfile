FROM python:3.10-slim

# minimal system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /app
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# copy project & set entrypoint
COPY . /app
CMD ["python", "-m", "your_entrypoint"]
