terraform {
  backend "s3" {
    bucket       = "ghcicd"
    key          = "terraform/prod/terraform.tfstate"
    region       = "eu-central-1"
    # optional, enables native object-lock instead of DynamoDB
    use_lockfile = true
  }
}
