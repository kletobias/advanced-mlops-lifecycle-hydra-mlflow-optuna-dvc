output "bucket_name" { value = data.aws_s3_bucket.target.bucket }
output "bucket_arn"  { value = data.aws_s3_bucket.target.arn }
