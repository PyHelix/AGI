#!/bin/bash
# Upload encrypted weights and metrics to S3
set -e
DATE=$(date +%F)
aws s3 cp global_weights.enc "s3://my-bucket/$DATE/" --acl private
aws s3 cp scoreboard.csv "s3://my-bucket/$DATE/" --acl private
