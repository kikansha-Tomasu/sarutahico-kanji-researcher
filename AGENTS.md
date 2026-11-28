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
- 中国語 Piper 音声は学習データ CC0 の `zh_CN-chaowen-medium` のみ同梱する。
  `phoneme_type: pinyin` のため espeak phonemizer は不要。`pinyin-pro` で
  声母・韻母・声調のシンボル列を作り、`phoneme_id_map` で ID 化する。
  BOS/EOS/pad も同マップから取得し、未対応音素は `console.warn` に記録する。
- 音素系列は上流 `OHF-Voice/piper1-gpl` の `phonemize_chinese.py` に厳密に合わせる。
  旧 espeak ボイスの方式（`BOS,pad,...` と全音素後に pad）を流用すると学習時と
  異なる系列になり発音が崩れる。正しくは BOS の後に pad を入れず、
  `GROUP_END_PHONEMES`（声調 1〜5 と句読点・空白）の後のみ pad を入れる。
- 零声母は `Ø`（ID 3）を明示する。`爱` は `['Ø','ai','4']`、`中` は
  `['zh','ong','1']`、対応 ID はそれぞれ `[1,3,30,67,0,2]` / `[1,18,38,64,0,2]`。
- pinyin-pro は軽声を `de0` / `ma0` と出力するが chaowen の地図には `0` が無く
  `5` が軽声なので `0`→`5` に変換する。上流は `u:` / `ü` のみを `v` に変える。
  pinyin-pro の j/q/x/y 後の韻母は既に上流 g2pW と同じ plain `u` なので
  **追加で `v` 化しない**（`ju1`→`j,u,1`、`quan2`→`q,uan,2`）。
  上流テスト `test_phonemize` も `语`→`['y','u','3']` を期待する。
  上流 docstring の `ju:an3`→`jvan3` は g2pW が `u:` を返した場合の
  defensive な例であり、実際の g2pW 辞書は `ㄐㄩ`→`ju` を返す。
  一方 n/l 後の `ü` は `nü` / `lüe` として入力されるため `v` / `ve` へ変換する
  （`女`→`n,v,3`、`略`→`l,ve,4`）。これは上流の `ㄋㄩ`→`nv` / `ㄌㄩㄝ`→`lve` と一致する。
  `jiu` / `you` の `iu` / `ou` も保持し、`iv` / `ov` のような未定義音素を
  出さない（`九`→`j,iu,3`、`右`→`y,ou,4`）。
- 句読点は `phoneme_id_map` の実シンボルとして保持し、数字は pinyin 変換前に
  漢字へ展開する。一般数値は上流 `unicode_rbnf` の `zh` spellout に合わせ、
  `105` → `一百〇五`、`2026` → `二千〇二十六` とする。
- **年の漢数字は桁読みで `〇` を使う**（`2026年` → `二〇二六年`）。
  `零` は年表記に使わず、既存の `二零二六年` も `〇` へ正規化する。
  一般数値の `〇` と温度の `零下` は上流準拠で併存する。
- 数字展開は `unicode-rbnf==2.4.0` を一時ディレクトリへ導入し、6,142 ケースと
  上位ギャップ集中ケースの期待値を `main.html` の純粋関数と照合済み
  （`FAIL: 0`）。整数は文字列の 4 桁グループで処理し、`Number` による丸めを
  避ける。RBNF に合わせ、`〇` は最下位グループの直前の空グループ、または
  小さい末尾グループの前にだけ 1 つ入れる（上位の途中の空グループでは
  入れない）。（`100001000` → `一亿〇一千`）。正の小数は末尾が全て `0`
  なら省略し、負の小数は丸ごと省略する
  （`-7.5` → `负七`、`-0.5` → `负`、`-0` → `〇`）。
- 数値トークンは `replaceNumericRuns()` で 1 回スキャンする。非数字文字の
  分岐で `i` を進めないと無限ループになり、ブラウザ検証全体がハングする。
  「非数字をコピーしたら必ず `i++`」を守り、64 桁超を含む純粋関数テストを
  先に実行してからブラウザ回帰へ進む。
