import io, os, re, sys, zipfile, urllib.request
from pathlib import Path
from PIL import Image, ImageOps

BASE = "https://cdn.tse.jus.br/estatistica/sead/eleicoes/eleicoes2026/fotos"
DATASET = "https://dadosabertos.tse.jus.br/dataset/candidatos-2026"
OUT = Path(__file__).resolve().parent / "photos"
OUT.mkdir(parents=True, exist_ok=True)
HEADERS = {
    "User-Agent": "Mozilla/5.0 (Colinha Eleicoes 2026; dados publicos)",
    "Accept": "application/zip,*/*",
    "Referer": DATASET,
}

def download(url):
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=240) as r:
        data = r.read()
    if len(data) < 1000:
        raise RuntimeError(f"download pequeno: {url} ({len(data)} bytes)")
    return data

def candidate_id(name):
    base = os.path.basename(name)
    nums = re.findall(r"\d{10,}", base)
    return nums[0] if nums else None

def save_thumb(raw, cid):
    try:
        with Image.open(io.BytesIO(raw)) as im:
            im = ImageOps.exif_transpose(im).convert("RGB")
            im.thumbnail((420, 520), Image.Resampling.LANCZOS)
            dest = OUT / f"{cid}.jpg"
            im.save(dest, "JPEG", quality=84, optimize=True, progressive=True)
            return True
    except Exception as e:
        print("skip", cid, repr(e))
        return False

def process(uf):
    url = f"{BASE}/foto_cand2026_{uf}_div.zip"
    print("downloading", url, flush=True)
    data = download(url)
    print("downloaded", uf, len(data), "bytes", flush=True)
    count = 0
    with zipfile.ZipFile(io.BytesIO(data)) as z:
        for info in z.infolist():
            if info.is_dir():
                continue
            cid = candidate_id(info.filename)
            if not cid:
                continue
            if save_thumb(z.read(info), cid):
                count += 1
    print("saved", uf, count, "photos", flush=True)
    return count

total = 0
for uf in ("MG", "BR"):
    try:
        total += process(uf)
    except Exception as e:
        print("ERROR", uf, repr(e), file=sys.stderr)
        if uf == "MG":
            raise

# The fixed candidate must always be present.
fixed = OUT / "130002535321.jpg"
if not fixed.exists() or fixed.stat().st_size < 1000:
    raise SystemExit("foto oficial da Ana Paula nao foi gerada")

print("TOTAL", total)
print("FILES", len(list(OUT.glob("*.jpg"))))
