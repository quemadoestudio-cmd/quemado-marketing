#!/usr/bin/env python3
"""Genera imágenes para Quemado Estudio con Gemini 2.5 Flash Image (con reintentos)."""
import base64, json, os, time, urllib.request, urllib.error

KEY = os.environ["GEMINI_KEY"]
MODEL = "gemini-2.5-flash-image"
URL = f"https://generativelanguage.googleapis.com/v1beta/models/{MODEL}:generateContent?key={KEY}"

STYLE = ("dark moody premium commercial photography, deep blacks, high contrast, "
         "cinematic lighting, minimal editorial, 16:9 widescreen, no text, no words")

IMAGES = {
    "hero-rock": "A single piece of black volcanic obsidian rock floating in pure black void, dramatic rim lighting, glossy burnt texture, centered product photography, " + STYLE,
    "content": "Behind the scenes of a high-end video shoot, cinema camera and softbox lights in a dark studio, moody atmosphere, " + STYLE,
    "branding": "Luxury black perfume bottle on rough volcanic black rocks, minimalist premium product shot, soft spotlight, " + STYLE,
    "social": "Modern smartphone floating against black background showing abstract glowing social media grid, sleek tech product photography, " + STYLE,
    "web": "Sleek laptop on dark surface displaying a minimal dark website, glowing screen, premium tech photography, low key lighting, " + STYLE,
    "graphic": "Premium black product packaging and printed brochures flat lay on dark concrete, embossed minimalist design, studio lighting, " + STYLE,
}

def gen(name, prompt, attempt=1):
    out = f"images/{name}.png"
    if os.path.exists(out):
        print(f"SKIP {out} (ya existe)"); return True
    body = json.dumps({"contents": [{"parts": [{"text": prompt}]}]}).encode()
    req = urllib.request.Request(URL, data=body, headers={"Content-Type": "application/json"})
    try:
        data = json.load(urllib.request.urlopen(req, timeout=180))
        for p in data["candidates"][0]["content"]["parts"]:
            if "inlineData" in p:
                with open(out, "wb") as f:
                    f.write(base64.b64decode(p["inlineData"]["data"]))
                print(f"OK  {out}"); return True
        print(f"ERR {name}: sin imagen"); return False
    except urllib.error.HTTPError as e:
        if e.code == 429 and attempt <= 6:
            wait = 40 * attempt
            print(f"429 {name}: espero {wait}s (intento {attempt})")
            time.sleep(wait)
            return gen(name, prompt, attempt + 1)
        print(f"ERR {name}: {e.code} {e.read().decode()[:160]}"); return False

for n, p in IMAGES.items():
    gen(n, p)
    time.sleep(8)
