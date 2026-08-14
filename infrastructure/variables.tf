variable "aws_region" {
  description = "AWS region"
  type        = string
  default     = "ap-northeast-1"
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
  default     = "teai"
}

variable "domain_name" {
  description = "Domain name"
  type        = string
  default     = "teai.io"
}

variable "vpc_cidr" {
  description = "VPC CIDR block"
  type        = string
  default     = "10.0.0.0/16"
}

variable "availability_zones" {
  description = "Availability zones"
  type        = list(string)
  default     = ["ap-northeast-1a", "ap-northeast-1c"]
}

# データベース設定
variable "database_name" {
  description = "Database name"
  type        = string
  default     = "teai"
}

variable "database_username" {
  description = "Database username"
  type        = string
  default     = "teai_admin"
}

variable "database_password" {
  description = "Database password"
  type        = string
  sensitive   = true
}

# ECS設定
variable "container_insights" {
  description = "Enable container insights"
  type        = bool
  default     = true
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 3000
}

variable "app_count" {
  description = "Number of application containers"
  type        = number
  default     = 2
}

# Route 53設定
variable "create_root_zone" {
  description = "Whether to create root zone"
  type        = bool
  default     = false
}

# CloudFront設定
variable "enable_waf" {
  description = "Enable WAF for CloudFront"
  type        = bool
  default     = true
}

# バックアップ設定
variable "backup_retention_period" {
  description = "Backup retention period in days"
  type        = number
  default     = 7
}

# モニタリング設定
variable "enable_enhanced_monitoring" {
  description = "Enable enhanced monitoring"
  type        = bool
  default     = true
}

# タグ設定
variable "additional_tags" {
  description = "Additional tags"
  type        = map(string)
  default     = {}