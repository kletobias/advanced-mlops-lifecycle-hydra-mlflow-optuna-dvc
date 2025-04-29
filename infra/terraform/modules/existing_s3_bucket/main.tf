data "aws_s3_bucket" "target" {
  bucket = var.bucket_name
}

resource "aws_s3_bucket_public_access_block" "allow_public" {
  bucket                  = data.aws_s3_bucket.target.id
  block_public_acls       = false
  ignore_public_acls      = false
  block_public_policy     = false
  restrict_public_buckets = false
}

data "aws_iam_policy_document" "public_read" {
  statement {
    sid     = "PublicReadPrefixes"
    effect  = "Allow"
    actions = ["s3:GetObject"]

    principals {
      type        = "*"
      identifiers = ["*"]
    }

    resources = [
      for p in var.public_read_prefixes :
      "${data.aws_s3_bucket.target.arn}/${trim(p, "/")}/*"
    ]
  }
}

resource "aws_s3_bucket_policy" "public_read" {
  bucket = data.aws_s3_bucket.target.id
  policy = data.aws_iam_policy_document.public_read.json
}
