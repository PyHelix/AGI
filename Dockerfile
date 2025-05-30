FROM python:3.10-slim

# minimal system packages
RUN apt-get update && \
    apt-get install -y --no-install-recommends git && \
    rm -rf /var/lib/apt/lists/*

# install Python dependencies
COPY requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

# copy project & set entrypoint
WORKDIR /app
COPY . /app
CMD ["python", "-m", "your_entrypoint"]
