import os
import sys
import json
import argparse
import logging
from pathlib import Path

# --- ロギング設定 ---
# 標準エラー出力にログを出力することで、MCPの通信（標準入出力）と分離する
logging.basicConfig(level=logging.INFO, stream=sys.stderr, format='[%(levelname)s] %(message)s')

class LocalCodeAssistant:
    """
    ローカルファイルシステムを安全に操作するための自己完結型アシスタント。
    外部依存関係やネットワーク通信を一切行わない設計。
    """
    def __init__(self, project_root):
        self.project_root = Path(project_root).resolve()
        logging.info(f"プロジェクトルートを '{self.project_root}' に設定しました。")
        if not self.project_root.is_dir():
            logging.error(f"指定されたプロジェクトルート '{self.project_root}' が存在しないか、ディレクトリではありません。")
            raise ValueError("Invalid project root")

    def _is_safe_path(self, target_path):
        """
        指定されたパスがプロジェクトルート内にあり、安全であることを確認する。
        ディレクトリトラバーサル攻撃を防ぐ。
        """
        resolved_path = Path(self.project_root / target_path).resolve()
        is_safe = resolved_path.is_relative_to(self.project_root)
        if not is_safe:
            logging.warning(f"セキュリティ警告: パス '{target_path}' はプロジェクトルート外へのアクセスを試みました。")
        return is_safe

    def list_files(self, directory="."):
        """
        指定されたディレクトリ内のファイルとディレクトリを再帰的にリストアップする。
       .gitや__pycache__などの一般的な不要ファイルは除外する。
        """
        target_dir = Path(self.project_root / directory)
        if not self._is_safe_path(directory) or not target_dir.is_dir():
            return {"status": "error", "message": f"無効なディレクトリです: {directory}"}

        excluded_dirs = {'.git', '__pycache__', 'node_modules', '.venv', '.idea', '.vscode'}
        excluded_files = {'.DS_Store'}
        
        file_list = []
        for root, dirs, files in os.walk(target_dir):
            # 除外ディレクトリを探索対象から外す
            dirs[:] = [d for d in dirs if d not in excluded_dirs]
            
            for name in files:
                if name not in excluded_files:
                    relative_path = Path(root).relative_to(self.project_root) / name
                    file_list.append(str(relative_path.as_posix()))
        
        return {"status": "success", "files": sorted(file_list)}

    def read_file(self, filepath):
        """
        指定されたファイルのコンテンツを読み取る。
        """
        if not self._is_safe_path(filepath):
            return {"status": "error", "message": "セキュリティ違反: プロジェクト外のファイルへのアクセスは許可されていません。"}
        
        target_file = self.project_root / filepath
        try:
            with open(target_file, 'r', encoding='utf-8') as f:
                content = f.read()
            return {"status": "success", "filepath": filepath, "content": content}
        except FileNotFoundError:
            return {"status": "error", "message": f"ファイルが見つかりません: {filepath}"}
        except Exception as e:
            return {"status": "error", "message": f"ファイルの読み込み中にエラーが発生しました: {str(e)}"}

    def write_file(self, filepath, content):
        """
        指定されたファイルにコンテンツを書き込む（上書き）。
        ファイルが存在しない場合は新規作成する。
        """
        if not self._is_safe_path(filepath):
            return {"status": "error", "message": "セキュリティ違反: プロジェクト外のファイルへの書き込みは許可されていません。"}
            
        target_file = self.project_root / filepath
        try:
            # 親ディレクトリが存在しない場合は作成する
            target_file.parent.mkdir(parents=True, exist_ok=True)
            with open(target_file, 'w', encoding='utf-8') as f:
                f.write(content)
            return {"status": "success", "message": f"ファイル '{filepath}' を正常に書き込みました。"}
        except Exception as e:
            return {"status": "error", "message": f"ファイルの書き込み中にエラーが発生しました: {str(e)}"}

    def search_in_files(self, query):
        """
        プロジェクト内の全ファイルを対象に、指定されたクエリ文字列を検索する。
        """
        results = []
        list_result = self.list_files()
        if list_result["status"] == "error":
            return list_result

        for filepath in list_result["files"]:
            read_result = self.read_file(filepath)
            if read_result["status"] == "success":
                lines = read_result["content"].splitlines()
                for i, line in enumerate(lines):
                    if query in line:
                        results.append({"filepath": filepath, "line_number": i + 1, "line_content": line.strip()})
        
        return {"status": "success", "query": query, "results": results}


def main():
    """
    コマンドライン引数を処理し、アシスタントのメインループを開始する。
    """
    parser = argparse.ArgumentParser(description="Local Code Assistant for Claude Code")
    parser.add_argument('--project', type=str, required=True, help='操作対象のプロジェクトのルートディレクトリ')
    args = parser.parse_args()

    try:
        assistant = LocalCodeAssistant(args.project)
    except ValueError as e:
        logging.error(e)
        sys.exit(1)

    logging.info("Local Code Assistantが起動しました。標準入力からのコマンドを待機しています...")

    # 標準入力からコマンドを一行ずつ読み込み、処理するループ
    for line in sys.stdin:
        try:
            request = json.loads(line)
            command = request.get("command")
            params = request.get("params", {})
            
            response = {}
            if command == "list_files":
                response = assistant.list_files(**params)
            elif command == "read_file":
                response = assistant.read_file(**params)
            elif command == "write_file":
                response = assistant.write_file(**params)
            elif command == "search_in_files":
                response = assistant.search_in_files(**params)
            else:
                response = {"status": "error", "message": f"不明なコマンドです: {command}"}

        except json.JSONDecodeError:
            response = {"status": "error", "message": "無効なJSON形式です。"}
        except Exception as e:
            response = {"status": "error", "message": f"予期せぬエラーが発生しました: {str(e)}"}
        
        # 結果をJSON形式で標準出力に書き出す
        sys.stdout.write(json.dumps(response) + '\n')
        sys.stdout.flush()

if __name__ == "__main__":
    main()
