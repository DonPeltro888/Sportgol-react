"""
CWV Image Optimizer — converts PNG/JPG to WebP+AVIF.
Maintains the original; produces siblings .webp + .avif.
"""
import logging
from pathlib import Path
from typing import Any, Dict, List

import pillow_avif  # noqa: F401  registers AVIF plugin
from PIL import Image

logger = logging.getLogger(__name__)


def convert_one(src: Path, *, webp_quality: int = 82, avif_quality: int = 60) -> Dict[str, Any]:
    if not src.exists():
        return {"src": str(src), "ok": False, "error": "not_found"}
    if src.suffix.lower() not in (".png", ".jpg", ".jpeg"):
        return {"src": str(src), "ok": False, "error": f"unsupported_{src.suffix}"}
    out: Dict[str, Any] = {"src": str(src), "ok": True, "generated": [], "skipped": []}
    src_mtime = src.stat().st_mtime
    try:
        img = Image.open(src)
        if img.mode == "RGBA" and src.suffix.lower() in (".jpg", ".jpeg"):
            img = img.convert("RGB")
        webp = src.with_suffix(".webp")
        if webp.exists() and webp.stat().st_mtime >= src_mtime:
            out["skipped"].append("webp")
        else:
            img.save(webp, "WEBP", quality=webp_quality, method=6)
            out["generated"].append({"format": "webp", "path": str(webp), "size": webp.stat().st_size})
        avif = src.with_suffix(".avif")
        if avif.exists() and avif.stat().st_mtime >= src_mtime:
            out["skipped"].append("avif")
        else:
            img.save(avif, "AVIF", quality=avif_quality)
            out["generated"].append({"format": "avif", "path": str(avif), "size": avif.stat().st_size})
        out["original_size"] = src.stat().st_size
    except Exception as e:
        return {"src": str(src), "ok": False, "error": str(e)[:200]}
    return out


def batch_convert(folder: str = "/app/backend/uploads/seo") -> Dict[str, Any]:
    p = Path(folder)
    if not p.exists():
        return {"ok": False, "error": "folder_not_found", "folder": folder}
    targets: List[Path] = []
    for ext in ("*.png", "*.jpg", "*.jpeg"):
        targets.extend(p.glob(ext))
    results = []
    total_orig = total_webp = total_avif = success = 0
    for f in targets:
        r = convert_one(f)
        results.append(r)
        if r.get("ok"):
            success += 1
            total_orig += r.get("original_size", 0)
            for g in r.get("generated", []):
                if g["format"] == "webp":
                    total_webp += g["size"]
                elif g["format"] == "avif":
                    total_avif += g["size"]
    saving_webp = round((1 - total_webp / total_orig) * 100, 1) if total_orig else 0
    saving_avif = round((1 - total_avif / total_orig) * 100, 1) if total_orig else 0
    return {
        "ok": True, "folder": folder, "total_files": len(targets),
        "success": success, "failed": len(targets) - success,
        "bytes_original": total_orig, "bytes_webp": total_webp, "bytes_avif": total_avif,
        "saving_webp_pct": saving_webp, "saving_avif_pct": saving_avif,
        "details": results[:50],
    }
