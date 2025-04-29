# infra/terraform/prod/backend.tf
terraform {
  backend "s3" {
    bucket         = "ghcicd"
    key            = "terraform/prod/terraform.tfstate"
    region         = "eu-central-1"
    dynamodb_table = "terraform-locks"
    encrypt        = true
  }
}
