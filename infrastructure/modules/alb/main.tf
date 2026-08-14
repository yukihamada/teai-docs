locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# Application Load Balancer
resource "aws_lb" "main" {
  name               = "${local.name_prefix}-alb"
  internal           = false
  load_balancer_type = "application"
  security_groups    = var.sg_ids
  subnets           = var.subnet_ids

  # コスト最適化のための設定
  enable_deletion_protection = var.environment == "prod"
  idle_timeout              = 60

  # アクセスログは本番環境のみ有効化
  dynamic "access_logs" {
    for_each = var.environment == "prod" ? [1] : []
    content {
      bucket  = var.log_bucket_id
      prefix  = "alb-logs"
      enabled = true
    }
  }

  tags = {
    Name = "${local.name_prefix}-alb"
  }
}

# デフォルトのターゲットグループ
resource "aws_lb_target_group" "main" {
  name        = "${local.name_prefix}-tg"
  port        = var.app_port
  protocol    = "HTTP"
  vpc_id      = var.vpc_id
  target_type = "ip"

  health_check {
    enabled             = true
    healthy_threshold   = 2
    interval            = 30
    matcher            = "200-299"
    path               = "/health"
    port               = "traffic-port"
    protocol           = "HTTP"
    timeout            = 5
    unhealthy_threshold = 3
  }

  tags = {
    Name = "${local.name_prefix}-tg"
  }
}

# HTTPリスナー（HTTPSにリダイレクト）
resource "aws_lb_listener" "http" {
  load_balancer_arn = aws_lb.main.arn
  port              = "80"
  protocol          = "HTTP"

  default_action {
    type = "redirect"

    redirect {
      port        = "443"
      protocol    = "HTTPS"
      status_code = "HTTP_301"
    }
  }
}

# HTTPSリスナー
resource "aws_lb_listener" "https" {
  load_balancer_arn = aws_lb.main.arn
  port              = "443"
  protocol          = "HTTPS"
  ssl_policy        = "ELBSecurityPolicy-TLS13-1-2-2021-06"
  certificate_arn   = var.certificate_arn

  default_action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }
}

# ホストベースのルーティングルール
resource "aws_lb_listener_rule" "host_based" {
  listener_arn = aws_lb_listener.https.arn
  priority     = 1

  action {
    type             = "forward"
    target_group_arn = aws_lb_target_group.main.arn
  }

  condition {
    host_header {
      values = ["*.${var.domain_name}"]
    }
  }
}