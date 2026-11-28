#   猿田彦 漢字解析アプリ

画像・手書きから中国語漢字を読み取り、意味・ピンイン・例文を表示するブラウザアプリです。ビルド不要で、基本機能は API 不要（外部 API なし）で動作します。
「猿田彦」様は日本の「導きの神」のため，名前に使っています。

## クイックスタート

```bash
python tools/serve.py
```

ブラウザで <http://127.0.0.1:8123/main.html> を開いてください。

開発サーバーはアプリに必要なファイルだけを配信します（`/vendor/`、`/examples/`、`/index.html`、`/main.html`、`/sarutahico_logo.png`）。`.git/` や `backups/`、`tools/` は配信されません。`--bind 0.0.0.0` で起動する場合も同様です。CSP ヘッダーも付与します（単一 HTML のインラインスクリプト、Tesseract/Piper の blob URL、SRI 付き CDN フォールバック用の `https://cdn.jsdelivr.net` を許可し、接続先を self・HTTP(S) に制限します）。API URL 自体はアプリ側で loopback のみに制限されます。

`file://` での直接開きは、Cache API と ES モジュールの制限により推奨しません。開発時は上記ローカルサーバー、公開時は後述の GitHub Pages 経由で利用してください。

## GitHub Pages で使う

1. GitHub Free では public リポジトリからのみ Pages を公開できます（private からの公開には Pro / Team / Enterprise 等が必要）。このリポジトリは public です。リポジトリの **Settings → Pages → Build and deployment** で、Source を `Deploy from a branch`、Branch を `main`、Folder を `/(root)` に設定します。
2. ルートの `.nojekyll` により Jekyll の変換は行われません。ビルドは不要です。
3. 公開 URL は `https://<owner>.github.io/<repository>/` です（ユーザー／組織サイトの場合は `https://<owner>.github.io/`）。ルート URL の `index.html` は `main.html` へリダイレクトします。直接 `https://<owner>.github.io/<repository>/main.html` を開いても動作します。
4. Pages に配置した `vendor/` があれば、OCR・Piper とも外部通信なしで動作します。主要スクリプトが欠けた場合は SRI 検証付きの CDN へ、音声モデルが欠けた場合は完全性検証付きの Hugging Face へフォールバックします。Tesseract / ORT の二次アセットが欠けた場合はフォールバックせずエラーになります。

このリポジトリでは Pages を有効化済みで、公開 URL は `https://kikansha-tomasu.github.io/sarutahico-kanji-researcher/` です。fork などで有効化されていない場合は、上記の Settings 操作が必要です。

GitHub Pages では開発サーバーの CSP・allowlist・MIME 指定は使えません。MIME は Pages 側の既定値（`.mjs` は `text/javascript`、`.wasm` は `application/wasm`）に依存します。Pages サイトは公開され、`backups/` / `tools/` / `AGENTS.md` を含むリポジトリ全体が配信対象です。秘密情報は置かないでください。旧バックアップと参考デモの HTML は `.html.txt` にリネームしており、Pages では実行可能な HTML として配信されません。API 連携モードは引き続き loopback のみを受け付けるため、Pages 版では API 不要モードでの利用を想定しています。再設定や fork では GitHub の設定操作が必要で、push だけでは公開されません。

## できること

- 手書きキャンバス／画像ファイル（選択・ドラッグ＆ドロップ・Ctrl+V 貼り付け）からの漢字認識（Tesseract.js、`chi_sim`、Otsu 二値化＋インク領域クロップ正規化）
- キャンバスのキーボード描画（矢印／Shift+矢印で移動、Space／Enterで描画、Homeで中央、Escで取り消し、Ctrl+Zで元に戻す）
- 内蔵辞書（620 一意キー）による意味・ピンイン・例文の表示（未登録漢字も同梱 `pinyin-pro` でピンイン自動推定）
- 手動入力による辞書検索（IME 変換対応、API 連携モード時は API 検索に連動）、最近の検索履歴（最大 8 件）、結果コピー
- 解析のキャンセルと競合制御（モード切替・描画・画像選択で実行中解析を破棄）
- Piper（ブラウザ内ニューラル TTS）による漢字・例文の音声再生
  - `piper:medium`（CC0 学習データの `chaowen`、モデル約 63 MB）
  - 文末記号ごとに推論を分け、BOS/EOS をリセットして音声を連結
  - ブラウザ標準音声（`SpeechSynthesis`）への自動フォールバック
- 速度・音程調整、再生／停止、再生の競合制御
- 任意の OpenAI 互換ローカル API を使う API 連携モード（URL は loopback のみ、15 秒タイムアウト）

