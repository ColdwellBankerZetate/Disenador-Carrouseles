#!/usr/bin/env python3
"""Ajuste suave de iluminación y export 4:5 (1080x1350) para carruseles de Instagram.

Solo toca la luz: balance de blancos, exposición/brillo y contraste.
No agrega ni quita objetos y no deforma: para llegar a 4:5 recorta (centrado
o con el ancla que elijas), nunca estira.

Uso:
    python scripts/ajuste_fotos.py ENTRADA SALIDA [--orden lista.txt] [--fuerza 0.5]

- ENTRADA: carpeta con las fotos elegidas.
- SALIDA: carpeta donde se escriben 01.jpg, 02.jpg, ...
- --orden: archivo de texto con un nombre de foto por línea, en el orden del
  carrusel (la primera es la portada). Opcionalmente, "nombre.jpg|top" o "|bottom"
  para anclar el recorte. Sin --orden se usa el orden alfabético.
- --fuerza: de 0 a 1, cuánto de la corrección automática se aplica (por defecto 0.5:
  suave).
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import numpy as np
from PIL import Image, ImageOps

ANCHO, ALTO = 1080, 1350
EXTS = {".jpg", ".jpeg", ".png", ".tif", ".tiff", ".webp"}


def balance_blancos(arr: np.ndarray, fuerza: float) -> np.ndarray:
    """Gray-world suave: acerca las medias de R, G y B entre sí."""
    medias = arr.reshape(-1, 3).mean(axis=0)
    gris = medias.mean()
    ganancia = gris / np.maximum(medias, 1e-3)
    ganancia = np.clip(ganancia, 0.85, 1.15)  # nunca un cambio de color fuerte
    ganancia = 1 + (ganancia - 1) * fuerza
    return arr * ganancia


def exposicion(arr: np.ndarray, fuerza: float, objetivo: float = 0.46) -> np.ndarray:
    """Corrección gamma para llevar la luminancia media hacia el objetivo."""
    lum = (0.2126 * arr[..., 0] + 0.7152 * arr[..., 1] + 0.0722 * arr[..., 2]).mean()
    lum = float(np.clip(lum, 0.05, 0.95))
    gamma = np.log(objetivo) / np.log(lum)
    gamma = float(np.clip(gamma, 0.7, 1.4))
    gamma = 1 + (gamma - 1) * fuerza
    return np.power(np.clip(arr, 0, 1), gamma)


def contraste(arr: np.ndarray, fuerza: float) -> np.ndarray:
    """Estira los niveles entre los percentiles 0.5 y 99.5, de forma suave."""
    lo, hi = np.percentile(arr, [0.5, 99.5])
    if hi - lo < 1e-3:
        return arr
    estirado = (arr - lo) / (hi - lo)
    return arr + (estirado - arr) * fuerza * 0.6


def ajustar(img: Image.Image, fuerza: float) -> Image.Image:
    img = ImageOps.exif_transpose(img).convert("RGB")
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = balance_blancos(arr, fuerza)
    arr = exposicion(arr, fuerza)
    arr = contraste(arr, fuerza)
    arr = np.clip(arr * 255.0 + 0.5, 0, 255).astype(np.uint8)
    return Image.fromarray(arr)


def recortar_4x5(img: Image.Image, ancla: str = "center") -> Image.Image:
    """Recorta a 4:5 sin deformar y escala a 1080x1350."""
    centrado = {"top": (0.5, 0.0), "bottom": (0.5, 1.0)}.get(ancla, (0.5, 0.5))
    return ImageOps.fit(img, (ANCHO, ALTO), method=Image.Resampling.LANCZOS, centering=centrado)


def leer_orden(entrada: Path, orden: Path | None) -> list[tuple[Path, str]]:
    if orden is None:
        fotos = sorted(p for p in entrada.iterdir() if p.suffix.lower() in EXTS)
        return [(p, "center") for p in fotos]
    items = []
    for linea in orden.read_text(encoding="utf-8").splitlines():
        linea = linea.strip()
        if not linea or linea.startswith("#"):
            continue
        nombre, _, ancla = linea.partition("|")
        ruta = entrada / nombre.strip()
        if not ruta.exists():
            sys.exit(f"No existe: {ruta}")
        items.append((ruta, ancla.strip() or "center"))
    return items


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("entrada", type=Path)
    ap.add_argument("salida", type=Path)
    ap.add_argument("--orden", type=Path)
    ap.add_argument("--fuerza", type=float, default=0.5)
    args = ap.parse_args()

    fuerza = float(np.clip(args.fuerza, 0, 1))
    items = leer_orden(args.entrada, args.orden)
    if not items:
        sys.exit("No hay fotos para procesar.")
    if not 10 <= len(items) <= 11:
        print(f"Aviso: hay {len(items)} fotos; para un carrusel de propiedad se esperan 10 u 11.")

    args.salida.mkdir(parents=True, exist_ok=True)
    for i, (ruta, ancla) in enumerate(items, start=1):
        with Image.open(ruta) as img:
            final = recortar_4x5(ajustar(img, fuerza), ancla)
        destino = args.salida / f"{i:02d}.jpg"
        final.save(destino, "JPEG", quality=92, optimize=True, progressive=True, subsampling=0)
        print(f"{destino.name} <- {ruta.name} ({ancla})")


if __name__ == "__main__":
    main()
