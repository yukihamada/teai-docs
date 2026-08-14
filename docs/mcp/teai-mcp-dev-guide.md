# teai.io MCPツールストア 開発者ガイド — 出品して80%受け取るまで

> 2026-08-10時点・全て実測に基づく一次情報。筆者はこの手順で5ツール(qrcode/pdftext/ogpmaker/seikyusho/shohyo)を1日で出品した。

## 北極星

**「呼べば、すぐ、確実に、正直な価格で返る」**

エージェントは説明文と価格だけを読んで道具を選ぶ。人間向けのブランディングは効かない。効くのは:
1. 説明文が正確(何を入れると何が返るか・実測レイテンシ・できないこと)
2. 確実に返る(成功率・明確なエラー)
3. 価格の根拠が自明(重いAI=高い・軽いユーティリティ=安い)

## 全体像

```
あなたのMCPサーバ(どこでもOK・公開URL必須)
   ↑ tools/list, tools/call (JSON-RPC 2.0 over HTTP POST)
teai.io ゲートウェイ  https://api.teai.io/mcp/{あなたのslug}
   ↑ teaiキー(te_/cw_)で認証・呼び出しごとにクレジット課金
利用者(AIエージェント / Claude Code / Sente ほか)
```

- 課金はteai側が行い、**売上の80%が開発者の台帳に記録される**(あなたのツールが呼ばれるたび)
- 価格は登録時に自分で決める(**上限60クレジット/回**)
- 上流エラー時・残高不足時は課金されない(誤課金なしは実測確認済み)

## 1. 最小実装(Cloudflare Workers・約100行)

必要なのはJSON-RPC 2.0のPOSTハンドラ1本。実装必須メソッド:

| メソッド | 返すもの |
|---|---|
| `initialize` | protocolVersion, capabilities, serverInfo |
| `notifications/*` | 202/204で受け流す |
| `tools/list` | ツール定義の配列(name/description/inputSchema) |
| `tools/call` | `{content: [{type:"text"|"image"|"resource", ...}]}` |

スターターテンプレート: `teai-mcp-starter/`(このガイドと同じ場所)をコピーして`wrangler deploy`するだけで動く雛形。実例3つ:
- 画像を返す: `ogpmaker/mcp-worker/src/index.js`
- PDF(バイナリresource)を返す: `seikyusho-mcp/src/index.js`
- 上流APIをラップする: `shohyo-mcp/src/index.js`

## 2. 説明文の型(これが一番効く)

```
1行目: 「◯◯を渡すと、◯◯を返します」— 具体的に
入力: 各パラメータの意味・単位・上限・既定値(例つき)
出力: 形式とサイズ感
実測レイテンシ: 「実測でおよそN秒」(必ず自分で3回測る)
できないこと: 限界を正直に(OCRしない・実データ照合しない等)
```

盛らない。「5分で」「完璧に」等の未検証の形容は書かない。エージェントは説明文の通りに動かないツールを二度と呼ばない。

## 3. 価格の決め方(実例)

| クラス | 目安 | 実例 |
|---|---|---|
| 軽量ユーティリティ(ms〜1秒) | 3〜5cr | qrcode=3cr, pdftext=5cr |
| 生成系(1〜5秒) | 10〜15cr | ogpmaker=10cr, seikyusho=15cr |
| 重いAI呼び出し(数十秒) | 30〜60cr | shohyo=50cr |

- 分配は切り上げ式 `(price×80+99)/100`。**低額ツールは開発者取り分100%になる**(3cr→3cr。teai取り分ゼロ)。3crを下回る価格設定は意味が薄い
- 上限60cr/回(第三者ツール)

## 4. 登録〜公開

```bash
# 登録(→pending。登録時に上流へtools/list実疎通が走る=先にデプロイしておく)
curl -X POST https://api.teai.io/api/v1/mcp/services \
  -H "Authorization: Bearer $TEAI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"slug":"yourtool","upstream_url":"https://yourtool.example.workers.dev","default_credits":5}'

# 自分の登録一覧・状態確認
curl https://api.teai.io/api/v1/mcp/services/mine -H "Authorization: Bearer $TEAI_API_KEY"

# 収益台帳(呼ばれるたびに credits / developer_credits が記録される)
curl https://api.teai.io/api/v1/mcp/earnings -H "Authorization: Bearer $TEAI_API_KEY"
```

- 審査(pending→live)はteai運営が行う
- slug変更・upstream変更(PUT)は再審査になる

## 5. 🪤 実測で踏んだ罠(全部一次情報)

1. **上流レスポンス5MB上限**: フォント全埋め込みPDF(4.2MB)+base64をresourceとtextに二重出力して超過した。バイナリは1回だけ出力・フォントはsubset埋め込み(4.2MB→35KBになった)
2. **slugは3文字以上**("qr"は拒否された→"qrcode")
3. **デプロイ直後20〜30秒はエッジ伝播ラグで1042/1104エラー**。5回連続200を確認してから登録に進む
4. **課金検証は残高でなく台帳で**。共有アカウントだと他プロセスの消費が混ざる。`/api/v1/mcp/earnings`が正本
5. **ゲートウェイはJSON-RPCエラー(HTTP 200内)を見て課金をスキップする**。入力バリデーションエラーはきちんとJSON-RPCエラーで返せば利用者に課金されない=信頼につながる
6. 登録APIはレート制限5回/分
7. `wrangler dev`のローカルworkerdはcompatibility_dateの未来日付を拒否することがある(本番は問題ない)
8. curlの素朴な計測はTLSハンドシェイク遅延を含む。レイテンシはハンドラ内で測るか複数回の中央値を取る

## 6. チェックリスト(出品前)

- [ ] tools/list が説明文の型に沿っている(レイテンシ実測済み・できないこと明記)
- [ ] 変な入力(空・超過・型違い)がJSON-RPCエラーで返る
- [ ] レスポンスが5MB未満
- [ ] 本番URLで5回連続200
- [ ] 登録→live後、ゲートウェイ経由で1回実呼び出しして台帳に80%が記録されることを確認
