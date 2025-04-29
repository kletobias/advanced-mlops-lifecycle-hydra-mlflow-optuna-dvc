# infra/terraform/modules/s3_bucket/outputs.tf
output "bucket_name" { value = aws_s3_bucket.this.bucket }
output "bucket_arn"  { value = aws_s3_bucket.this.arn }
