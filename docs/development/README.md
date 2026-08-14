# 開発ガイド

## 開発環境セットアップ

### 必要条件
- Node.js 18以上
- Docker
- AWS CLI
- Terraform
- Make

### ローカル環境構築
```bash
# リポジトリのクローン
git clone https://github.com/teai-io/teai-platform.git
cd teai-platform

# 依存関係のインストール
make setup

# 環境変数の設定
cp .env.example .env
# .envファイルを編集

# 開発サーバーの起動
make dev
```

## プロジェクト構成

```
teai-platform/
├── website/              # メインサービスサイト (Next.js)
│   ├── pages/           # ページコンポーネント
│   ├── components/      # 共通コンポーネント
│   ├── styles/         # スタイル定義
│   └── public/         # 静的アセット
├── infrastructure/      # Terraform設定
├── proxy-server/       # Nginxプロキシ設定
├── dashboard/          # 管理画面フロントエンド
├── api/                # バックエンドAPI
├── docs/              # ドキュメント
└── scripts/           # デプロイメントスクリプト
```

## 開発フロー

### 1. ブランチ戦略
- main: 本番環境
- staging: ステージング環境
- develop: 開発環境
- feature/*: 機能開発
- hotfix/*: 緊急修正

### 2. コミットメッセージ規約
```
feat: 新機能
fix: バグ修正
docs: ドキュメントのみの変更
style: コードスタイルの変更
refactor: リファクタリング
test: テストコード
chore: ビルドプロセス等の変更
```

### 3. レビュープロセス
1. PRの作成
2. CIチェック
3. コードレビュー
4. 承認
5. マージ

## テスト

### ユニットテスト
```bash
# 全テストの実行
npm test

# 特定のテストの実行
npm test -- -t "test name"

# カバレッジレポート
npm run test:coverage
```

### E2Eテスト
```bash
# Cypressテストの実行
npm run cypress:open

# ヘッドレスモード
npm run cypress:run
```

## デバッグ

### ログ確認
```bash
# アプリケーションログ
make logs app

# Nginxログ
make logs nginx

# APIログ
make logs api
```

### メトリクス確認
```bash
# リソース使用率
make metrics

# パフォーマンス
make performance
```

## API開発

### エンドポイント追加
1. ルート定義
2. コントローラー作成
3. サービス実装
4. テスト作成
5. ドキュメント更新

### OpenAPI仕様
- 仕様書の生成
- クライアントの生成
- バリデーション

## フロントエンド開発

### コンポーネント開発
1. Storybookでの開発
2. テスト作成
3. ドキュメント作成

### 状態管理
- Zustandの使用
- キャッシュ戦略
- パフォーマンス最適化

## セキュリティ

### セキュリティチェック
```bash
# 依存関係のチェック
npm audit

# コードスキャン
make security-scan

# 脆弱性テスト
make pentest
```

### コードクオリティ
```bash
# リンター実行
npm run lint

# 型チェック
npm run type-check

# フォーマット
npm run format
```

## パフォーマンス最適化

### フロントエンド
- バンドルサイズ最適化
- 画像最適化
- レンダリング最適化

### バックエンド
- キャッシュ戦略
- クエリ最適化
- N+1問題の解決

## トラブルシューティング

### 一般的な問題
1. 環境変数の確認
2. 依存関係の更新
3. キャッシュのクリア
4. ログの確認

### デバッグツール
- Chrome DevTools
- React Developer Tools
- Redux DevTools
- Postman