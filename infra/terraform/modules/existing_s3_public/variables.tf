variable "bucket_name" {
  type = string
}

variable "public_read_prefixes" {
  type    = list(string)
  default = []
}
