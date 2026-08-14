terraform {
  required_version = ">= 1.0.0"

  backend "s3" {
    bucket         = "teai-terraform-state"
    key            = "terraform.tfstate"
    region         = "ap-northeast-1"
    dynamodb_table = "teai-terraform-lock"
    encrypt        = true
  }

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
  }
}

provider "aws" {
  region = var.aws_region

  default_tags {
    tags = {
      Environment = var.environment
      Project     = "teai"
      ManagedBy   = "terraform"
    }
  }
}

# VPCモジュール
module "vpc" {
  source = "./modules/vpc"

  environment         = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  project_name       = var.project_name
}

# セキュリティモジュール
module "security" {
  source = "./modules/security"

  environment   = var.environment
  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
}

# ALBモジュール
module "alb" {
  source = "./modules/alb"

  environment   = var.environment
  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.public_subnet_ids
  sg_ids       = [module.security.alb_sg_id]
}

# ECSモジュール
module "ecs" {
  source = "./modules/ecs"

  environment    = var.environment
  project_name  = var.project_name
  vpc_id        = module.vpc.vpc_id
  subnet_ids    = module.vpc.private_subnet_ids
  sg_ids        = [module.security.ecs_sg_id]
  alb_target_group_arn = module.alb.target_group_arn
}

# RDSモジュール
module "rds" {
  source = "./modules/rds"

  environment   = var.environment
  project_name = var.project_name
  vpc_id       = module.vpc.vpc_id
  subnet_ids   = module.vpc.database_subnet_ids
  sg_ids       = [module.security.rds_sg_id]
}

# Route 53モジュール
module "route53" {
  source = "./modules/route53"

  environment   = var.environment
  project_name = var.project_name
  domain_name  = var.domain_name
  alb_dns_name = module.alb.alb_dns_name
  alb_zone_id  = module.alb.alb_zone_id
}

# CloudFrontモジュール
module "cloudfront" {
  source = "./modules/cloudfront"

  environment   = var.environment
  project_name = var.project_name
  domain_name  = var.domain_name
  alb_dns_name = module.alb.alb_dns_name
}