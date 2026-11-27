#!/usr/bin/env python3
"""Download all runtime assets so the app works without a CDN.

Run:
    python tools/fetch-assets.py

Assets are written under vendor/. Re-running replaces files whose size or
SHA-256 does not match the manifest. Upstream version changes require updating
the manifest URLs, sizes and hashes.
"""
from __future__ import annotations

import base64
import hashlib
import os
import re
import subprocess
import sys
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
VENDOR = os.path.join(ROOT, "vendor")

ORT = "https://cdn.jsdelivr.net/npm/onnxruntime-web@1.22.0/dist/"
PINYIN = "https://cdn.jsdelivr.net/npm/pinyin-pro@3.29.5/"
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
    (PINYIN + "dist/index.js", "pinyin/pinyin-pro.js", 325698),
    (PINYIN + "LICENSE", "pinyin/LICENSE", 1070),
    (HF + "/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx.json",
     "piper/models/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx.json", 4360),
    (HF + "/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx",
     "piper/models/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx", 63221984),
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

SHA256 = {
    "ort/ort.min.js": "924e4fcdfdf69acccff3d024d6e1ad3f41ca858d27fc4dd59fc4927dd933e7db",
    "ort/ort-wasm-simd-threaded.wasm": "71aef04959c5c1b6de461b6538e2058e306610034a85aad2742d0c7fd4533fe4",
    "ort/ort-wasm-simd-threaded.mjs": "30dd851d9c00622940500f71ddd2ff8820c5cb65270816080175b958705385a8",
    "ort/ort-wasm-simd-threaded.jsep.mjs": "1cbcba8f2c769c1eecbab66a1b1e55ef11704515bf4306373e3db3c37cf6dcd8",
    "ort/ort-wasm-simd-threaded.jsep.wasm": "b45970d0632383a057c27ca5b660b216f8e00c17cf8db9f6207b5e4abc839368",
    "pinyin/pinyin-pro.js": "a488173470768ace074c3c4fffbb880e83523b3aa9598a8147c930e7f2d5c7dc",
    "pinyin/LICENSE": "824f6069c5a59b0c1650d0fb9f8d091866c6019eb761c8e658dfc03f001eabd2",
    "piper/models/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx.json": "48477042ba5f07dc1f10ac535a25f21bb6a0f9c40581d2f6d0ce5f51a1d347a6",
    "piper/models/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx": "83a5268616ad0aa2d3e2b67158824b5e23b24e0973473ce28859c059457b824e",
    "tesseract/tesseract.min.js": "a8e29918d098b2b06e1012bdaeffb4aec0445c5d5654709023e0bd1f442a80e8",
    "tesseract/worker.min.js": "aca1229639fc9907d86f96e825955a2b7c5716d17f3bc3acd71f9c7ab66181fc",
    "tesseract/core/tesseract-core.wasm.js": "2b8c8c92b8788807061fb4bb16c5acdf000c149e100255f879f78d2c58ca9969",
    "tesseract/core/tesseract-core.wasm": "b47a852b19181ae0999f9d970c368cd351135a320ea978b35bd38602d8bcc0bc",
    "tesseract/core/tesseract-core-simd.wasm.js": "63f232c4f7a97b04e52eb940202700b2c6239783a75d0ff0553274fac530cd5c",
    "tesseract/core/tesseract-core-simd.wasm": "baa2f54ef5af43ada4605fd7ae999bde3c6ecc96bfe0d0410b0b4f4a5f9c8b91",
    "tesseract/core/tesseract-core-lstm.wasm.js": "8f04aa0cc81e7bde33f80e92fa01a7a665f0b4884d098acf5de9c7104a11dfaa",
    "tesseract/core/tesseract-core-lstm.wasm": "5db58ea4d1bd4256be81e8ae3b4fa226c4625dfba1850b1b3308dbf3700e9929",
    "tesseract/core/tesseract-core-simd-lstm.wasm.js": "ce20eda9533cbed1e6c2b4276fbae1e0adc61b6754b5513084be601787b457cf",
    "tesseract/core/tesseract-core-simd-lstm.wasm": "66b601224a0c4a8977bc9d92dd39841189f9ca22cc4122fcd7208cdb0961eeef",
    "tesseract/lang/chi_sim.traineddata.gz": "b8a23f10c7de500891eb458a8adc9cc58ab7f242f08b7d149f5e9aea4ad5db7c",
}


