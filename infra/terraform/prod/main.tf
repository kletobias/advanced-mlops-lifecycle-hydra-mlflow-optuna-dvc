# infra/terraform/prod/main.tf
provider "aws" {
  region = "eu-central-1"
}

module "ghcicd_bucket" {
  source               = "../modules/s3_bucket"
  bucket_name          = "ghcicd"
  public_read_prefixes = ["dvc", "mlruns"]
  tags = {
    Purpose     = "MLops assets"
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}
