# teai MCP tool starter

コピーして5分で出品できる雛形。詳細ガイド: https://teai.io/blog/mcp-dev-guide (EN: https://teai.io/blog/mcp-dev-guide-en) / 登録ページ: https://teai.io/mcp-developers

最初の数人には実装から出品まで直接伴走します。詰まったら焚き火( https://takibi.wtf )か team@teai.io へ。

```bash
git clone --depth 1 https://github.com/yukihamada/teai-docs && cp -r teai-docs/mcp-starter my-tool && cd my-tool
# 1. wrangler.toml の name と src/index.js の TOOLS/handleToolCall を書き換える
# 2. ローカル確認(グローバルwrangler推奨・npxはハングすることがある)
wrangler dev   # 別ターミナルで: curl localhost:8787 -d '{"jsonrpc":"2.0","id":1,"method":"tools/list"}'
# 3. デプロイ(20〜30秒待ってから5回連続200を確認)
wrangler deploy
# 4. ストア登録(→pending→運営がliveに)
curl -X POST https://api.teai.io/api/v1/mcp/services \
  -H "Authorization: Bearer $TEAI_API_KEY" -H 'Content-Type: application/json' \
  -d '{"slug":"mytool","upstream_url":"https://my-mcp-tool.<you>.workers.dev","default_credits":5}'
# 5. 収益確認
curl https://api.teai.io/api/v1/mcp/earnings -H "Authorization: Bearer $TEAI_API_KEY"
```

チェックリストと罠(5MB上限・slug3文字以上・課金検証は台帳で等)はガイド本文へ。
