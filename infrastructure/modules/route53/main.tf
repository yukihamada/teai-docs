locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# メインのホストゾーン（既存のものを使用）
data "aws_route53_zone" "main" {
  name = var.domain_name
}

# ALBのエイリアスレコード
resource "aws_route53_record" "alb" {
  zone_id = data.aws_route53_zone.main.zone_id
  name    = "*.${var.domain_name}"
  type    = "A"

  alias {
    name                   = var.alb_dns_name
    zone_id                = var.alb_zone_id
    evaluate_target_health = true
  }
}

# ヘルスチェック
resource "aws_route53_health_check" "main" {
  count             = var.environment == "prod" ? 1 : 0
  fqdn              = var.alb_dns_name
  port              = 443
  type              = "HTTPS"
  resource_path     = "/health"
  failure_threshold = "3"
  request_interval  = "30"

  tags = {
    Name = "${local.name_prefix}-health-check"
  }
}

# CloudWatchアラーム（本番環境のみ）
resource "aws_cloudwatch_metric_alarm" "health_check" {
  count               = var.environment == "prod" ? 1 : 0
  alarm_name          = "${local.name_prefix}-route53-health"
  alarm_description   = "Route 53 health check status"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "HealthCheckStatus"
  namespace          = "AWS/Route53"
  period             = "60"
  statistic          = "Minimum"
  threshold          = "1"

  dimensions = {
    HealthCheckId = aws_route53_health_check.main[0].id
  }

  alarm_actions = var.alarm_actions
  ok_actions    = var.alarm_actions
}