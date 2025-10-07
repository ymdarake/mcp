# mcp

主要なディレクトリ構成

- `mcp_local_assistant/` — パッケージ化したアシスタント本体
  - `local_code_assistant.py` — アシスタント本体（stdin/stdout で JSON をやり取り）
  - `tests/` — 単体テスト（Python `unittest`）
  - `Makefile` — `make test`, `make smoke`, `make run` などの補助ターゲット
  - `README.md` — パッケージ内の詳細説明（日本語）

- `local_code_assistant.py`（ルート） — 作業中に使ったスクリプト（旧ファイル、参照用）
- `tests/`（ルート） — ルート向けテスト（存在する場合があります）
- `Makefile`（ルート） — ルートで使える補助コマンド（`make test` など）

## Claude / MCP への登録（プロジェクトに紐づける方法）

プロジェクトに対してこのアシスタントを MCP ツールとして登録する場合、対象プロジェクトのルートでコマンドを実行すると、そのプロジェクト向けに `--project` を固定して登録できます。例:

```bash
# まずプロジェクトのルートへ移動
cd /path/to/your/project

# 推奨: Python を明示して登録する（移植性が高い）
claude mcp add local-assistant -- python /absolute/path/to/repo/local_code_assistant/local_code_assistant.py --project "$(pwd)"
```

例（実行可能化後の登録）:

```bash
SCRIPT_PATH=/absolute/path/to/repo/local_code_assistant/local_code_assistant.py
chmod +x "$SCRIPT_PATH"
cd /path/to/your/project
claude mcp add local-assistant -- "$SCRIPT_PATH" --project "$(pwd)"

注意:
- `python /path/to/script.py` は Windows を含む幅広い環境で確実に動きます。
- 実行可能化して直接登録する方法は短くて便利ですが、shebang と実行ビットに依存します（主に macOS/Linux 向け）。
- `$(pwd)` は登録コマンドを実行したシェルで展開され、登録時にその絶対パスがコマンドに埋め込まれます。登録後はそのプロジェクトに固定される点に注意してください。
```