## アセットについて

`vendor/` に OCR・Piper・ONNX Runtime・ピンイン変換のアセットを同梱しています。同梱アセットがある限り、実行時に外部通信は発生しません。アセットを更新したい場合は次を実行してください。

```bash
python tools/fetch-assets.py
```

主要スクリプト（`tesseract.min.js` / `ort.min.js` / `pinyin-pro.js`）が無い場合は CDN へフォールバックしますが、その際は外部通信が発生します。SRI（Subresource Integrity）は同梱ファイルを読み込む場合にも適用され、実行時にバイト列の改ざんを検出します。CDN フォールバック時も SRI で改ざんされたレスポンスを拒否します。`worker.min.js`・`core/`・`lang/`・`.wasm` などライブラリ内部で読み込まれる二次アセットは SRI を付けられないため、主要スクリプトが CDN フォールバックした場合でも**常にローカル同梱のパスを使います**。欠落時は未検証コードの実行を避けて処理を失敗させ、再取得を促すメッセージを表示します。`tools/fetch-assets.py` はサイズ・SHA-256 に加えて、`main.html` の全 SRI ハッシュ（CDN 主要スクリプトと音声モデル／設定）が同梱ファイルと一致するかも検証します。Git リポジトリ内では `vendor/` の全ファイルが追跡済みかも確認し、配布漏れを検出します。音声モデルだけが無い場合は Hugging Face から取得しますが、設定・モデルとも SHA-256 を照合し、一致しない場合は破棄してブラウザ音声へフォールバックします。検証済みのバイト列だけを Cache API に保存し、キャッシュキーにも SRI を含めるため、ハッシュ変更時に古い内容が再利用されることはありません。ローカル同梱アセットはビルド時に検証済みのためキャッシュしません（更新後に古い内容が残らないようにするためです）。古い `sarutahico-piper-v*` キャッシュは起動時に削除します。

同梱アセットのライセンスは [THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md) を参照してください。同梱の中国語音声は学習データが CC0 の `chaowen` のみで、ライセンス不明のモデルは含まれていません。

## 検証

`main.html` の `<script>` を抽出して構文チェック:

```bash
node -e "const fs=require('fs');const c=fs.readFileSync('main.html','utf-8');const s=c.split('<script>')[1].split('</script>')[0];fs.writeFileSync('check.js',s)" && node --check check.js
```

ブラウザ検証は Playwright（`playwright-core` + Edge）で実施しています。主な確認項目:

- OCR（`中` の認識）、Piper `chaowen` の WAV 生成、ブラウザ音声フォールバック
- 再生中のボタン切替、準備中の停止、上流準拠のピンイン音素化
  （零声母 `Ø`、軽声 `0`→`5`、ü 韻母のみ `v` 化、グループ末尾のみ pad）
  （`九` → `j,iu,3`、`右` → `y,ou,4`、`居` → `j,u,1`）
- 数字展開（`2026年` → `二〇二六年`、`105` → `一百〇五`、`100001000` → `一亿〇一千`、`1,000` → `一千`）と上流 RBNF 8,178 ケース・上位ギャップ集中ケース（86 ケース）との一致、ランダム 20,000 ケースのファズテスト（`FAILURES 0`）
- 20 桁超の桁グループ読み（`123456789012345678901` → `一垓二千三百四十五京…`）で単位が欠落しないこと
- 年の桁読み（`2026年9月` → `二〇二六年九月`、`2026年2027年` → `二〇二六年二〇二七年`、5 桁以上は一般数値）
- CDN フォールバック時の SRI 属性付与、不正ハッシュの拒否、二次アセット欠落時の fail-closed、二次アセットのローカルパス強制
- Hugging Face フォールバックの完全性検証（正常モデルは再生・キャッシュ再利用、改ざんモデルは拒否してブラウザ音声へ切替）、旧キャッシュの削除。ローカル同梱アセットが Cache API に保存されないこと
- 外部通信を遮断した状態での OCR / Piper 動作
- Piper の句読点クラスタ（`。 ` / `！！` / `……`）保持と文ごとの推論分割
- 解析の競合制御（実行中にモード切替で古い OCR 結果を破棄、空キャンバスで完了状態を通知しない）
- API URL の loopback 制限（外部ホスト・埋め込み認証情報を拒否）と fetch の中断シグナル（モード切替時に実行中 fetch を abort）
- 残存レビュー項目: 結果ノードの `lang="zh-CN"`（二言語例文は中国語/日本語を個別タグ化）、結果要約の polite 通知とクリア、通常/緊急メッセージの `aria-live` 切替、`prefers-reduced-motion`、API URL のフィールド単位エラー、途中経過の過剰通知抑止、OCR ジョブ ID の一意性と直列化、古い Piper 準備セッションの解放と結果破棄
- 開発サーバーの allowlist（`/` と `/index.html` が 200、`.git/config` / `backups/` / `tools/` / `README.md` が 404）
- GitHub Pages 相当のサブパス配信（ルートのリダイレクト、OCR / Piper、SRI、外部通信ゼロ）
- 実 GitHub Pages の live 配信（ルートのリダイレクト、主要／二次アセットと音声モデルの 200、SRI、OCR / Piper、外部通信ゼロ）を Edge / Firefox / WebKit で確認
- CDN / Hugging Face の実ネットワーク（SRI 一致、CORS、モデル・設定の完全性）
- axe-core による WCAG 2.1 AA 検証（Chromium / Firefox、実 Pages では Firefox / WebKit とも `violations: []`, `incomplete: []`）
- Firefox の OCR / Piper、WebKit の OCR / モデル推論（実 Pages でも両エンジンで OCR・音素生成を確認）

