# バックアップについて

このディレクトリのファイルは、大きな変更前に保存した**過去状態のスナップショット**です。実行時には一切読み込まれません。

GitHub Pages は branch-root（`main` / `/`）で公開され、このディレクトリも配信対象です。そのため旧 HTML はすべて `.html.txt` にリネームしており、Pages 上では実行可能な HTML として扱われません。ロールバック時はファイル名を戻してローカルで使用してください。

- `main_before_chaowen_20261128.html.txt` / `fetch-assets_before_chaowen_20261128.py`
  - ライセンス不明の `huayan` 音声や旧 phonemizer への参照を含みます。
  - ロールバック時の参考としてのみ保持しています。
- `main_before_piper_20261127.html.txt`
  - Piper 導入前の状態です。
- `main_before_residual_fix_20261128.html.txt`
  - UI・進捗表示・OCR・キャッシュ・数値展開の残存修正前の状態です。
- `main_before_keyboard_csp_20261128.html.txt`
  - キーボード描画、解析の競合制御、API URL 制限、開発サーバーの allowlist、Piper の文分割導入前の状態です。
- `main_before_review_fixes_20261128.html.txt` / `serve_before_review_fixes_20261128.py`
  - 残存レビュー対応（ローカル SRI、OCR 初期化の共有、通知の live region 分離、
    Piper 取得の中断、CSP ヘッダーなど）導入前の状態です。ローカル SRI は
    `main.html` 側、CSP は `tools/serve.py` 側の変更です。
- `main_before_uv_fix_20261128.html.txt`
  - n/l + ü の音素化修正（`女` → `n,v,3`、`略` → `l,ve,4`）導入前の状態です。
- `README_before_github_pages_20261128.md` / `serve_before_github_pages_20261128.py`
  - GitHub Pages 対応（`.nojekyll`、ルートの `index.html` リダイレクト、
    開発サーバーの allowlist 更新、README の公開手順）導入前の状態です。
- `main_before_residual_a11y_20261128.html.txt` / `fetch-assets_before_residual_a11y_20261128.py.txt`
  - 第2次残存対応（結果の `lang` / live region、`prefers-reduced-motion`、
    API URL のフィールドエラー、解析 fetch の abort、OCR ジョブ ID、
    Piper 準備セッションの token、SRI call-site 検証とダウンロード上限）導入前の状態です。

現行の実装は、Pages のエントリがリポジトリ直下の `index.html`、アプリ本体が `main.html`、開発サーバーが `tools/` です。
