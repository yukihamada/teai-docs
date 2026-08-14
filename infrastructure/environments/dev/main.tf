terraform {
  backend "s3" {
    bucket         = "teai-terraform-state"
    key            = "dev/terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "teai-terraform-lock"
    encrypt        = true
  }
}

provider "aws" {
  region = "ap-northeast-1"
}

module "main" {
  source = "../.."

  environment = "dev"
  project_name = "teai"
  domain_name = "teai.io"

  vpc_cidr = "10.0.0.0/16"
  availability_zones = ["ap-northeast-1a", "ap-northeast-1c"]

  # データベース設定
  db_name     = "teai"
  db_username = "teai_admin"
  db_password = var.db_password

  # アプリケーション設定
  app_image = "docker.all-hands.dev/all-hands-ai/openhands:latest"
  app_port  = 3000

  # ECS設定
  task_cpu    = 256
  task_memory = 512
  app_count   = 1

  # タグ設定
  additional_tags = {
    Environment = "dev"
    ManagedBy   = "terraform"
  }
}