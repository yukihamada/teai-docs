# デプロイメントガイド

## インフラストラクチャのセットアップ

### 1. AWSアカウントの準備
- IAMユーザーの作成
- 必要な権限の付与
- アクセスキーの発行

### 2. Terraformの実行
```bash
# 初期化
cd infrastructure
terraform init

# プラン確認
terraform plan

# 適用
terraform apply
```

### 3. ドメインの設定
- Route 53でのゾーン作成
- SSL証明書の取得
- DNSレコードの設定

## アプリケーションのデプロイ

### 1. サービスサイト (www.teai.io)
```bash
# ビルド
cd website
npm run build

# デプロイ
npm run deploy
```

### 2. APIサーバー (api.teai.io)
```bash
# Dockerイメージのビルド
cd api
docker build -t teai-api .

# ECRへのプッシュ
aws ecr get-login-password --region ap-northeast-1 | docker login --username AWS --password-stdin $ECR_REGISTRY
docker tag teai-api:latest $ECR_REGISTRY/teai-api:latest
docker push $ECR_REGISTRY/teai-api:latest

# ECSタスク定義の更新
aws ecs update-service --cluster teai-cluster --service api-service --force-new-deployment
```

### 3. 管理画面 (dashboard.teai.io)
```bash
# ビルド
cd dashboard
npm run build

# デプロイ
npm run deploy
```

### 4. プロキシサーバー
```bash
# Nginxの設定
cd proxy-server
./deploy.sh
```

## 環境変数の設定

### 1. シークレットの管理
```bash
# AWS Systems Managerパラメータストアへの保存
aws ssm put-parameter \
    --name "/teai/prod/DATABASE_URL" \
    --value "postgresql://..." \
    --type "SecureString"
```

### 2. 環境変数の設定
```bash
# ECSタスク定義での環境変数設定
{
  "containerDefinitions": [
    {
      "name": "api",
      "environment": [
        {
          "name": "NODE_ENV",
          "value": "production"
        }
      ],
      "secrets": [
        {
          "name": "DATABASE_URL",
          "valueFrom": "arn:aws:ssm:region:account:parameter/teai/prod/DATABASE_URL"
        }
      ]
    }
  ]
}
```

## データベースのセットアップ

### 1. スキーマの適用
```bash
# マイグレーション実行
cd api
npm run migration:run
```

### 2. 初期データの投入
```bash
# シードデータの実行
npm run seed:run
```

## 監視の設定

### 1. CloudWatchアラームの設定
```bash
# CPU使用率アラーム
aws cloudwatch put-metric-alarm \
    --alarm-name cpu-utilization \
    --comparison-operator GreaterThanThreshold \
    --evaluation-periods 2 \
    --metric-name CPUUtilization \
    --namespace AWS/ECS \
    --period 300 \
    --statistic Average \
    --threshold 70 \
    --alarm-actions arn:aws:sns:region:account:alerts
```

### 2. ログの設定
```bash
# CloudWatch Logsの設定
{
  "logConfiguration": {
    "logDriver": "awslogs",
    "options": {
      "awslogs-group": "/ecs/teai",
      "awslogs-region": "ap-northeast-1",
      "awslogs-stream-prefix": "api"
    }
  }
}
```

## バックアップの設定

### 1. データベースバックアップ
```bash
# RDSスナップショットの自動化
aws rds create-db-snapshot \
    --db-instance-identifier teai-db \
    --db-snapshot-identifier teai-db-snapshot
```

### 2. 設定バックアップ
```bash
# S3バケットへのバックアップ
aws s3 sync /etc/nginx/conf.d/ s3://teai-backups/nginx/
```

## セキュリティ設定

### 1. WAFルールの設定
```bash
# WAFルールの作成
aws wafv2 create-web-acl \
    --name teai-waf \
    --scope REGIONAL \
    --default-action Block={} \
    --rules ...
```

### 2. セキュリティグループの設定
```bash
# セキュリティグループの更新
aws ec2 update-security-group-rule-descriptions-ingress \
    --group-id sg-... \
    --ip-permissions ...
```

## スケーリング設定

### 1. Auto Scalingの設定
```bash
# Auto Scaling設定
aws application-autoscaling register-scalable-target \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/teai-cluster/api-service \
    --min-capacity 2 \
    --max-capacity 10
```

### 2. スケーリングポリシーの設定
```bash
# スケーリングポリシーの作成
aws application-autoscaling put-scaling-policy \
    --policy-name cpu-tracking \
    --service-namespace ecs \
    --scalable-dimension ecs:service:DesiredCount \
    --resource-id service/teai-cluster/api-service \
    --policy-type TargetTrackingScaling \
    --target-tracking-scaling-policy-configuration ...
```

## ロールバック手順

### 1. アプリケーションのロールバック
```bash
# 前バージョンへのロールバック
aws ecs update-service \
    --cluster teai-cluster \
    --service api-service \
    --task-definition teai-api:previous
```

### 2. データベースのロールバック
```bash
# スナップショットからの復元
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier teai-db \
    --db-snapshot-identifier teai-db-snapshot
```

## トラブルシューティング

### 1. デプロイ失敗時
1. CloudWatchログの確認
2. ECSサービスの状態確認
3. ヘルスチェックの確認
4. ロールバックの実行

### 2. パフォーマンス問題
1. メトリクスの確認
2. スロークエリの特定
3. キャッシュの確認
4. スケーリングの調整

### 3. セキュリティインシデント
1. WAFログの確認
2. アクセスログの分析
3. セキュリティグループの確認
4. 必要に応じた遮断