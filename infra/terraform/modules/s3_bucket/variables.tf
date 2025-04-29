# infra/terraform/modules/s3_bucket/variables.tf
variable "bucket_name"         { type = string }
variable "public_read_prefixes" { type = list(string) default = [] }
variable "kms_key_id"          { type = string       default = "" }
variable "versioning"          { type = bool         default = true }
variable "tags"                { type = map(string)  default = {} }
