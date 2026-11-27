# SARUTAHICO 漢字解析アプリ

画像・手書きから中国語漢字を読み取り、意味・ピンイン・例文を表示するブラウザアプリです。ビルド不要で、基本機能は API 不要（外部 API なし）で動作します。

## クイックスタート

```bash
python tools/serve.py
```

ブラウザで <http://127.0.0.1:8123/main.html> を開いてください。

`file://` での直接開きは、Cache API と ES モジュールの制限により推奨しません。必ず上記ローカルサーバー経由で利用してください。

## できること

- 手書きキャンバス／画像ファイルからの漢字認識（Tesseract.js、`chi_sim`）
- 内蔵辞書（367 一意キー）による意味・ピンイン・例文の表示
- 手動入力による辞書検索
- Piper（ブラウザ内ニューラル TTS）による漢字・例文の音声再生
  - `piper:medium`（CC0 学習データの `chaowen`、モデル約 63 MB）
  - ブラウザ標準音声（`SpeechSynthesis`）への自動フォールバック
- 速度・音程調整、再生／停止、再生の競合制御
- 任意の OpenAI 互換ローカル API を使う API 連携モード

## アセットについて

`vendor/` に OCR・Piper・ONNX Runtime・ピンイン変換のアセットを同梱しています。同梱アセットがある限り、実行時に外部通信は発生しません。アセットを更新したい場合は次を実行してください。

```bash
python tools/fetch-assets.py
```

主要スクリプト（`tesseract.min.js` / `ort.min.js` / `pinyin-pro.js` / 音声モデル）が無い場合は CDN へフォールバックしますが、その際は外部通信が発生します。`worker.min.js`・`core/`・`lang/`・`.wasm` などの二次アセットが欠落している場合は CDN フォールバックせず失敗するため、`tools/fetch-assets.py` を再実行してください。同スクリプトはサイズと SHA-256 の両方で整合性を検証します。

同梱アセットのライセンスは [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。同梱の中国語音声は学習データが CC0 の `chaowen` のみで、ライセンス不明のモデルは含まれていません。

## 検証

`main.html` の `<script>` を抽出して構文チェック:

```bash
node -e "const fs=require('fs');const c=fs.readFileSync('main.html','utf-8');const s=c.split('<script>')[1].split('</script>')[0];fs.writeFileSync('check.js',s)" && node --check check.js
```

ブラウザ検証は Playwright（`playwright-core` + Edge）で実施しています。主な確認項目:

- OCR（`中` の認識）、Piper `chaowen` の WAV 生成、ブラウザ音声フォールバック
- 再生中のボタン切替、準備中の停止、上流準拠のピンイン音素化
  （零声母 `Ø`、軽声 `0`→`5`、ü の `v` 化、グループ末尾のみ pad）
- 外部通信を遮断した状態での OCR / Piper 動作
- axe-core による WCAG 2.1 AA 検証（Chromium / Firefox とも `violations: []`, `incomplete: []`）
- Firefox の OCR / Piper、WebKit の OCR / モデル推論

## ファイル構成

```text
main.html                    アプリ本体（単一 HTML）
AGENTS.md                    設計判断・検証知見
THIRD_PARTY_NOTICES.md       同梱アセットのライセンス情報
tools/serve.py               MIME 正しい開発用ローカルサーバー
tools/fetch-assets.py        vendor/ の取得・検証
vendor/                      OCR / Piper / ONNX Runtime / pinyin-pro 同梱アセット
examples/                    AivisSpeech API の参考デモ
backups/                     変更前のバックアップ
sarutahico_logo.png          ヘッダーロゴ
```

## 制約

- 動作確認済み: Chromium 系（Edge）と Firefox で OCR・Piper 再生・axe 検証が完了しています。
- WebKit（Safari 系エンジン）では OCR とモデル推論まで確認できましたが、検証用ヘッドレスビルドに音声出力機能が無いため再生は未検証です。実機 Safari も未検証です。
- 初回のモデル読み込みには数秒〜十数秒かかります（同梱アセットがある場合はダウンロードは発生しません）。
- 音声の自然さは聴取による主観評価が必要です。自動テストでは WAV の生成・再生状態・ピーク値と、上流 `piper1-gpl` の音素/ID 系列との一致までを検証しています。
