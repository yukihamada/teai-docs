# Claude Codeの向き先を1行変えるだけで、1タスク0.03円で回せた話【teai.io】

**結論**: Claude Code の `ANTHROPIC_BASE_URL` を `https://api.teai.io/v1` に変えるだけで、Kimi K3・DeepSeek V4 Pro・GLM 5.2 などが Claude Code としてそのまま動き、日々のコーディングタスクが **1タスクあたり 0.03円〜1円** で回りました。機械採点つきの実測ログを公開します。

---

## 背景: Claude Code、便利だけど課金が気になる

Claude Code は強力ですが、Sonnet/Opus をガンガン回すとコストが積み上がります。かといって「安いモデルに変えたら品質が落ちるのでは?」という不安もある。

そこで **[teai.io](https://teai.io)**（日本発のLLMゲートウェイ、Anthropic Messages API互換）に向き先を変えて、**「このタスクなら、このモデルで、この値段」** を機械採点で検証しました。

## やり方（3分）

```bash
export ANTHROPIC_BASE_URL=https://api.teai.io/v1
export ANTHROPIC_AUTH_TOKEN=te_xxxxxxxx   # teai.io/keys で無料発行
export ANTHROPIC_MODEL=deepseek/deepseek-v4-pro   # 使いたいモデルを指定
claude   # いつも通り起動するだけ
```

OpenAI 互換エンドポイント（`/v1/chat/completions`）もあるので、OpenCode や素の Python スクリプトからも `base_url` を1行変えるだけで使えます。

## 実測: コーディングタスクの最安合格ライン

### ① Claude Code 互換 — Python 営業日計算関数（機械採点7ケース）

| モデル | 結果 | 所要時間 | コスト |
|---|---|---|---|
| deepseek/deepseek-v4-pro | ✅ 全PASS | — | **$0.00023（≈0.03円）** |
| claude-haiku-4-5 | ✅ PASS | 2.1s | $0.00144（0.22円） |
| claude-sonnet-5 | ✅ PASS | 5.8s | $0.00721（1.08円） |

### ② 1画面HTML生成（「今夜なに食べる?」UI）

最安の合格ラインは `google/gemma-3-27b-it` で **$0.00021（≈0.03円）**。

### 月間コストの試算（1日100タスクの場合）

| 振り分け | 1タスク | 1日 | 月 |
|---|---|---|---|
| 全部 Sonnet 5 | 1.08円 | 108円 | 約2,160円 |
| 全部 Kimi K3 | 0.48円 | 48円 | 約960円 |
| 簡単なのは DeepSeek V4 Pro に振り分け | 0.03〜0.11円 | 3〜11円 | **約70〜220円** |

難しい設計・根深いバグだけ上位モデル、日常は合格実績のある安いモデル——という**振り分けが base_url 1行でできる**のが実利です。teai.io は2026-07-31に「**上流実費+5%**」へ全面改定されたので、安いモデルを選ぶ判断がそのまま原価に効きます。

## まずは無料で30秒: te CLI（登録不要のゲストモード）

いきなりAPIキー発行はハードルが高い方向けに、**登録不要でその場で試せるCLI** もあります。

```bash
curl -fsSL https://teai.io/te | sh
te run "このディレクトリのREADMEを書いて"
```

APIキーなしで起動すると自動でゲストモード（無料モデル・レート制限あり）になり、気に入ったら `te login` で全95+モデルに切り替わります。

## 注意点

- 失敗した4モデル（grok-4.5, fable-5, sonnet-5, gpt-5.6-sol のHTML生成）は上流の502エラーであり、モデルの能力差ではありません
- 価格は2026-08-01時点の実測。最新は [teai.io のモデル一覧](https://teai.io/#models) を確認してください
- ゲストモードは無料モデル（Nemotron）固定・1日の回数制限あり。本格利用は無料キー発行がおすすめです

## まとめ

- Claude Code の向き先を `https://api.teai.io/v1` に変えるだけで、95+モデルがそのまま使える
- 機械採点で「このタスクはこのモデルで十分」を決めれば、**月のコストを1/10以下**にできる
- まずは `curl -fsSL https://teai.io/te | sh` で登録不要のお試しが可能

計測スクリプトと全ログは公開してあるので、`TEAI_API_KEY` を入れれば同じ実験がそのまま再現できます。

---

*本記事は teai.io を運営する株式会社イネブラのメンバーが書いています。数字は全て実測値で、再現手順を明記しています。*
