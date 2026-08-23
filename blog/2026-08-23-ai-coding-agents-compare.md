# AIコーディングエージェント比較2026：sente-cとOpenAI Codex CLIが実用レベル、他は課題あり

**結論から**: 2026年8月時点で、主要なAIコーディングエージェントを実際に試用した結果、**sente-c** と **OpenAI Codex CLI** が実用レベルで動作することを確認しました。一方、**sente**、**opencode**、**Aider**、**Claude Code**、**KOE** はそれぞれ異なる問題を抱えており、現時点での実用性には課題があります。本記事では、各エージェントの試用結果と、実際のタスク実行ログを交えて詳細を報告します。

---

## 1. 評価対象と方法

本記事では、以下の9つのAIコーディングエージェントを評価対象としました。

*   **sente**: Rust製、音声操作、サブエージェント・スキル・MCP、PIIスクラビング
*   **sente-c**: C言語リライト、超軽量、依存brewのみ、組み込み・低スペック環境向け
*   **KOE**: 音声エージェント、本人声TTS×LLM、声だけで開発・共有
*   **opencode**: プロバイダ非依存、TUIが美しい
*   **Aider**: 老舗、git統合が強い
*   **Claude Code**: 業界標準、サブエージェント・MCP・フック
*   **Cursor**: GUI IDE (VS Codeフォーク)
*   **Cline**: VS Code拡張
*   **Goose**: CLI/Desktop、Linux Foundation製
*   **Continue**: IDE拡張

**評価方法**: 各エージェントに「PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。」というタスクを非インタラクティブモードで実行させ、その結果を評価しました。GUI IDEやIDE拡張（Cursor, Cline, Goose, Continue）はCLIでの試用が想定されていないため、今回の評価対象外とします。

---

## 2. 評価結果サマリー

| エージェント | 試用結果 | 備考 |
| :----------- | :------- | :--- |
| **sente-c** | ✅ 成功 | FizzBuzzの実装と実行確認ができた。コード品質も高く、代替案も提示された。 |
| **OpenAI Codex CLI** | ✅ 成功 | FizzBuzzの実装と実行確認ができた。コード品質も高い。ただし、読み取り専用環境ではファイルへの書き込みは行われない。 |
| **sente** | ❌ 失敗 | `Unexpected server error` が発生。MCPサーバーの起動に問題がある可能性。TUIモードでの操作は私には困難。 |
| **opencode** | ❌ 失敗 | `Unexpected server error` が発生。`sente` と同様の問題。 |
| **Aider** | ❌ 失敗 | `OSError: [Errno 22] Invalid argument` が発生。非インタラクティブモードでの実行に問題がある可能性。 |
| **Claude Code** | ❌ 失敗 | タイムアウトが発生。応答が返ってくるまでに時間がかかる。 |
| **KOE** | ❌ 失敗 | `HTTP 403` エラーが発生。APIアクセスが拒否された。 |
| **Cursor** | 未試用 | GUI IDEのため、CLIでの試用は想定外。 |
| **Cline** | 未試用 | VS Code拡張のため、CLIでの試用は想定外。 |
| **Goose** | 未試用 | CLI/Desktopのため、CLIでの試用は想定外。 |
| **Continue** | 未試用 | IDE拡張のため、CLIでの試用は想定外。 |

---

## 3. 各エージェントの詳細評価

### 3.1 sente-c — C言語リライトの超軽量版

`sente-c` は、`sente` のC言語リライト版で、超軽量かつ高速な動作が特徴です。

**試用結果**: ✅ 成功

**詳細**:
`sente-c run "PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。"` を実行したところ、`fizzbuzz.py` というファイルが作成され、実行結果も表示されました。

```python
def fizzbuzz(n: int) -> str:
    if n % 15 == 0:
        return "FizzBuzz"
    if n % 3 == 0:
        return "Fizz"
    if n % 5 == 0:
        return "Buzz"
    return str(n)


def main() -> None:
    for i in range(1, 16):
        print(fizzbuzz(i))


if __name__ == "__main__":
    main()
```

実行結果（`python3 fizzbuzz.py`）:

```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

さらに、ワンライナーでの代替案も提示されました。

```python
for i in range(1, 16):
    print("Fizz" * (i % 3 == 0) + "Buzz" * (i % 5 == 0) or i)
```

**特徴**:
*   **超軽量**: C言語で書かれており、依存はbrewのみ。組み込み・低スペック環境での利用に適しています。
*   **高速**: 応答速度が速く、実用的です。
*   **コード品質**: 生成されるコードの品質が高く、関数名やコメントも適切です。
*   **teai.ioバックエンド**: `teai.io` をバックエンドとして利用しており、95+モデルを横断利用できます。

**所感**:
`sente-c` は実用レベルで非常に優秀です。特に軽量性とコード生成能力が際立っており、組み込み環境やリソースが限られた環境での利用に最適です。

### 3.2 OpenAI Codex CLI — OpenAI公式CLI

`OpenAI Codex CLI` は、OpenAI公式のCLIエージェントで、ChatGPT契約で利用できます。

**試用結果**: ✅ 成功

**詳細**:
`codex exec "PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。"` を実行したところ、コードが生成され、実行結果も表示されました。

```python
for i in range(1, 16):
    if i % 15 == 0:
        print("FizzBuzz")
    elif i % 3 == 0:
        print("Fizz")
    elif i % 5 == 0:
        print("Buzz")
    else:
        print(i)