- 温度・パーセント・漢数字年の regex に `\d{1,64}` のような桁数上限を付けると、
  65 桁目から部分一致して単位変換が壊れる（`1`.repeat(65)+'%'` など）。
  上限を外した `\d+(?:\.\d+)?\s*単位` も単位が無い long run で二乗時間
  になるため、**数値単位は regex を使わず `replaceNumericRuns()` の
  1 回スキャンで処理する**。`matchNumericUnit()` で先読みし、単位が無ければ
  空白を消費しない。4 桁の年は符号を保ったまま桁読みする。
- 漢字の連続に対する `[漢字]+年` / `[漢字]+%` も単位が無い long text で
  全開始位置から再走査となり二乗時間になる。`expandChineseUnitRuns()` で
  1 回スキャンする。年は旧 regex と同じく run の**末尾側だけ**を
  `[〇零一二三四五六七八九]` として `零`→`〇` にし（`十三 年`→`十三年`、
  `一百零一年`→`一百〇一年`）、% は `[零〇一二三四五六七八九十百千万亿两点]+`
  の run 全体を対象にする。`replaceNumericRuns()` も非数字の塊を
  `slice()` でまとめてコピーし、1 文字ずつ連結しない。
- Unicode のマイナス `−` は `%` の前でも ASCII `-` と同じく
  `百分之负…` として扱う（温度は従来どおり `零下…度`）。
- 上流 RBNF / CLDR の大数単位は `京`（10^16）まで。20 桁超で単位が欠けて
  不正な読みになるため、`CHINESE_GROUP_UNITS` に古典的な単位
  （`垓` 10^20 〜 `极` 10^48）を追加する。この拡張部分は上流と照合できない
  が、`123456789012345678901` のような入力でも桁グループが欠落しない。
  名前の付いた単位を超える（10^52 以上）場合は桁読みへフォールバックし、
  単位を黙って消さない。桁区切りカンマは数字展開の前に取り除く
  （`1,000` → `一千`）。
- 年の正規化は `replaceNumericRuns()` が数字 run の長さで判定する。4 桁なら
  符号を保ったまま桁読みし、5 桁以上は一般数値として読み上げる
  （`12026年` → `一万二千〇二十六年`）。末尾に `(?!\d)` を付けると
  `2026年9月` / `2026年2027年` を桁読みできないので使わない。
- 複数の符号が続く場合、% / ℃ では最後の符号だけを負の読みに使い、
  それ以前はそのまま残す（`--1%` → `-百分之负一`、`--1℃` → `-零下一度`）。
  4 桁の年と裸の数値は旧挙動どおり全符号をそのまま残し、絶対値を読む
  （`--2026年` → `--二〇二六年`、`--5` → `--五`）。
- 検証は一時的な Playwright スクリプトで実施する（リポジトリには含めない）。
  起動は `python tools/serve.py`、`http://127.0.0.1:8123/main.html` に対して
  `piperSession.phonemize()` と ID 化結果を上記期待値と突き合わせる。
- 再生停止・音声エラー時は `setTtsStatus('')` で状態表示もクリアする。
- UI 文言は「オフライン」ではなく「API不要」に統一する。実行時は `vendor/` の
  同梱アセットを優先し、無い場合のみ CDN へフォールバックする。
- CDN フォールバックの主要スクリプトには SRI（`CDN_SRI`）を付ける。ハッシュは
  `vendor/` の SHA-256 と同じバイト列なので、`tools/fetch-assets.py` の更新時に
  必ず `CDN_SRI` も更新する。同スクリプトは `CDN_SRI` と `PIPER_ASSET_SRI` の
  キー集合と `main.html` 内の全 `sha256-*` リテラルまで照合し、古い/余分な
  ハッシュを検出する。さらに `resolveAsset()` の全呼び出しサイトを解析し、
   CDN URL が `CDN_SRI` に無ければビルド時にも失敗させる（実行時は例外）。
   `PIPER_ASSET_SRI` で別途検証する音声モデルだけ `{ requireSri: false }` を
   明示する。二次アセット配列（`TESSERACT_LOCAL_ASSETS` /
   `ORT_LOCAL_ASSETS`）も MANIFEST と完全一致するよう照合する。Git リポジトリでは `vendor/` の全ファイルが追跡済みかも
  確認する。`worker.min.js` / `core/` / `lang/` / ORT の `.wasm` / `.mjs` は
  ライブラリ内部で読み込まれ SRI を付けられないため、主要スクリプトが CDN
  フォールバックしても**常にローカル同梱のパスを指定する**。存在確認は
  `requireLocalAssets()` で行い、欠落時は未検証コードを実行せずエラーにする
  （fail-closed）。`tesseractOptions` と `ort.env.wasm.wasmPaths` は
  `*.local` の値で分岐させず、常に `vendor/` を指すこと。
