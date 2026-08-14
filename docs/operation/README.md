# 運用ガイド

## 日常運用

### 1. 監視業務
- CloudWatchダッシュボードの確認
- アラートの確認と対応
- リソース使用率の確認
- パフォーマンスメトリクスの確認

### 2. バックアップ確認
- データベースバックアップの確認
- 設定ファイルのバックアップ確認
- バックアップの整合性チェック
- リストアテスト

### 3. セキュリティ確認
- WAFログの確認
- セキュリティアラートの確認
- 脆弱性スキャンの実施
- セキュリティパッチの適用

## インシデント対応

### 1. システム障害
```bash
# ログの確認
aws logs get-log-events \
    --log-group-name /ecs/teai \
    --log-stream-name api/xxxxx

# メトリクスの確認
aws cloudwatch get-metric-statistics \
    --namespace AWS/ECS \
    --metric-name CPUUtilization \
    --dimensions Name=ClusterName,Value=teai-cluster \
    --start-time ... \
    --end-time ... \
    --period 300 \
    --statistics Average
```

### 2. セキュリティインシデント
1. 初動対応
   - 影響範囲の特定
   - 一時的な遮断
   - ログの保全

2. 原因調査
   - ログ分析
   - アクセスパターン分析
   - 脆弱性調査

3. 復旧対応
   - パッチ適用
   - 設定変更
   - 監視強化

### 3. パフォーマンス問題
1. 問題の切り分け
   - ボトルネックの特定
   - リソース使用率の確認
   - スロークエリの特定

2. 対応策の実施
   - スケーリング
   - キャッシュ調整
   - クエリ最適化

## 定期メンテナンス

### 1. パッチ適用
```bash
# セキュリティパッチの適用
aws ssm send-command \
    --document-name "AWS-RunPatchBaseline" \
    --targets "Key=tag:Environment,Values=production" \
    --parameters "Operation=Install"
```

### 2. リソース最適化
- 未使用リソースの特定
- コスト最適化
- パフォーマンスチューニング

### 3. バックアップ管理
- 古いバックアップの削除
- バックアップ世代管理
- リストアテスト

## 顧客サポート

### 1. 問い合わせ対応
- チケット管理
- エスカレーションフロー
- 対応履歴管理

### 2. アカウント管理
- アカウント作成/削除
- 権限管理
- 請求管理

### 3. 技術サポート
- トラブルシューティング
- 設定支援
- ベストプラクティス提供

## パフォーマンス管理

### 1. 負荷監視
```bash
# ECSサービスの負荷確認
aws ecs describe-services \
    --cluster teai-cluster \
    --services api-service

# RDS負荷確認
aws rds describe-db-instances \
    --db-instance-identifier teai-db
```

### 2. キャパシティ管理
- リソース使用率の予測
- スケーリング閾値の調整
- キャパシティプランニング

### 3. パフォーマンスチューニング
- アプリケーション最適化
- データベース最適化
- キャッシュ戦略の調整

## コスト管理

### 1. コスト監視
```bash
# コストと使用状況レポート
aws ce get-cost-and-usage \
    --time-period Start=2025-01-01,End=2025-01-31 \
    --granularity MONTHLY \
    --metrics "BlendedCost" "UnblendedCost" "UsageQuantity"
```

### 2. コスト最適化
- リザーブドインスタンスの活用
- オートスケーリングの最適化
- ストレージ使用量の最適化

### 3. 予算管理
- 予算設定
- アラート設定
- コスト予測

## セキュリティ管理

### 1. アクセス管理
```bash
# IAMポリシーの確認
aws iam list-policies \
    --scope Local \
    --only-attached

# セキュリティグループの確認
aws ec2 describe-security-groups \
    --group-ids sg-...
```

### 2. 脆弱性管理
- 定期スキャン
- パッチ管理
- セキュリティ評価

### 3. コンプライアンス管理
- 監査ログの管理
- コンプライアンスチェック
- セキュリティレポート

## 障害復旧

### 1. バックアップリストア
```bash
# RDSスナップショットからのリストア
aws rds restore-db-instance-from-db-snapshot \
    --db-instance-identifier teai-db-restored \
    --db-snapshot-identifier teai-db-snapshot

# ECSタスク定義のロールバック
aws ecs update-service \
    --cluster teai-cluster \
    --service api-service \
    --task-definition previous-version
```

### 2. フェイルオーバー
- マルチAZ切り替え
- DNSフェイルオーバー
- アプリケーションフェイルオーバー

### 3. 災害復旧
- DRサイトへの切り替え
- データ同期確認
- サービス復旧手順

## 改善活動

### 1. モニタリング改善
- メトリクスの見直し
- アラート閾値の調整
- 監視項目の追加

### 2. 自動化推進
- 運用タスクの自動化
- CI/CDパイプラインの改善
- 障害対応の自動化

### 3. ドキュメント管理
- 手順書の更新
- ナレッジベースの整備
- トラブルシューティングガイドの更新