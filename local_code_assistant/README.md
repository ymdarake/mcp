# Local Code Assistant

自己完結型のローカルコードアシスタントです。

内容:
- `local_code_assistant.py`: アシスタント本体の実装
- `tests/`: Python 標準の `unittest` を使った単体テスト
- `Makefile`: `make test` / `make smoke` / `make run` 等の補助ターゲット

クイックスタート:
```bash
cd local_code_assistant
make test
make smoke
```

設計ノート:
- 標準入力/標準出力で改行区切りの JSON をやり取りするプロトコルを採用しています（stdin/stdout）。
- ログは標準エラー出力（stderr）に出力します。プロトコルの JSON は stdout を使うため、ログと混ざりません。
- パスの安全性は `Path.resolve()` と `Path.is_relative_to()` を組み合わせてディレクトリトラバーサルを防いでいます。

注意事項:
- `Path.is_relative_to()` を使っているため、Python 3.9 以上を想定しています。必要であれば互換性のためのフォールバック実装を追加できます。
- 大きなファイルやバイナリを扱う場合の取り扱いについては追加の保護（サイズ上限やバイナリ検出）を検討してください。

ライセンス: MIT（必要であれば LICENSE ファイルを追加してください）

## プロジェクトへの登録方法（`claude mcp add`）

プロジェクトに対してこのアシスタントを MCP ツールとして登録するには、まず対象のプロジェクトディレクトリへ移動してから `claude mcp add` を実行します。シェルの `$(pwd)` を使うと、登録時にその時点の絶対パスがコマンドに埋め込まれるため、実行時にプロジェクトルートを固定できます。

例:

```bash
# プロジェクトのルートディレクトリへ移動する
cd /path/to/your/project

# そのディレクトリを --project に渡して登録する（登録時に $(pwd) が展開されます）
claude mcp add local-assistant -- python </path/to/>local_code_assistant.py --project $(pwd)
```

この方法で登録すると、ツールが呼ばれたときに `--project` に登録時のパスが渡され、そのプロジェクト内での操作に限定されます。

注意点:
- 登録コマンド内で `$(pwd)` を使うと、コマンド実行時のカレントディレクトリが埋め込まれます。登録後に別ディレクトリで実行したい場合は、ラッパースクリプトを用意して実行時のカレントディレクトリを渡す方法が柔軟です。
- 先にスクリプトを実行可能にしておけば（`#!/usr/bin/env python3` を先頭に追加して `chmod +x`）、`python` を明示せず直接パスだけで登録することも可能です。
