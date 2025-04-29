AWS_PROFILE ?= tobias
TF_DIR      := infra/terraform/prod

tf-init:      ; cd $(TF_DIR) && terraform init
tf-plan:      ; cd $(TF_DIR) && terraform plan
tf-apply:     ; cd $(TF_DIR) && terraform apply -auto-approve
tf-import:    ; cd $(TF_DIR) && terraform import \
                 'module.ghcicd_bucket.aws_s3_bucket.this' ghcicd
