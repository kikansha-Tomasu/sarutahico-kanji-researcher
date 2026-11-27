# Third-party notices

This application bundles third-party runtime assets under `vendor/`. They are fetched by `tools/fetch-assets.py`.

| Component | Version | License | Source |
|---|---|---|---|
| onnxruntime-web | 1.22.0 | MIT | https://github.com/microsoft/onnxruntime |
| @diffusionstudio/piper-wasm | 1.0.0 | MIT | https://github.com/diffusion-studio/piper-wasm |
| tesseract.js | 5.1.1 | Apache-2.0 | https://github.com/naptha/tesseract.js |
| tesseract.js-core | 5.1.1 | Apache-2.0 | https://github.com/naptha/tesseract.js-core |
| @tesseract.js-data/chi_sim | 1.0.0 | MIT | https://github.com/naptha/tessdata |
| rhasspy/piper-voices (repository) | — | MIT (Hugging Face card) | https://huggingface.co/rhasspy/piper-voices |
| zh_CN-huayan-x_low / zh_CN-huayan-medium | — | **Unknown / not stated in MODEL_CARD** | https://huggingface.co/rhasspy/piper-voices/tree/main/zh/zh_CN/huayan |

## huayan voice models — important

The `rhasspy/piper-voices` repository itself is tagged `license:mit`, but the model card for both bundled voices states:

```text
License: Unknown
Dataset URL: https://github.com/PlayVoice/HuaYan_TTS
Training: Finetuned from lessac ...
```

The dataset URL above currently returns 404, so the training data license could not be verified. The models are redistributed here only because the user explicitly authorized uploading this project to GitHub. Before making the repository public or using the models commercially, review the upstream licenses and replace the voices with a clearly licensed alternative if needed.

For reference, `zh_CN-chaowen-medium` has a CC0 dataset license, but it requires Piper 1.5 / g2pW pinyin phonemes and is **not** compatible with the bundled phonemizer and phoneme map, so it was not adopted.

## API mode

The optional API mode talks to a user-supplied OpenAI-compatible endpoint. No API client library is bundled, and no request is sent unless the user explicitly switches to API mode.

## Original code

The original application code in this repository (`main.html`, `tools/`, documentation) has no license file. Contact the author before reuse.
