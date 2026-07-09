#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate one image via the PaperArt direct-task API and download it.

Usage: python gen_image.py "<prompt>" <out_path> [width] [height]
Reads the UAT API key from the skills .env (never printed / committed).
Falls back from explicit width/height to resolution=2K if the sized task fails.
"""
import json
import os
import subprocess
import sys
import time
import urllib.request

ENV_CANDIDATES = [
    r"C:\Users\jinchao\.claude\skills\.env",
    r"F:\Projects\As\PaperSkill\.env",
]
BACKEND = "doubao-seedream-4-0-250828"


def load_env():
    env = {}
    for path in ENV_CANDIDATES:
        if os.path.exists(path):
            with open(path, "r", encoding="utf-8") as fh:
                for line in fh:
                    line = line.strip()
                    if not line or line.startswith("#") or "=" not in line:
                        continue
                    k, v = line.split("=", 1)
                    env[k.strip()] = v.strip().strip('"').strip("'")
            break
    return env


def submit(base, key, payload):
    tmp = os.path.join(os.path.dirname(os.path.abspath(__file__)), "_payload.json")
    with open(tmp, "w", encoding="utf-8") as fh:
        json.dump(payload, fh, ensure_ascii=False)
    cmd = [
        "curl", "-sS", "-X", "POST", base + "/task/direct/image",
        "-H", "Authorization: Bearer " + key,
        "-H", "AUTH_TYPE: UAT",
        "-F", "payload=<" + tmp,
    ]
    out = subprocess.run(cmd, capture_output=True, text=True)
    try:
        os.remove(tmp)
    except OSError:
        pass
    try:
        data = json.loads(out.stdout)
        return data.get("data", {}).get("id"), out.stdout
    except Exception:
        return None, out.stdout + out.stderr


def poll(base, key, task_id, timeout=420):
    url = base + "/task/direct/result/one?task_id=" + str(task_id)
    deadline = time.time() + timeout
    while time.time() < deadline:
        req = urllib.request.Request(url)
        req.add_header("Authorization", "Bearer " + key)
        req.add_header("AUTH_TYPE", "UAT")
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                data = json.loads(resp.read().decode("utf-8"))
        except Exception as exc:
            print("poll error:", exc, flush=True)
            time.sleep(8)
            continue
        d = data.get("data", {})
        result = d.get("result", "")
        if result == "success":
            return d.get("output_path", [])
        if result == "failed":
            print("task failed:", d.get("response_txt", ""), flush=True)
            return None
        print("  ... pending", flush=True)
        time.sleep(9)
    print("timed out", flush=True)
    return None


def download(url, out_path):
    req = urllib.request.Request(url)
    with urllib.request.urlopen(req, timeout=120) as resp:
        blob = resp.read()
    os.makedirs(os.path.dirname(os.path.abspath(out_path)), exist_ok=True)
    with open(out_path, "wb") as fh:
        fh.write(blob)
    return len(blob)


def run(prompt, out_path, width=None, height=None):
    env = load_env()
    key = env.get("PAPERART_UAT_API_KEY")
    base = env.get("PAPERART_BASE_URL", "https://tc-sd.diezhi.net:8066/api/v1")
    if not key:
        print("no PAPERART_UAT_API_KEY found", flush=True)
        return 1

    attempts = []
    if width and height:
        attempts.append({"backend": BACKEND, "prompt": prompt, "width": int(width), "height": int(height)})
    attempts.append({"backend": BACKEND, "prompt": prompt, "resolution": "2K"})

    for payload in attempts:
        print("submitting:", {k: payload[k] for k in payload if k != "prompt"}, flush=True)
        task_id, raw = submit(base, key, payload)
        if not task_id:
            print("submit failed:", raw[:300], flush=True)
            continue
        print("task id:", task_id, flush=True)
        paths = poll(base, key, task_id)
        if paths:
            n = download(paths[0], out_path)
            print("saved", out_path, n, "bytes", flush=True)
            return 0
    return 2


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(64)
    w = sys.argv[3] if len(sys.argv) > 3 else None
    h = sys.argv[4] if len(sys.argv) > 4 else None
    sys.exit(run(sys.argv[1], sys.argv[2], w, h))
