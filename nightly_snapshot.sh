#!/bin/bash
# Upload encrypted weights and metrics to S3
set -e
DATE=$(date +%F)
aws s3 cp global_weights.enc "s3://my-bucket/$DATE/" --acl private
python scripts/encrypt_dataset.py --input scoreboard.csv --output scoreboard.enc
aws s3 cp scoreboard.enc "s3://my-bucket/$DATE/" --acl private
