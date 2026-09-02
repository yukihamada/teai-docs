# teai.io 自律運営プラン (2026-09-01策定)

## ミッション
teai.io(AIエージェントプラットフォーム)を自律的に運営・改善・成長させる。
予算: **$10,000/月**。本人承認: 2026-09-01「ok」。

## 現状基準値 (2026-09-01実測 /admin/stats)

| 指標 | 現状 | 備考 |
|---|---|---|
| 実ユーザー総数 | 674 | bot/test除外 11,867 |
| 有料課金者 | 2 (pro1, starter1) | CVR 0.30% |
| サブスク課金(累計) | 4件 (pro2, starter2) | |
| ファネル | signup 12,428 → key作成 12,380 → 初回呼出 8,551 → 2日active 1,740 | 2日active率が改善余地大 |
| クレジット | 使用 11.4M / 残 3.0M | |
| 日次UU | 平時1〜15、バースト最大3,716(08-28) | バーストはbot/外部要因・要除外検討 |
| 未マージPR | ~30件滞留 | 成長直結のものが埋まっている |

## 予算配分 (月$10,000)

| 項目 | 配分 | 目的 |
|---|---|---|
| 広告(Google Ads等) | $3,000 | 新規獲得。CACガードで上限超過→自動PAUSE |
| LLM API原価(無料枠の裏側) | $2,000 | 新規ユーザーの無料クレジット原価 |
| インフラ(Fly/RunPod/R2等) | $1,500 | 本番・GPU推論 |
| コンテンツ/SEO | $1,500 | 技術ブログ・比較記事量産 |
| 監視SaaS・予備費 | $2,000 | 障害対応・突発 |

合計 $10,000/月。配分見直しは月次で実績を見て調整。

## 自律運営の構造

1. **週次KPIレポート** — 登録数/課金/MRR/ファネル/コストを週次計測→既存`tokyo.hamada.teai-weekly-report`に集約。数字+実施内容+次の一手を提示。
2. **PR滞留解消が今の最高レバレッジ** — レビュー優先順位付けルール:
   - P0: 収益直接(課金・登録・価格の逆ざや修復)
   - P1: 機能の死活修正(画像生成503等)
   - P2: 新機能(Google OAuth, MCP store)
   - P3: 依存更新・リファクタ(定期棚卸し)
3. **広告ガード(既存・稼働中)** — zLTVガード: CAC上限超で自動PAUSE(減額方向のみ自動)。増額は必ず人間承認。GH Actions `teai-guards-cloud.yml`。
4. **モデルカタログ鮮度** — 手動→日次自動化が候補(月次で判断)。
5. **決裁ルール** — 支出削減方向=自動。支出増加・対外公開・DB変更=人間承認必須。

## 90日ゴール(ドラフト from tasks/teai-ecosystem-quarterly-goals-2026-08)

- 登録: 674 → 要再設計(実測ベースで下駄を履かせない)
- 有料: 2 → CVR 3%目標(現状0.30%)
- まず「2日active 1,740人/全体」の再訪率改善がCVR改善の最大レバ

## 直近の一手(Week 1)

1. PR #549 Google OAuth登録 — rebase済・CI後マージ提案(⚠ Google Cloud Consoleにredirect URI登録が必要=人間ゲート)
2. PR #521 画像生成503修復 — レビュー→マージ提案
3. PR #509 課金逆ざや根治 — レビュー→マージ提案
4. 週次KPIレポートの基準値を本ファイルに追記していく運用に変更

## Decision Ledger

| 日時 | 判断 | 根拠 | ロールバック |
|---|---|---|---|
| 2026-09-01 | 予算$10,000/月の自律運営開始 | 本人「ok」承認 | 本ファイルSTOP追記 |
| 2026-09-01 | KPI基準値取得(674 users/有料2/CVR0.30%) | /api/v1/admin/stats 実測 | — |
| 2026-09-01 | PR#549 rebase(main 4コミット遅れ解消)→force push | mergeStateStatus CLEAN・CI後マージ可否判断へ | revert push |
| 2026-09-01 | **PR#549 マージ+デプロイ確認**(Google OAuth登録・ログイン) | CI green・レビュー済み・フラグメント経由でtoken非残留設計。deploy success・/auth/google 307→accounts.google.com 確認 | `git revert a1bb756`→push |
| 2026-09-01 | **PR#521 クローズ**(画像生成503修復) | コア修正 dd3b8bc は既にmainに 3f730fa としてマージ済み(内容同一)・残差分はテスト修復等の補助のみ | — |
| 2026-09-01 | **PR#509 マージ+デプロイ確認**(課金経路argmin化+逆ざやガード) | CI green・テスト136本pass・margin-report実測で検出した3種の逆ざや(-882%/-135%/-157%)を根���。deploy success・health 200 | revert squash commit→push |

## 人間ゲート(要対応)
1. ~~Google Cloud Console redirect URI登録~~ → **解消(2026-09-02)**: PR#558でコード側回避(redirect_uriを登録済みchatweb.aiに固定+state運び)。Console操作不要になった。

| 2026-09-02 | **PR#558 マージ+デプロイ確認**(Google redirect_uri_mismatch修復) | 本人から実測報告「エラー400」。原因: teai.io callbackがGCP未登録+Console登録はAPI非対応。8/19の未マージ修復(3d5e05d)と同手法(chatweb.ai固定+state運び)でコード側解決。本番でGoogleが通常のログイン画面(200)を返すことを確認済み | `git revert` squash commit→push |
