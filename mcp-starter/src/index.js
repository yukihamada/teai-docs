/**
 * teai.io MCPツールストア スターター
 * これをコピーして tools/list の定義と handleToolCall() を書き換えるだけで出品できる。
 * 実装例: 文字数カウントツール(count_chars)
 */

const SERVER_INFO = { name: "my-mcp-tool", version: "1.0.0" };

const TOOLS = [
  {
    name: "count_chars",
    // 説明文の型: 1行目=何を入れると何が返るか / 入力の単位・上限 / 出力 / 実測レイテンシ / できないこと
    description:
      "テキストを渡すと、文字数・単語数・行数をJSONで返します。\n" +
      "入力: text(必須・100,000文字まで)。\n" +
      "出力: {chars, words, lines}。\n" +
      "実測レイテンシ: 0.1秒未満。\n" +
      "できないこと: 形態素解析はしません(単語数は空白区切りの概算)。",
    inputSchema: {
      type: "object",
      properties: {
        text: { type: "string", description: "数える対象のテキスト。最大100,000文字。", maxLength: 100000 },
      },
      required: ["text"],
    },
  },
];

function handleToolCall(name, args) {
  if (name === "count_chars") {
    const text = args?.text;
    if (typeof text !== "string" || text.length === 0) {
      throw rpcError(-32602, "text は必須です(空でない文字列)");
    }
    if (text.length > 100000) throw rpcError(-32602, "text は100,000文字までです");
    const result = {
      chars: [...text].length,
      words: text.trim().split(/\s+/).filter(Boolean).length,
      lines: text.split("\n").length,
    };
    return { content: [{ type: "text", text: JSON.stringify(result) }] };
  }
  throw rpcError(-32601, `unknown tool: ${name}`);
}

// ---- 以下はそのまま使えるJSON-RPC 2.0ボイラープレート ----

function rpcError(code, message) {
  const e = new Error(message);
  e.rpc = { code, message };
  return e;
}

function json(obj, status = 200) {
  return new Response(JSON.stringify(obj), {
    status,
    headers: { "content-type": "application/json" },
  });
}

export default {
  async fetch(request) {
    if (request.method !== "POST") {
      return json({ ok: true, hint: "MCP endpoint. POST JSON-RPC 2.0." });
    }
    let req;
    try {
      req = await request.json();
    } catch {
      return json({ jsonrpc: "2.0", id: null, error: { code: -32700, message: "parse error" } });
    }
    const { id, method, params } = req ?? {};

    // 通知は受け流す(202)
    if (typeof method === "string" && method.startsWith("notifications/")) {
      return new Response(null, { status: 202 });
    }

    try {
      if (method === "initialize") {
        return json({
          jsonrpc: "2.0", id,
          result: {
            protocolVersion: params?.protocolVersion ?? "2025-06-18",
            capabilities: { tools: {} },
            serverInfo: SERVER_INFO,
          },
        });
      }
      if (method === "tools/list") {
        return json({ jsonrpc: "2.0", id, result: { tools: TOOLS } });
      }
      if (method === "tools/call") {
        const result = handleToolCall(params?.name, params?.arguments ?? {});
        return json({ jsonrpc: "2.0", id, result });
      }
      return json({ jsonrpc: "2.0", id, error: { code: -32601, message: `unknown method: ${method}` } });
    } catch (e) {
      const rpc = e.rpc ?? { code: -32000, message: String(e?.message ?? e) };
      return json({ jsonrpc: "2.0", id, error: rpc });
    }
  },
};
