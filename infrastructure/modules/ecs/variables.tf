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
  description = "Subnet IDs for ECS tasks"
  type        = list(string)
}

variable "sg_ids" {
  description = "Security group IDs for ECS tasks"
  type        = list(string)
}

variable "app_port" {
  description = "Application port"
  type        = number
  default     = 3000
}

variable "app_image" {
  description = "Docker image for the application"
  type        = string
}

variable "task_cpu" {
  description = "Task CPU units"
  type        = number
  default     = 256 # 0.25 vCPU
}

variable "task_memory" {
  description = "Task memory (MiB)"
  type        = number
  default     = 512
}

variable "container_cpu" {
  description = "Container CPU units"
  type        = number
  default     = 256
}

variable "container_memory" {
  description = "Container memory limit (MiB)"
  type        = number
  default     = 512
}

variable "desired_count" {
  description = "Desired number of tasks"
  type        = number
  default     = 1
}

variable "min_capacity" {
  description = "Minimum number of tasks"
  type        = number
  default     = 1
}

variable "max_capacity" {
  description = "Maximum number of tasks"
  type        = number
  default     = 4
}

variable "target_group_arn" {
  description = "ALB target group ARN"
  type        = string
}

variable "environment_variables" {
  description = "Environment variables for the container"
  type        = list(object({
    name  = string
    value = string
  }))
  default = []
}

variable "secrets" {
  description = "Secrets for the container"
  type        = list(object({
    name      = string
    valueFrom = string
  }))
  default = []
}