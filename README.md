# meta/mcp — Local Code Assistant コレクション

このリポジトリは、ローカルで動作する自己完結型の「Local Code Assistant」を含むサンプル／まとめリポジトリです。MCP（Claude のツール）コレクションに組み込んで使えるように整理しています。

主要なディレクトリ構成

- `mcp_local_assistant/` — パッケージ化したアシスタント本体
  - `local_code_assistant.py` — アシスタント本体（stdin/stdout で JSON をやり取り）
  - `tests/` — 単体テスト（Python `unittest`）
  - `Makefile` — `make test`, `make smoke`, `make run` などの補助ターゲット
  - `README.md` — パッケージ内の詳細説明（日本語）

- `local_code_assistant.py`（ルート） — 作業中に使ったスクリプト（旧ファイル、参照用）
- `tests/`（ルート） — ルート向けテスト（存在する場合があります）
- `Makefile`（ルート） — ルートで使える補助コマンド（`make test` など）

クイックスタート

1. リポジトリのルートでテストを実行する（ルート Makefile がある場合）:

```bash
make test
```

2. パッケージ単位でテストやスモークテストを実行するには:

```bash
cd mcp_local_assistant
make test
make smoke
```

Claude / MCP への登録（プロジェクトに紐づける方法）

プロジェクトに対してこのアシスタントを MCP ツールとして登録する場合、対象プロジェクトのルートでコマンドを実行すると、そのプロジェクト向けに `--project` を固定して登録できます。例:

```bash
# まずプロジェクトのルートへ移動
cd /path/to/your/project

# そのディレクトリを --project に渡して登録する
claude mcp add local-assistant -- python /Users/ymdarake/workspace/meta/mcp/mcp_local_assistant/local_code_assistant.py --project $(pwd)
```

このように登録すれば、実行時に `--project` に登録時の絶対パスが渡され、ツールはそのプロジェクトのみを操作します。

注意:

- `$(pwd)` はシェルで展開されるため、登録を行ったディレクトリの絶対パスがコマンドに埋め込まれます。別のディレクトリで実行したい場合や動的にプロジェクトを切り替えたい場合は、ラッパースクリプトを用意して `os.getcwd()` を渡す方式が柔軟です。
- スクリプトを直接実行可能にしたい場合は、`local_code_assistant.py` の先頭に `#!/usr/bin/env python3` を追加して `chmod +x` を実行してください。すると `python` を明示せずにパスだけで登録できます。

例（実行可能化後の登録）:

```bash
chmod +x /Users/ymdarake/workspace/meta/mcp/mcp_local_assistant/local_code_assistant.py
cd /path/to/your/project
claude mcp add local-assistant -- /Users/ymdarake/workspace/meta/mcp/mcp_local_assistant/local_code_assistant.py --project $(pwd)
```

README とドキュメント

- パッケージ固有の使い方や MCP との連携例は `mcp_local_assistant/README.md` を参照してください。Claude（MCP）向けの JSON コマンド例や Python サブプロセスのサンプルを載せています。

次にやること（提案）

- ラッパースクリプトを追加して、登録時に固定パスを書き込まずにどのプロジェクトでも動かせるようにする
- Git リポジトリの整備（LICENSE、.gitignore、初回コミット）を行う
- CI (GitHub Actions) を追加して `make test` を自動化する

必要な作業があれば教えてください。どれを優先しますか？
