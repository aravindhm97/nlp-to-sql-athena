#!/bin/bash
set -e

# Parse arguments
while [[ $# -gt 0 ]]; do
  case $1 in
    --region) AWS_REGION="$2"; shift ;;
    --bucket-prefix) BUCKET_PREFIX="$2"; shift ;;
    --athena-db) ATHENA_DB="$2"; shift ;;
    *) echo "Unknown parameter: $1"; exit 1 ;;
  esac
  shift
done

# Create S3 buckets
DATA_BUCKET="${BUCKET_PREFIX}-data"
RESULTS_BUCKET="${BUCKET_PREFIX}-results"

aws s3api create-bucket \
  --bucket "$DATA_BUCKET" \
  --region "$AWS_REGION" \
  --create-bucket-configuration LocationConstraint="$AWS_REGION" 2>/dev/null || true

aws s3api create-bucket \
  --bucket "$RESULTS_BUCKET" \
  --region "$AWS_REGION" \
  --create-bucket-configuration LocationConstraint="$AWS_REGION" 2>/dev/null || true

# Upload sample data
aws s3 cp data/sales_data.csv "s3://$DATA_BUCKET/"

# Create Athena table
python scripts/create_athena_table.py \
  --region "$AWS_REGION" \
  --bucket "$DATA_BUCKET" \
  --database "$ATHENA_DB"

echo "AWS SETUP COMPLETE"
echo "DATA_BUCKET=$DATA_BUCKET"
echo "RESULTS_BUCKET=$RESULTS_BUCKET"
echo "ATHENA_DB=$ATHENA_DB"
