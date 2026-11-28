# バックアップについて

このディレクトリのファイルは、大きな変更前に保存した**過去状態のスナップショット**です。実行時には一切読み込まれません。

- `main_before_chaowen_20261128.html` / `fetch-assets_before_chaowen_20261128.py`
  - ライセンス不明の `huayan` 音声や旧 phonemizer への参照を含みます。
  - ロールバック時の参考としてのみ保持しています。
- `main_before_piper_20261127.html`
  - Piper 導入前の状態です。
- `main_before_residual_fix_20261128.html`
  - UI・進捗表示・OCR・キャッシュ・数値展開の残存修正前の状態です。
- `main_before_keyboard_csp_20261128.html`
  - キーボード描画、解析の競合制御、API URL 制限、開発サーバーの allowlist、Piper の文分割導入前の状態です。
- `main_before_review_fixes_20261128.html` / `serve_before_review_fixes_20261128.py`
  - 残存レビュー対応（ローカル SRI、OCR 初期化の共有、通知のlive region 分離、
    Piper 取得の中断、CSP ヘッダーなど）導入前の状態です。ローカル SRI は
    `main.html` 側、CSP は `tools/serve.py` 側の変更です。

現行の実装はリポジトリ直下の `main.html` と `tools/` のみを参照してください。
