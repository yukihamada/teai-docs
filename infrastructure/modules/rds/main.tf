locals {
  name_prefix = "${var.project_name}-${var.environment}"
}

# DB Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${local.name_prefix}-db-subnet"
  subnet_ids = var.subnet_ids

  tags = {
    Name = "${local.name_prefix}-db-subnet"
  }
}

# RDS Parameter Group
resource "aws_db_parameter_group" "main" {
  name   = "${local.name_prefix}-pg"
  family = "postgres14"

  parameter {
    name  = "log_min_duration_statement"
    value = "1000"  # 1秒以上のクエリのみログ
  }

  parameter {
    name  = "autovacuum"
    value = "1"
  }

  tags = {
    Name = "${local.name_prefix}-pg"
  }
}

# RDS Instance
resource "aws_db_instance" "main" {
  identifier = "${local.name_prefix}-db"

  # コスト最適化設定
  instance_class         = var.environment == "prod" ? "db.t4g.small" : "db.t4g.micro"
  multi_az              = var.environment == "prod"
  allocated_storage     = var.environment == "prod" ? 20 : 10
  max_allocated_storage = var.environment == "prod" ? 100 : 20

  engine               = "postgres"
  engine_version       = "14"
  username             = var.db_username
  password             = var.db_password
  db_name             = var.db_name

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = var.sg_ids
  parameter_group_name   = aws_db_parameter_group.main.name

  backup_retention_period = var.environment == "prod" ? 7 : 1
  backup_window          = "17:00-18:00"  # UTC
  maintenance_window     = "Mon:18:00-Mon:19:00"  # UTC

  # パフォーマンスインサイトは本番環境のみ
  performance_insights_enabled = var.environment == "prod"
  performance_insights_retention_period = var.environment == "prod" ? 7 : 0

  # ストレージ設定
  storage_type          = "gp3"
  storage_encrypted     = true

  # 自動マイナーバージョンアップグレード
  auto_minor_version_upgrade = var.environment == "prod"

  # 削除保護は本番環境のみ
  deletion_protection = var.environment == "prod"
  skip_final_snapshot = var.environment != "prod"

  # モニタリング設定
  monitoring_interval = var.environment == "prod" ? 60 : 0
  enabled_cloudwatch_logs_exports = var.environment == "prod" ? ["postgresql", "upgrade"] : []

  tags = {
    Name = "${local.name_prefix}-db"
  }
}

# CloudWatch アラーム（本番環境のみ）
resource "aws_cloudwatch_metric_alarm" "db_cpu" {
  count               = var.environment == "prod" ? 1 : 0
  alarm_name          = "${local.name_prefix}-db-cpu"
  alarm_description   = "Database CPU utilization"
  comparison_operator = "GreaterThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "CPUUtilization"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "80"

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = var.alarm_actions
  ok_actions    = var.alarm_actions
}

# CloudWatch アラーム - ストレージ
resource "aws_cloudwatch_metric_alarm" "db_storage" {
  count               = var.environment == "prod" ? 1 : 0
  alarm_name          = "${local.name_prefix}-db-storage"
  alarm_description   = "Database free storage space"
  comparison_operator = "LessThanThreshold"
  evaluation_periods  = "2"
  metric_name        = "FreeStorageSpace"
  namespace          = "AWS/RDS"
  period             = "300"
  statistic          = "Average"
  threshold          = "5000000000"  # 5GB

  dimensions = {
    DBInstanceIdentifier = aws_db_instance.main.id
  }

  alarm_actions = var.alarm_actions
  ok_actions    = var.alarm_actions
}