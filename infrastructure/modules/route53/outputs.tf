output "zone_id" {
  description = "Route 53 hosted zone ID"
  value       = data.aws_route53_zone.main.zone_id
}

output "domain_name" {
  description = "Domain name"
  value       = var.domain_name
}

output "health_check_id" {
  description = "Route 53 health check ID"
  value       = var.environment == "prod" ? aws_route53_health_check.main[0].id : null
}