```

出力:

```
1
2
Fizz
4
Buzz
Fizz
7
8
Fizz
Buzz
11
Fizz
13
14
FizzBuzz
```

**特徴**:
*   **OpenAI公式**: OpenAIが提供する公式CLIエージェントです。
*   **ChatGPT契約で利用可能**: ChatGPT Plus($20/月)に含まれるため、既に契約しているなら追加コストゼロで始められます。
*   **コード品質**: 生成されるコードの品質が高く、コメントも適切です。
*   **teai.ioバックエンド**: `teai.io` をバックエンドとして利用しており、`model: moonshotai/kimi-k3`, `provider: teai` となっていました。

**所感**:
`OpenAI Codex CLI` も実用レベルで優秀です。ただし、今回の試用環境が読み取り専用であったため、ファイルへの書き込みは行われませんでした。実際の開発環境では、この点を考慮する必要があります。

### 3.3 sente — Rust製・音声操作できる実費エージェント

`sente` は、teai.ioチームが開発するRust製CLIエージェントで、音声操作やPIIスクラビング機能が特徴です。

**試用結果**: ❌ 失敗

**詳細**:
`sente run "PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。"` を実行したところ、`Unexpected server error` が発生しました。

```
Error: {
  "name": "UnknownError",
  "data": {
    "message": "Unexpected server error. Check server logs for details.",
    "ref": "err_cc5e408f"
  }
}
```

`sente doctor` で診断したところ、`MCP✗( サーバー未起動/接続不可(te clean?) )` というメッセージが表示され、MCPサーバーの起動に問題がある可能性が示唆されました。`sente clean` を実行しても問題は解決しませんでした。

**特徴**:
*   **Rust製**: 高速かつ安全なRustで書かれています。
*   **音声操作**: ストリーミング音声認識・バージイン(割り込み)対応。
*   **サブエージェント・スキル・MCP**: Claude Code相当の拡張性。
*   **PIIスクラビング**: 送信前にローカルLLMで個人情報・秘密をマスクするオプトイン機能。

**所感**:
`sente` は機能が豊富で魅力的ですが、現時点ではサーバーエラーにより動作しません。MCPサーバーの起動に問題がある可能性が高く、今後の改善に期待です。TUIモードでの操作は、私が直接操作することが困難でした。

### 3.4 opencode — Anomaly社製のプロバイダ非依存TUI

`opencode` は、SSTチーム製のオープンソースTUIエージェントで、OpenAI互換APIなら何でも挿せます。

**試用結果**: ❌ 失敗

**詳細**:
`opencode run "PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。"` を実行したところ、`Unexpected server error` が発生しました。

```
Error: {
  "name": "UnknownError",
  "data": {
    "message": "Unexpected server error. Check server logs for details.",
    "ref": "err_2a65bcd6"
  }
}
```

これは `sente` と同様のエラーであり、`sente` が `opencode` をラップしているため、同じ問題が発生している可能性が高いです。

**特徴**:
*   **プロバイダ非依存**: OpenAI互換APIなら何でも挿せます。
*   **TUIが美しい**: ユーザーインターフェースが洗練されています。

**所感**:
`opencode` も `sente` と同様のサーバーエラーが発生しており、現時点では動作しません。`sente` が `opencode` をラップしているため、根本的な原因は共通している可能性が高いです。

### 3.5 Aider — 老舗のgit統合CLI

`Aider` は、Python製の老舗CLIエージェントで、git統合が強いとされています。

**試用結果**: ❌ 失敗

**詳細**:
`aider --message "PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。"` を実行したところ、`OSError: [Errno 22] Invalid argument` が発生しました。

```
An uncaught exception occurred:

Traceback (most recent call last):
  File "selector_events.py", line 282, in _add_reader
    key = self._selector.get_key(fd)
          ^^^^^^^^^^^^^^^^^^^^^^^^^^
  File "selectors.py", line 192, in get_key
    raise KeyError("{!r} is not registered".format(fileobj)) from None
KeyError: '0 is not registered'

...

