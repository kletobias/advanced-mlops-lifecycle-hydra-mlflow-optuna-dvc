# infra/terraform/prod/main.tf
provider "aws" {
  region = "eu-central-1"
  profile = "tobias"
}

module "ghcicd_bucket" {
  source               = "../modules/existing_s3_bucket"
  bucket_name          = "ghcicd"
  public_read_prefixes = ["dvc", "mlruns"]
  tags = {
    Purpose     = "MLops assets"
    Environment = "prod"
    ManagedBy   = "terraform"
  }
}
