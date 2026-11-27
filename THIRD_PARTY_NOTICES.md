# Third-party notices

This application bundles third-party runtime assets under `vendor/`. They are fetched by `tools/fetch-assets.py`.

| Component | Version | License | Source |
|---|---|---|---|
| onnxruntime-web | 1.22.0 | MIT | https://github.com/microsoft/onnxruntime |
| pinyin-pro | 3.29.5 | MIT | https://github.com/anylee2021/pinyin-pro |
| tesseract.js | 5.1.1 | Apache-2.0 | https://github.com/naptha/tesseract.js |
| tesseract.js-core | 5.1.1 | Apache-2.0 | https://github.com/naptha/tesseract.js-core |
| @tesseract.js-data/chi_sim | 1.0.0 | MIT | https://github.com/naptha/tessdata |
| rhasspy/piper-voices (repository) | — | MIT (Hugging Face card) | https://huggingface.co/rhasspy/piper-voices |
| zh_CN-chaowen-medium | — | dataset: CC0 (per MODEL_CARD) | https://huggingface.co/rhasspy/piper-voices/tree/main/zh/zh_CN/chaowen |

## Chinese voice model

The bundled voice is `zh_CN-chaowen-medium`. Its MODEL_CARD states `License: CC0` for the training dataset sourced from `OHF-Voice/voice-datasets`. The base voice is derived from the Hi-Fi TTS reader; review that upstream source before commercial use.

Previously bundled `zh_CN-huayan-*` models were removed: their MODEL_CARD stated `License: Unknown` and the linked dataset (`PlayVoice/HuaYan_TTS`) returns 404. No license-unknown voice is redistributed now.

The app generates Piper pinyin phonemes (initial / final / tone symbols) in the browser with `pinyin-pro`, so the espeak-based `piper-wasm` phonemizer and its 18 MB data files are no longer bundled.

## API mode

The optional API mode talks to a user-supplied OpenAI-compatible endpoint. No API client library is bundled, and no request is sent unless the user explicitly switches to API mode.

## Original code

The original application code in this repository (`main.html`, `tools/`, documentation) is licensed under the MIT License; see [`LICENSE`](LICENSE). Bundled third-party assets keep their own licenses as described above.