def sha256(path: str) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def check_cdn_sri() -> list[str]:
    """Ensure every SRI hash in main.html matches a vendored SHA-256.

    Covers both CDN fallback scripts and the optional Hugging Face voice
    fallback, so a changed vendored file cannot leave a stale browser hash.
    """
    html_path = os.path.join(ROOT, "main.html")
    if not os.path.exists(html_path):
        return [f"main.html not found: {html_path}"]
    with open(html_path, encoding="utf-8") as f:
        html = f.read()
    constants = dict(re.findall(r"const (ORT_BASE|PINYIN_PRO_BASE|TESSERACT_CDN) = '([^']+)';", html))

    def resolve(expr: str) -> str:
        expr = expr.strip()
        if expr in constants:
            return constants[expr]
        match = re.fullmatch(r"(\w+)\s*\+\s*'([^']+)'", expr)
        if match and match.group(1) in constants:
            return constants[match.group(1)] + match.group(2)
        return expr

    declared = {
        resolve(expr): digest
        for expr, digest in re.findall(r"\[([^\]]+)\]\s*:\s*['\"]sha256-([^'\"]+)['\"]", html)
    }
    pairs = [
        (ORT + "ort.min.js", "ort/ort.min.js"),
        (PINYIN + "dist/index.js", "pinyin/pinyin-pro.js"),
        (TESS + "tesseract.min.js", "tesseract/tesseract.min.js"),
    ]
    digests = {
        rel: base64.b64encode(bytes.fromhex(SHA256[rel])).decode("ascii")
        for _, rel in pairs
    }
    voice_rel = "piper/models/zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx"
    voice_path = "zh/zh_CN/chaowen/medium/zh_CN-chaowen-medium.onnx"
    voice_pairs = [(voice_path, voice_rel), (voice_path + ".json", voice_rel + ".json")]
    voice_digests = {
        rel: base64.b64encode(bytes.fromhex(SHA256[rel])).decode("ascii")
        for _, rel in voice_pairs
    }
    declared_voice = {
        path: digest
        for path, digest in re.findall(
            r"['\"]([^'\"]+\.onnx(?:\.json)?)['\"]\s*:\s*['\"]sha256-([^'\"]+)['\"]", html
        )
    }
    failures = []
    for url, rel in pairs:
        actual = declared.get(url)
        if actual != digests[rel]:
            failures.append(f"CDN_SRI mismatch for {rel}: {actual} != {digests[rel]}")
    expected_urls = {url for url, _ in pairs}
    extra_urls = set(declared) - expected_urls
    missing_urls = expected_urls - set(declared)
    if extra_urls or missing_urls:
        failures.append(f"CDN_SRI keys mismatch: extra={sorted(extra_urls)}, missing={sorted(missing_urls)}")
    for path, rel in voice_pairs:
        actual = declared_voice.get(path)
        if actual != voice_digests[rel]:
            failures.append(f"PIPER_ASSET_SRI mismatch for {rel}: {actual} != {voice_digests[rel]}")
    expected_paths = {path for path, _ in voice_pairs}
    extra_paths = set(declared_voice) - expected_paths
    missing_paths = expected_paths - set(declared_voice)
    if extra_paths or missing_paths:
        failures.append(
            f"PIPER_ASSET_SRI keys mismatch: extra={sorted(extra_paths)}, "
            f"missing={sorted(missing_paths)}"
        )
    # Quote-agnostic so a double-quoted or template-literal hash cannot be
    # silently ignored. The validation regex in main.html does not match here
    # because a base64 digest cannot start with '(' or "'".
    literals = set(re.findall(r"sha256-([A-Za-z0-9+/]+={0,2})", html))
    expected_literals = set(digests.values()) | set(voice_digests.values())
    if literals != expected_literals:
        failures.append(
            f"sha256 literals mismatch: extra={sorted(literals - expected_literals)}, "
            f"missing={sorted(expected_literals - literals)}"
        )
    return failures


def check_git_tracking() -> list[str]:
    """Report manifest assets that are present but not committed to git."""
    if not os.path.isdir(os.path.join(ROOT, ".git")):
        return []
    try:
        tracked = set(subprocess.check_output(
            ["git", "ls-files", "vendor"], cwd=ROOT, text=True
        ).splitlines())
    except Exception as exc:
        return [f"git tracking check failed: {exc}"]
    tracked = {path.replace(os.sep, "/") for path in tracked}
    expected = {"vendor/" + rel for _, rel, _ in MANIFEST}
    for dirpath, _, filenames in os.walk(os.path.join(ROOT, "vendor")):
        for name in filenames:
            path = os.path.relpath(os.path.join(dirpath, name), ROOT)
            expected.add(path.replace(os.sep, "/"))
    missing = sorted(expected - tracked)
    if missing:
        return [f"vendor assets not tracked by git: {missing}"]
    return []


def main() -> int:
    failures = []
    for url, rel, expected in MANIFEST:
        dest = os.path.join(VENDOR, rel.replace("/", os.sep))
        os.makedirs(os.path.dirname(dest), exist_ok=True)
        if (os.path.exists(dest) and os.path.getsize(dest) == expected
                and sha256(dest) == SHA256[rel]):
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
            digest = sha256(tmp)
            if digest != SHA256[rel]:
                raise RuntimeError(f"sha256 mismatch: expected {SHA256[rel][:16]}, got {digest[:16]}")
            os.replace(tmp, dest)
            print(f"SAVED    {rel} sha256={digest[:16]}")
        except Exception as exc:  # keep going, report all failures at the end
            if os.path.exists(tmp):
                os.remove(tmp)
            failures.append((rel, str(exc)))
            print(f"FAILED   {rel}: {exc}", file=sys.stderr)
    sri_failures = check_cdn_sri() + check_git_tracking()
    for failure in sri_failures:
        print(f"FAILED   {failure}", file=sys.stderr)
    failures.extend(sri_failures)
    if failures:
        print(f"\n{len(failures)} asset check(s) failed (see FAILED lines above).", file=sys.stderr)
        return 1
    print("\nAll assets are available locally in vendor/, SRI hashes match, and vendor/ is fully tracked.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
