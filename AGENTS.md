# SARUTAHICO 漢字解析アプリ - 開発メモ

## 目的
- 画像・手書きから中国語漢字を読み取り、意味・ピンイン・例文を表示する。
- 基本動作は API 不要（ブラウザ内 OCR + 内蔵辞書 + 音声合成）。
- API モード（ローカル OpenAI 互換 API）は任意機能として残す。

## 現在の構成
- `main.html`: 唯一のアプリ本体（単一 HTML ファイル、ビルド不要）。
- `examples/aivisspeech_auto_demo.html`: AivisSpeech API の参考デモ（API モードの参考のみ）。
- `sarutahico_logo.png`: ヘッダーロゴ。
- `backups/main_before_piper_20261127.html`: Piper 導入前のバックアップ。
- `vendor/`: OCR / Piper / ONNX Runtime の同梱アセット。`tools/fetch-assets.py` で再取得可能。
- `tools/serve.py`: `.mjs` を正しい MIME で配信する開発用ローカルサーバー。
- `tools/fetch-assets.py`: `vendor/` のアセットを取得・サイズ検証するスクリプト。
- `THIRD_PARTY_NOTICES.md`: 同梱アセットのライセンスと注意事項。
- 初期版の名残だった `silent.mp3` は未使用のため削除済み。

## 設計判断
- 重複していた `main.html` / `main_2.html` は統合し、`main.html` に統一した。
- `speechSynthesis.speak()` の戻り値を `src` に代入するバグを廃止し、
  `SpeechSynthesisUtterance` + 再生/停止ボタン方式に変更した。
- OCR は Tesseract.js@5 を動的読み込みし、Otsu 二値化 + コントラストストレッチ +
  複数 PSM（10/8/13）で精度を改善した。ワーカーは永続化する。
- 辞書は `KANJI_DICT` に内蔵。キー重複に注意。
- TTS は `SpeechSynthesis` に加え、Piper/VITS（ONNX Runtime Web/WASM）をブラウザ内で動かすオプションを追加済み。
  Piper が失敗した場合は `SpeechSynthesis` へ自動フォールバックする。
- ブラウザ内 phonemizer は新版の音素表（178種）を使う一方、huayan の音声モデルは
  旧版の表（x_low=130 ID、medium=256 ID空間）を使う。phoneme_ids を直接渡さず、
  `phonemes.phonemes` を `config.phoneme_id_map` でマッピングし直すこと。
- 再生停止・音声エラー時は `setTtsStatus('')` で状態表示もクリアする。
- UI 文言は「オフライン」ではなく「API不要」に統一する。実行時は `vendor/` の
  同梱アセットを優先し、無い場合のみ CDN へフォールバックする。
- `vendor/` が揃っていれば外部通信ゼロで OCR / Piper が動くことを
  Playwright で確認済み（`external: []`）。
- Tesseract.js の言語データは既定の `4.0.0_best_int` を同梱する。`4.0.0` では
  「中」を「十」と誤認識したため置換した。
- ONNX Runtime Web 1.22 の `.mjs` は MIME が `text/javascript` で必要。
  `python -m http.server` では `text/plain` になるため `tools/serve.py` を使う。
- huayan 音声の学習データのライセンスは MODEL_CARD に未記載。公開リポジトリへ
  上げる前に `THIRD_PARTY_NOTICES.md` を確認すること。
- axe-core で WCAG 2.1 AA を検証済み（`violations: []`）。`--red` / `--gold` / `--green` は
  白文字で 4.5:1 以上になる暗めの色を維持する。範囲入力には `aria-label` を付ける。
- 再生状態の競合対策: `playbackToken` と `activeUtterance` を用い、再生中に別ボタンを
  押したら旧音声を停止してから開始する。Audio の `onended` / `onerror` は
  `activeAudio === audio` を確認してから状態を変更する。準備中のステータス表示は
  `activeButton` と選択音声で判定し、停止後の古い進捗表示が残らないようにする。
- phonemizer は stdout を待つだけだとハングするため、20 秒タイムアウトと stderr エラー、
  `cancelPending()` による reject を用意する。BOS/EOS/pad は `phoneme_id_map` から取得し、
  未対応音素は `console.warn` に記録する。
- ブラウザ音声の `cancel()` で発火する `canceled` / `interrupted` エラーは
  「再生に失敗しました」と表示しない。

## 編集時の注意
- 2026-11-28 に Git 管理を開始し、private リポジトリ
  `kikansha-Tomasu/sarutahico-kanji-researcher` へ push 済み（初期コミット `1f6bb20`）。
- 大きな変更前に `backups/` へコピーを残す運用は継続する。
- 変更後は必ず `<script>` を抽出して `node --check` を実行する。
- 外部 API 呼び出しは API モード時のみ。API不要モードでは行わない。
- Piper モデルの初回ダウンロードは大きいため、進捗表示とキャッシュを必ず設ける。

## 検証コマンド（Windows bash）
```bash
cd "C:\Users\ryosk\OneDrive\ドキュメント\App_CN_character_researcher"
node -e "const fs=require('fs');const c=fs.readFileSync('main.html','utf-8');const s=c.split('<script>')[1].split('</script>')[0];fs.writeFileSync('C:/Users/ryosk/AppData/Local/Temp/opencode/check.js',s)"
node --check C:/Users/ryosk/AppData/Local/Temp/opencode/check.js
```
