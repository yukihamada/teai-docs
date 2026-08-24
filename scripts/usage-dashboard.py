#!/usr/bin/env python3
"""teai.io 利用ダッシュボード生成スクリプト
毎時実行(cron/launchd想定)。"直近24時間(1時間ごと)"と"直近30日(24時間ごと)"の推移グラフをHTML出力する。
"""
import json, os, sys, urllib.request, datetime, html

API_KEY = os.environ.get("TEAI_API_KEY", "")
BASE = "https://api.teai.io/api/v1"
OUT = os.path.expanduser("~/workspace/teai-usage-dashboard.html")
SNAP = os.path.expanduser("~/.teai_usage_snapshots.jsonl")


def api(path):
    req = urllib.request.Request(BASE + path, headers={"Authorization": f"Bearer {API_KEY}"})
    with urllib.request.urlopen(req, timeout=15) as r:
        return json.loads(r.read())


def fmt(n):
    return f"{n:,}"


def spark(bar_color, max_w, val, vmax):
    w = max(2, int(max_w * val / vmax)) if vmax else 2
    return f'<span class="bar" style="width:{w}px;background:{bar_color}">{val}</span>'


def main():
    if not API_KEY:
        sys.exit("TEAI_API_KEY 未設定")
    try:
        data = api("/usage")
    except Exception as e:
        sys.exit(f"API取得失敗: {e}")

    u = data["usage"]
    now = datetime.datetime.now(datetime.timezone.utc).astimezone()
    today = now.astimezone(datetime.timezone.utc).date().isoformat()

    rec = {
        "ts": now.isoformat(),
        "credits_remaining": data["credits_remaining"],
        "credits_used": data["credits_used"],
        "today_credits": u["credits_today"],
        "today_requests": u["requests_today"],
        "today_tokens": u["tokens_today"],
    }

    if os.path.exists(SNAP):
        with open(SNAP) as f:
            stmps = [json.loads(l) for l in f if l.strip()]
        stale = [s for s in stmps if s.get("today_credits") is None]
        if stale:
            print(f"note: {len(stale)} 件の旧フォーマットスナップショットをスキップ")
    else:
        stmps = []
    stmps.append(rec)
    with open(SNAP, "a") as f:
        f.write(json.dumps(rec) + "\n")
    stmps = [s for s in stmps if s.get("today_credits") is not None]

    last24 = [s for s in stmps if (now - datetime.datetime.fromisoformat(s["ts"])).total_seconds() < 28 * 3600][-25:]

    hourly_rows, hourly_chart = [], []
    deltas = []
    for i in range(1, len(last24)):
        a, b = last24[i - 1], last24[i]
        dh = int((datetime.datetime.fromisoformat(b["ts"]) - datetime.datetime.fromisoformat(a["ts"])).total_seconds() / 3600) or 1
        dc = (b["credits_used"] - a["credits_used"]) / dh
        dr = (b["today_requests"] - a["today_requests"]) / dh
        deltas.append((b["ts"], dc, dr, b["credits_remaining"]))
    vmax = max([d[1] for d in deltas] or [1])
    for ts, dc, dr, _ in deltas[-24:]:
        t = datetime.datetime.fromisoformat(ts).strftime("%m/%d %H:%M")
        hourly_rows.append(
            f"<tr><td>{t}</td><td>{fmt(int(dc))}</td>"
            f"<td>{spark('var(--accent)', 240, dc, vmax)}</td><td>{fmt(int(dr))}</td></tr>"
        )
        hourly_chart.append({"label": t, "credits": int(dc)})
    hourly_rows.reverse()

    daily_rows = []
    daily = sorted(u["daily_30d"], key=lambda d: d["date"], reverse=True)
    vmax_d = max([d["credits"] for d in daily] or [1])
    for d in daily:
        daily_rows.append(
            f"<tr><td>{d['date']}</td><td>{fmt(d['credits'])}</td>"
            f"<td>{spark('var(--accent2)', 240, d['credits'], vmax_d)}</td><td>{fmt(d['requests'])}</td></tr>"
        )

    models = sorted(u["by_model_30d"], key=lambda m: m["credits"], reverse=True)
    total_m = sum(m["credits"] for m in models) or 1
    model_rows = []
    for m in models:
        pct = m["credits"] / total_m * 100
        model_rows.append(
            f"<tr><td class='mono'>{html.escape(m['model'])}</td><td>{fmt(m['credits'])}</td>"
            f"<td>{fmt(m['input_tokens'] + m['output_tokens'])}</td><td>{fmt(m['requests'])}</td>"
            f"<td><div class='pct'><div class='fill' style='width:{pct:.1f}%'></div><span>{pct:.1f}%</span></div></td></tr>"
        )

    bal = "充足" if data["credits_remaining"] > 10000 else "残少注意"
    bal_cls = "ok" if data["credits_remaining"] > 10000 else "warn"

    hourly_json = json.dumps(hourly_chart, ensure_ascii=False)
    daily_json = json.dumps([{"label": d["date"], "credits": d["credits"], "requests": d["requests"]} for d in sorted(u["daily_30d"], key=lambda d: d["date"])], ensure_ascii=False)

    tpl = """<!DOCTYPE html>
<html lang="ja">
<head>
<meta charset="UTF-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="refresh" content="3600">
<title>teai.io 利用ダッシュボード</title>
<style>
:root{--bg:#0a0a0a;--surface:#141414;--border:#1e1e1e;--text:#e5e5e5;--muted:#888;--accent:#10b981;--accent2:#34d399;--warn:#f59e0b}
*{margin:0;padding:0;box-sizing:border-box}
body{font-family:-apple-system,BlinkMacSystemFont,'Hiragino Sans','Noto Sans JP',monospace;background:var(--bg);color:var(--text);padding:32px 24px;max-width:1100px;margin:0 auto}
h1{font-size:22px;font-weight:800}h1 span{color:var(--accent)}
header{display:flex;justify-content:space-between;align-items:baseline;margin-bottom:24px}
.meta{color:var(--muted);font-size:12px}
.cards{display:grid;grid-template-columns:repeat(auto-fit,minmax(160px,1fr));gap:12px;margin-bottom:28px}
.card{background:var(--surface);border:1px solid var(--border);border-radius:10px;padding:14px}
.card .label{font-size:11px;color:var(--muted);text-transform:uppercase;letter-spacing:.5px}
.card .value{font-size:22px;font-weight:800;margin-top:4px;font-variant-numeric:tabular-nums}
.card .value.ok{color:var(--accent)}.card .value.warn{color:var(--warn)}
section{margin-bottom:32px}
h2{font-size:15px;margin-bottom:12px;color:var(--accent);letter-spacing:.3px}
canvas{width:100%;background:var(--surface);border:1px solid var(--border);border-radius:10px;margin-bottom:12px}
table{width:100%;border-collapse:collapse;font-size:13px;background:var(--surface);border:1px solid var(--border);border-radius:10px;overflow:hidden}
th,td{padding:8px 12px;text-align:left;font-variant-numeric:tabular-nums}
th{background:#0f1a16;color:var(--muted);font-weight:600;font-size:11px;text-transform:uppercase}
tr+tr td{border-top:1px solid var(--border)}
td:nth-child(2){text-align:right}
.bar{display:block;height:14px;border-radius:3px;color:transparent}
.pct{position:relative;background:#0f1a16;height:16px;border-radius:4px;min-width:120px}
.pct .fill{position:absolute;left:0;top:0;bottom:0;background:var(--accent);border-radius:4px}
.pct span{position:relative;font-size:11px;color:#fff;padding-left:6px;line-height:16px}
.mono{font-family:ui-monospace,Menlo,monospace;font-size:12px}
footer{color:var(--muted);font-size:11px;text-align:center;margin-top:40px}
</style>
<script src="https://cdn.jsdelivr.net/npm/chart.js@4"></script>
</head>
<body>
<header>
  <h1><span>te</span>ai.io 利用ダッシュボード</h1>
  <div class="meta">最終更新: __NOW__ (自動リロード=1h)</div>
</header>
<div class="cards">
  <div class="card"><div class="label">プラン</div><div class="value">__PLAN__</div></div>
  <div class="card"><div class="label">残クレジット</div><div class="value __BALCLS__">__REMAIN__</div></div>
  <div class="card"><div class="label">累計使用クレジット</div><div class="value">__USED__</div></div>
  <div class="card"><div class="label">今日のクレジット</div><div class="value">__TODAY_C__</div></div>
  <div class="card"><div class="label">今日のリクエスト</div><div class="value">__TODAY_R__</div></div>
  <div class="card"><div class="label">30日リクエスト</div><div class="value">__R30__</div></div>
  <div class="card"><div class="label">残高状態</div><div class="value __BALCLS__">__BAL__</div></div>
</div>

<section>
  <h2>⏱ 直近24時間（1時間ごとの推移）</h2>
  <canvas id="hourly" height="110"></canvas>
  <table><thead><tr><th>時刻</th><th>クレジット/時</th><th>推移</th><th>リクエスト/時</th></tr></thead>
  <tbody>__HOURLY__</tbody></table>
</section>

<section>
  <h2>📅 直近30日（24時間ごとの推移）</h2>
  <canvas id="daily" height="110"></canvas>
  <table><thead><tr><th>日付</th><th>クレジット</th><th>推移</th><th>リクエスト</th></tr></thead>
  <tbody>__DAILY__</tbody></table>
</section>

<section>
  <h2>🧠 モデル別（30日・クレジット上位）</h2>
  <table><thead><tr><th>モデル</th><th>クレジット</th><th>トークン</th><th>リクエスト</th><th>シェア</th></tr></thead>
  <tbody>__MODELS__</tbody></table>
</section>
<footer>teai.io API usage dashboard — data: api.teai.io/api/v1/usage</footer>
<script>
const hd = __HOURLY_JSON__;
new Chart(document.getElementById('hourly'), {type:'line',
 data:{labels:hd.map(x=>x.label),datasets:[{label:'クレジット/時',data:hd.map(x=>x.credits),borderColor:'#10b981',backgroundColor:'#10b98130',fill:true,tension:.3,pointRadius:2}]},
 options:{plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#888',maxTicksLimit:12},grid:{color:'#1e1e1e'}},y:{ticks:{color:'#888'},grid:{color:'#1e1e1e'}}}}});
const dd = __DAILY_JSON__;
new Chart(document.getElementById('daily'), {type:'bar',
 data:{labels:dd.map(x=>x.label),datasets:[{label:'クレジット/日',data:dd.map(x=>x.credits),backgroundColor:'#34d399'}]},
 options:{plugins:{legend:{display:false}},scales:{x:{ticks:{color:'#888',maxTicksLimit:15},grid:{color:'#1e1e1e'}},y:{ticks:{color:'#888'},grid:{color:'#1e1e1e'}}}}});
</script>
</body></html>"""

    replacements = {
        "__NOW__": now.strftime("%Y-%m-%d %H:%M:%S %Z").replace("JST", "").strip() or now.strftime("%Y-%m-%d %H:%M"),
        "__PLAN__": html.escape(str(data.get("plan", "—"))),
        "__REMAIN__": fmt(data["credits_remaining"]),
        "__USED__": fmt(data["credits_used"]),
        "__TODAY_C__": fmt(u["credits_today"]),
        "__TODAY_R__": fmt(u["requests_today"]),
        "__R30__": fmt(u["requests_30d"]),
        "__BAL__": bal,
        "__BALCLS__": bal_cls,
        "__HOURLY__": "\n".join(hourly_rows),
        "__DAILY__": "\n".join(daily_rows),
        "__MODELS__": "\n".join(model_rows),
        "__HOURLY_JSON__": hourly_json,
        "__DAILY_JSON__": daily_json,
    }
    for k, v in replacements.items():
        tpl = tpl.replace(k, v)

    with open(OUT, "w") as f:
        f.write(tpl)
    print(f"✅ 更新: {OUT} ({now.strftime('%H:%M')}) — 残クレジット {fmt(data['credits_remaining'])}")


if __name__ == "__main__":
    main()