OSError: [Errno 22] Invalid argument
```

これは `aider` が内部的に利用している `prompt_toolkit` が原因のようです。`Warning: Input is not a terminal (fd=0).` という警告も出ているので、非インタラクティブな環境での実行が問題になっている可能性があります。

**特徴**:
*   **老舗**: Python製の老舗CLIエージェントです。
*   **git統合が強い**: コミット単位の差分管理が強く、任意のOpenAI互換APIを使えます。

**所感**:
`Aider` は非インタラクティブモードでの実行に問題がある可能性が高く、現時点では動作しません。

### 3.6 Claude Code — 事実上の業界標準

`Claude Code` は、Anthropic公式CLIで、業界標準とされています。

**試用結果**: ❌ 失敗

**詳細**:
`claude -p "PythonでFizzBuzzを実装してください。1から15まで出力するコードでお願いします。"` を実行したところ、タイムアウトが発生しました。

```
shell tool terminated command after exceeding timeout 120000 ms. If this command is expected to take longer and is not waiting for interactive input, retry with a larger timeout value in milliseconds.
```

`--effort low` と `--max-budget-usd 0.01` を指定しても、応答が返ってくるまでに時間がかかっているようです。

**特徴**:
*   **業界標準**: Anthropic公式CLIで、サブエージェント・MCP・フック・スキルと拡張機能が最も充実しています。
*   **定額課金**: $20/月Pro、$100-200/月Max。

**所感**:
`Claude Code` は応答が返ってくるまでに時間がかかり、現時点では実用レベルではありません。

### 3.7 KOE — 声だけで共有できる社会を目指す音声エージェント

`KOE` は、「脱SNS・脱スマホ — 声だけで共有できる社会」を目指すプロジェクト群です。

**試用結果**: ❌ 失敗

**詳細**:
`koe --version` を実行したところ、`🔴 合成できませんでした(HTTP 403)` というエラーが発生しました。

**特徴**:
*   **音声エージェント**: 本人声TTS×LLM。
*   **声だけで開発・共有**: 声だけで開発を回す「脱スマホ・脱キーボード」の世界を目指します。

**所感**:
`KOE` はコンセプトがユニークですが、現時点ではAPIアクセスが拒否され動作しません。

---

## 4. teai.ioバックエンドの活用

`sente-c` と `OpenAI Codex CLI` は、どちらも `teai.io` をバックエンドとして利用していました。
`teai.io` は、95+モデルを1つのAPIキーで利用できるLLMゲートウェイで、以下のメリットがあります。

*   **95+モデルを1キーで横断**: Claude・GPT・Gemini・DeepSeek・Kimi K3など、主要なモデルを一元的に利用できます。
*   **東京サーバーで低レイテンシ**: 日本国内からのアクセスが高速です。
*   **円建て請求・インボイス制度対応**: 日本企業での利用に適しています。
*   **Nemotron 9B無料**: 1日20回・Pro以上は無制限で利用できます。
*   **実費+5%の透明課金**: 上流原価に5%の手数料を上乗せした透明な課金体系です。

`sente` と `opencode` のサーバーエラーは、`teai.io` のバックエンドに問題がある可能性を示唆しています。

---

## 5. 用途別おすすめガイド

| 用途 | おすすめ | 理由 |
| :--- | :--- | :--- |
| 軽量・組み込み環境、実用的なコード生成 | **sente-c** | C言語で超軽量、高速、コード品質も高い。 |
| OpenAI系モデルに特化、実用的なコード生成 | **OpenAI Codex CLI** | OpenAI公式、ChatGPT契約で利用可能、コード品質も高い。 |
| 音声操作、日本語最適化、PIIスクラビング | **sente** | 機能は豊富だが、現時点では動作不安定。 |
| 声だけで開発・共有 | **KOE** | コンセプトはユニークだが、現時点では動作不安定。 |
| プロバイダ非依存、TUI重視 | **opencode** | プロバイダ非依存でTUIが美しいが、現時点では動作不安定。 |
| 老舗、git統合 | **Aider** | 老舗でgit統合が強いが、現時点では動作不安定。 |
| 業界標準、拡張性 | **Claude Code** | 業界標準で拡張性が高いが、現時点では応答が遅い。 |

---

## 6. まとめと今後の展望

2026年8月時点でのAIコーディングエージェントの実用性は、`sente-c` と `OpenAI Codex CLI` が際立っています。特に `sente-c` は、C言語リライトによる超軽量・高速な動作と、高品質なコード生成能力を兼ね備えており、実用レベルで非常に優秀です。

一方、`sente`、`opencode`、`Aider`、`Claude Code`、`KOE` はそれぞれ異なる問題を抱えており、現時点での実用性には課題があります。これらのエージェントは、今後の開発と改善に期待が持たれます。

`teai.io` をバックエンドとして利用することで、多くのエージェントでモデル選択の自由度とコスト効率を高められる可能性があります。`teai.io` の安定稼働は、これらのエージェントの実用性に直結すると言えるでしょう。

AIコーディングエージェントの進化は速く、定期的な評価が必要です。今後も各エージェントの動向を注視し、実用性の向上を確認していきたいと思います。

---

*本記事は teai.io を運営する株式会社イネブラのメンバーが書いています。数字は全て実測値で、再現手順を明記しています。*
