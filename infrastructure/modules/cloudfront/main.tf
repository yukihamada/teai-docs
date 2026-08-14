locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# CloudFront Distribution
resource "aws_cloudfront_distribution" "main" {
  enabled             = true
  is_ipv6_enabled    = true
  price_class        = var.environment == "prod" ? "PriceClass_200" : "PriceClass_100"
  aliases            = ["*.${var.domain_name}"]
  retain_on_delete   = var.environment == "prod"
  wait_for_deployment = false

  # オリジン設定
  origin {
    domain_name = var.alb_dns_name
    origin_id   = "ALB"

    custom_origin_config {
      http_port              = 80
      https_port             = 443
      origin_protocol_policy = "https-only"
      origin_ssl_protocols   = ["TLSv1.2"]
    }
  }

  # デフォルトキャッシュ動作
  default_cache_behavior {
    allowed_methods  = ["DELETE", "GET", "HEAD", "OPTIONS", "PATCH", "POST", "PUT"]
    cached_methods   = ["GET", "HEAD"]
    target_origin_id = "ALB"

    forwarded_values {
      query_string = true
      headers      = ["Host", "Origin", "Authorization"]

      cookies {
        forward = "all"
      }
    }

    viewer_protocol_policy = "redirect-to-https"
    min_ttl                = 0
    default_ttl            = 0
    max_ttl                = 0
    compress               = true
  }

  # 地理的制限
  restrictions {
    geo_restriction {
      restriction_type = "none"
    }
  }

  # SSL証明書
  viewer_certificate {
    acm_certificate_arn      = var.certificate_arn
    minimum_protocol_version = "TLSv1.2_2021"
    ssl_support_method       = "sni-only"
  }

  # WAF（本番環境のみ）
  dynamic "web_acl_id" {
    for_each = var.web_acl_id != "" && var.environment == "prod" ? [var.web_acl_id] : []
    content {
      web_acl_id = web_acl_id.value
    }
  }

  # カスタムエラーレスポンス
  custom_error_response {
    error_code         = 403
    response_code      = 200
    response_page_path = "/index.html"
  }

  custom_error_response {
    error_code         = 404
    response_code      = 200
    response_page_path = "/index.html"
  }

  tags = {
    Name = "${local.name_prefix}-cf"
  }
}

# CloudWatch アラーム（本番環境のみ）
resource "aws_cloudwatch_metric_alarm" "error_rate" {
  count               = var.environment == "prod" ? 1 : 0
  alarm_name          = "${local.name_prefix}-cf-error-rate"
  alarm_description   = "CloudFront error rate"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "TotalErrorRate"
  namespace          = "AWS/CloudFront"
  period             = "300"
  statistic          = "Average"
  threshold          = "5"

  dimensions = {
    DistributionId = aws_cloudfront_distribution.main.id
    Region         = "Global"
  }

  alarm_actions = var.alarm_actions
  ok_actions    = var.alarm_actions
}