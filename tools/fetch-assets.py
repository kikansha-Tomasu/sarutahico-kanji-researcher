#!/usr/bin/env python3
"""Download all runtime assets so the app works without a CDN.

Run:
    python tools/fetch-assets.py

Assets are written under vendor/. Re-running only replaces files whose size
does not match the manifest, so it is safe to use for updates.
"""
from __future__ import annotations

import hashlib
import os
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, "vendor")

ORT = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/"
PIPER_JS = "https://cdn.jsdelivr.net/npm/@diffusionstudio/piper-wasm@1.0.0/build/"
HF = "https://huggingface.co/rhasspy/piper-voices/resolve/main"
TESS = "https://cdn.jsdelivr.net/npm/tesseract.js@5.1.1/dist/"
TESS_CORE = "https://cdn.jsdelivr.net/npm/tesseract.js-core@5.1.1/"
TESS_LANG = "https://cdn.jsdelivr.net/npm/@tesseract.js-data/chi_sim@1.0.0/4.0.0_best_int/"

MANIFEST = [
    (ORT + "ort.min.js", "ort/ort.min.js", 357641),
    (ORT + "ort-wasm-simd-threaded.wasm", "ort/ort-wasm-simd-threaded.wasm", 11210254),
    (ORT + "ort-wasm-simd-threaded.mjs", "ort/ort-wasm-simd-threaded.mjs", 20856),
    (ORT + "ort-wasm-simd-threaded.jsep.mjs", "ort/ort-wasm-simd-threaded.jsep.mjs", 44677),
    (ORT + "ort-wasm-simd-threaded.jsep.wasm", "ort/ort-wasm-simd-threaded.jsep.wasm", 21872216),
    (PIPER_JS + "piper_phonemize.js", "piper/piper_phonemize.js", 120714),
    (PIPER_JS + "piper_phonemize.wasm", "piper/piper_phonemize.wasm", 635212),
    (PIPER_JS + "piper_phonemize.data", "piper/piper_phonemize.data", 18077249),
    (HF + "/zh/zh_CN/huayan/x_low/zh_CN-huayan-x_low.onnx.json",
     "piper/models/zh/zh_CN/huayan/x_low/zh_CN-huayan-x_low.onnx.json", 4164),
    (HF + "/zh/zh_CN/huayan/x_low/zh_CN-huayan-x_low.onnx",
     "piper/models/zh/zh_CN/huayan/x_low/zh_CN-huayan-x_low.onnx", 20628813),
    (HF + "/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx.json",
     "piper/models/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx.json", 4822),
    (HF + "/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx",
     "piper/models/zh/zh_CN/huayan/medium/zh_CN-huayan-medium.onnx", 63201294),
    (TESS + "tesseract.min.js", "tesseract/tesseract.min.js", 66695),
    (TESS + "worker.min.js", "tesseract/worker.min.js", 123724),
    (TESS_CORE + "tesseract-core.wasm.js", "tesseract/core/tesseract-core.wasm.js", 4734777),
    (TESS_CORE + "tesseract-core.wasm", "tesseract/core/tesseract-core.wasm", 3457035),
    (TESS_CORE + "tesseract-core-simd.wasm.js", "tesseract/core/tesseract-core-simd.wasm.js", 4735153),
    (TESS_CORE + "tesseract-core-simd.wasm", "tesseract/core/tesseract-core-simd.wasm", 3457317),
    (TESS_CORE + "tesseract-core-lstm.wasm.js", "tesseract/core/tesseract-core-lstm.wasm.js", 3938277),
    (TESS_CORE + "tesseract-core-lstm.wasm", "tesseract/core/tesseract-core-lstm.wasm", 2859424),
    (TESS_CORE + "tesseract-core-simd-lstm.wasm.js", "tesseract/core/tesseract-core-simd-lstm.wasm.js", 3938657),
    (TESS_CORE + "tesseract-core-simd-lstm.wasm", "tesseract/core/tesseract-core-simd-lstm.wasm", 2859709),
    (TESS_LANG + "chi_sim.traineddata.gz", "tesseract/lang/chi_sim.traineddata.gz", 1718768),
]


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    failures = []
    for url, rel, expected in MANIFEST:
        dest = os.path.join(VENDOR, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if os.path.exists(dest) and os.path.getsize(dest) == expected:
            print(f"OK       {rel} ({expected:,} bytes)")
            continue
        print(f"DOWNLOAD {rel} ...", flush=True)
        tmp = dest + ".part"
        try:
            req = urllib.request.Request(url, headers={"User-Agent": "sarutahico-asset-fetch/1.0"})
            with urllib.request.urlopen(req, timeout=120) as res, open(tmp, "wb") as out:
                while True:
                    chunk = res.read(1024 * 1024)
                    if not chunk:
                        break
                    out.write(chunk)
            size = os.path.getsize(tmp)
            if expected and size != expected:
                raise RuntimeError(f"size mismatch: expected {expected}, got {size}")
            os.replace(tmp, dest)
            print(f"SAVED    {rel} sha256={sha256(dest)[:16]}")
        except Exception as exc:  # keep going, report all failures at the end
            if os.path.exists(tmp):
                os.remove(tmp)
            failures.append((rel, str(exc)))
            print(f"FAILED   {rel}: {exc}", file=sys.stderr)
    if failures:
        print(f"\n{len(failures)} asset(s) failed to download.", file=sys.stderr)
        return 1
    print("\nAll assets are available locally in vendor/.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