## ファイル構成

```text
main.html                    アプリ本体（単一 HTML）
index.html                   GitHub Pages のルート用リダイレクト（アプリ本体ではない）
.nojekyll                    GitHub Pages で Jekyll 変換を無効化
AGENTS.md                    設計判断・検証知見
LICENSE                      アプリ本体の MIT ライセンス
SECURITY.md                  脆弱性報告方針
THIRD_PARTY_NOTICES.md       同梱アセットのライセンス情報
tools/serve.py               MIME 正しい開発用ローカルサーバー
tools/fetch-assets.py        vendor/ の取得・検証
vendor/                      OCR / Piper / ONNX Runtime / pinyin-pro 同梱アセット
examples/                    AivisSpeech API の参考デモ（.html.txt、実行不可）
backups/                     変更前のバックアップ（旧 HTML は .html.txt）
sarutahico_logo.png          ヘッダーロゴ
```

## 制約

- 動作確認済み: Chromium 系（Edge）と Firefox で OCR・Piper 再生・axe 検証が完了しています。
- 実 GitHub Pages（`https://kikansha-tomasu.github.io/sarutahico-kanji-researcher/`）でもルートのリダイレクト、全 `vendor/` アセットの 200、OCR / Piper、外部通信ゼロを確認済みです。
- CDN / Hugging Face の実ネットワークでも SRI・CORS・モデル／設定の完全性を確認済みです。通常は同梱 `vendor/` を使うため、これらの通信は発生しません。
- WebKit（Safari 系エンジン）では OCR・キーボード描画・モデル推論まで確認できましたが、検証用ヘッドレスビルドには `speechSynthesis` / `SpeechSynthesisUtterance` 自体が無いため、Piper 失敗時のブラウザ音声フォールバックは未検証です。実機 Safari / iOS とスクリーンリーダーも未検証です。
- API 連携モードの URL は `127.0.0.1` / `localhost` / `::1` の http(s) のみ受け付けます。LAN 上の別ホストにある API は指定できません。ローカル API 側で `http://127.0.0.1:8123` からの CORS（`Access-Control-Allow-Origin` と `Content-Type` の許可）が必要です。
- 初回のモデル読み込みには数秒〜十数秒かかります（同梱アセットがある場合はダウンロードは発生しません）。
- 音声の自然さは聴取による主観評価が必要です。自動テストでは WAV の生成・再生状態・ピーク値と、上流 `piper1-gpl` の音素/ID 系列との一致までを検証しています。
- `vendor/piper/.../zh_CN-chaowen-medium.onnx` は約 60 MB で、GitHub の推奨上限 50 MB を超えるため警告が表示されます。100 MB の硬制限内で push 済みですが、Git LFS 移行は外部ストレージ設定を伴うため未実施です。
- `backups/` は過去状態のスナップショットです。旧ライセンス不明モデルや旧 phonemizer への参照を含みますが、実行時には読み込まれません（[backups/README.md](backups/README.md) 参照）。Pages では `.html.txt` として配信されるため、ブラウザでアプリとして実行することもできません。
- 上流 RBNF は 19 桁以上で `NoRuleForNumberError`、17 桁の一部でも再帰上限に達するため、その範囲の一致は検証対象外です。アプリ側は `京`＝10^16 までを上流と照合済みで、それより大きい値は古典的な大数単位（`垓`＝10^20 〜 `极`＝10^48）で欠落なく読み上げますが、この拡張部分は上流 RBNF では検証できません。名前の付いた単位が無い 10^52 以上は桁読みへフォールバックします。
