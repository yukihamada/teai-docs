variable "environment" {
  description = "Environment name"
  type        = string
}

variable "project_name" {
  description = "Project name"
  type        = string
}

variable "vpc_id" {
  description = "VPC ID"
  type        = string
}

variable "subnet_ids" {
  description = "Subnet IDs for ALB"
  type        = list(string)
}

variable "sg_ids" {
  description = "Security group IDs for ALB"
  type        = list(string)
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 3000
}

variable "domain_name" {
  description = "Domain name"
  type        = string
}

variable "certificate_arn" {
  description = "ACM certificate ARN"
  type        = string
}

variable "log_bucket_id" {
  description = "S3 bucket ID for ALB logs"
  type        = string
  default     = ""
}