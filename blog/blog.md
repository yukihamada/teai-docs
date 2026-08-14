# 🎉 teai.io CLI (Sente) 完全自動化マルチエージェント実装 & 公開ブログ

## 1️⃣ 背景
teai.io は「日本語・低レイテンシ・95+モデルを1 APIキーで」提供するAIエージェント基盤です。  
既存の `te` コマンドは **単一タスク** しか扱えないため、マルチエージェント（複数エージェントが協働）を実装したいという要望がありました。

## 2️⃣ 実装した機能一覧
| 機能 | 実装内容 | 主なコマンド例 |
|------|----------|----------------|
| **プロファイル管理** | `te --profile <name>` で複数の APIキーを別ディレクトリに保管 | `te --profile work login` |
| **自動通知** | 完了・失敗時に macOS 通知 (`osascript` / `terminal-notifier`) | `te login` → 完了通知 |
| **テーマ切替** | CLI 出力の暗・明テーマ切替 (`te theme light|dark`) | `te theme dark` |
| **エラー自動リトライ** | 5xx/429 系エラーは指数バックオフで最大 3 回まで自動リトライ | `te run "..." --retry 5` |
| **エージェントテンプレート拡張** | `te agents init <name> --template <type>` で UI/CLI/Research などテンプレート選択 | `te agents init my-agent --template cli` |
| **コスト可視化** | `te stats` が残クレジット・推定チャット数を表示 | `te stats` |
| **スキーマ検証** | `te schema` が `opencode.json` の必須項目 (`model`, `provider`) をチェック | `te schema` |
| **Git 連携 (予備)** | `te git-commit` で自動 `git add` と AI 生成コミットメッセージ | `te git-commit -m "fix bug"` |
| **テストスイート (簡易)** | `te test <scenario>` が事前定義シナリオを実行し ✅/❌ で結果表示 | `te test quick_check` |

## 3️⃣ 主な変更点
### 3.1 `~/.local/bin/te` 本体
- プロファイルディレクトリ `~/.config/teai/profiles/` を追加し、プロファイルごとに別キーを管理  
- `cmd_login`, `cmd_rotate_key` がプロファイル名を取得し、書き換え・検証を行う  
- `cmd_theme` 追加 → `te theme light|dark`  
- `cmd_stats` に残クレジット・推定チャット数を表示  
- `cmd_agents_init` が `--template` オプションを受け取る拡張  
- `cmd_test` 追加 → 簡易テストシナリオ実行 → 結果を `✅/❌` で出力  

### 3.2 設定ファイル
- `~/.config/teai/opencode.json` はそのまま使用。  
- `instructions` に `~/.config/teai/sente-rules.md`（コードスキル）を追加し、マルチエージェントでも同じルールを適用。  

### 3.3 追加コマンド
```bash
# ① ログイン（ダッシュボード自動開く）
te login --profile work

# ② APIキーローテーション
te rotate-key --profile work

# ③ テーマ切替
te theme dark

# ④ 統計取得
te stats --profile work

# ⑤ エージェントテンプレート生成
te agents init sample-agent --template cli --profile work

# 6️⃣ ドキュメント自動生成
te docs --profile work   # docs/overview.md が作成される

# 7️⃣ テストスイート実行
te test quick_check --profile work   # ✅/❌ が出る
```

## 4️⃣ ローカルテスト実施手順
```bash
# ① テスト用プロファイル作成
te login --profile test

# ② スキーマ検証
te schema --profile test

# ③ 統計取得
te stats --profile test

# ④ エージェントテンプレート生成
te agents init test-agent --template ui --profile test

# ⑤ エラー自動リトライ確認（例：意図的に不正なエンドポイントへリクエスト）
te run "curl -s -o /dev/null -w '%{http_code}' https://api.teai.io/invalid" --retry 5 --profile test
```
上記コマンドはすべて **exit 0** で終了し、通知が出れば成功です。

## 5️⃣ マルチエージェントの活用例
```bash
# 例：複数プロファイルで同時にタスク実行
te run "--profile work" "curl -s https://api.teai.io/v1/models" &
te run "--profile personal" "curl -s https://api.teai.io/v1/models" &
wait
```
複数プロファイルを同時に走らせることで、**開発・運用・監視** を同時並行で行えるようになります。

## 6️⃣ 今後の展望
| 項目 | 予定 |
|------|------|
| **Git 連携** | `te git-commit` で自動 `git add`・`git commit -m "..."`、コミットメッセージは AI が生成 |
| **CI 統合** | GitHub Actions に `te test` を組み込み、PRごとに自動テストを走らせる |
| **ブログ自動生成** | `te blog generate` が `~/workspace/teai-blog/` に新しい Markdown を作成し、`git push` で自動デプロイ |
| **マルチモーダル出力** | `te multimodal <prompt>` → 画像生成（Gemini）や音声合成（KOE）を同時呼び出し |

## 7️⃣ まとめ
- **マルチプロファイル** と **自動リトライ**、テーマ切替など、日常的な開発・運用タスクが **1 行** で完結。  
- **エージェントテンプレート** を使えば、UI・CLI・Research など用途別に即スイッチでき、チーム間での共通基盤が確立。  
- すべての変更は **ローカルだけ** で完結し、CI/CD パイプラインへもそのまま組み込み可能です。

> **🚀 完成！**  
> 本ブログは `teai.io` の公式開発ブログに掲載予定です。  
> ぜひ `te` を試してみて、フィードバックを `teai.io/dashboard` から送ってください 🙌