- 音声モデルだけが欠けた場合の Hugging Face フォールバックも未検証のまま
  実行しない。`PIPER_ASSET_SRI`（同梱 model / config の SHA-256）で
  `cachedFetch()` のダウンロードを検証し、不一致ならキャッシュに保存せず
  ブラウザ音声へフォールバックする。キャッシュキーには SRI を含め、
  起動時に旧 `sarutahico-piper-v*` キャッシュを削除する（`v3` 以降）。
  同梱ファイルは `tools/fetch-assets.py` が検証するため、ローカル読み込みでは
  毎回のハッシュ計算は行わない。
- `vendor/` が揃っていれば外部通信ゼロで OCR / Piper が動くことを
  Playwright で確認済み（`external: []`）。
- Tesseract.js の言語データは既定の `4.0.0_best_int` を同梱する。`4.0.0` では
  「中」を「十」と誤認識したため置換した。
- ONNX Runtime Web 1.22 の `.mjs` は MIME が `text/javascript` で必要。
  `python -m http.server` では `text/plain` になるため `tools/serve.py` を使う。
- ライセンス不明の huayan 音声は削除済み。同梱アセットのライセンスは
  `THIRD_PARTY_NOTICES.md` に集約する。
- axe-core で WCAG 2.1 AA を検証済み（Chromium / Firefox とも `violations: []`,
  `incomplete: []`）。背景はグラデーションをやめ単色にし、`--purple` は `#75608F`
  以上に暗くして `#fcfcfc` に対して 4.5:1 を確保する。`--red` / `--gold` / `--green` は
  白文字で 4.5:1 以上になる暗めの色を維持する。範囲入力には `aria-label` を付ける。
- 再生状態の競合対策: `playbackToken` と `activeUtterance` を用い、再生中に別ボタンを
  押したら旧音声を停止してから開始する。Audio の `onended` / `onerror` は
  `activeAudio === audio` を確認してから状態を変更する。準備中のステータス表示は
  `activeButton` と選択音声で判定し、停止後の古い進捗表示が残らないようにする。
- pinyin-pro は同期変換のためタイムアウト不要。再生中に別音声へ切り替えた場合は
  `playbackToken` で古い生成結果を破棄する。
- ブラウザ音声の `cancel()` で発火する `canceled` / `interrupted` エラーは
  「再生に失敗しました」と表示しない。

## 編集時の注意
- 2026-11-28 に Git 管理を開始し、private リポジトリ
  `kikansha-Tomasu/sarutahico-kanji-researcher` へ push 済み（初期コミット `1f6bb20`）。
- 大きな変更前に `backups/` へコピーを残す運用は継続する。
- 変更後は必ず `<script>` を抽出して `node --check` を実行する。
- 外部 API 呼び出しは API モード時のみ。API不要モードでは行わない。
- Piper モデルの初回ダウンロードは大きいため、進捗表示とキャッシュを必ず設ける。
  リモート取得は完全性検証後にのみキャッシュする（キャッシュキーに SRI を含む）。

## 検証コマンド（Windows bash）
```bash
cd "C:\Users\ryosk\OneDrive\ドキュメント\App_CN_character_researcher"
node -e "const fs=require('fs');const c=fs.readFileSync('main.html','utf-8');const s=c.split('<script>')[1].split('</script>')[0];fs.writeFileSync('C:/Users/ryosk/AppData/Local/Temp/opencode/check.js',s)"
node --check C:/Users/ryosk/AppData/Local/Temp/opencode/check.js
```
