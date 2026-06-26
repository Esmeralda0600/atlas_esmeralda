"""Demo M3 — prueba visual del campo que pinta el mapa.

Usa el MISMO colormap/categorías que ``atlas.render`` (el que alimenta el
ImageOverlay de la app) y guarda una imagen con el campo de UTCI máximo diario
sobre México, la leyenda de estrés y algunas ciudades de referencia.

Uso:  uv run python scripts/demo_m3.py [salida.png]
"""

from __future__ import annotations

import datetime as dt
import sys

import matplotlib

matplotlib.use("Agg")
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt

from atlas import compute, config, indices
from atlas.render import _cmap_norm

FECHA = dt.date(2022, 6, 15)
INDICE = "utci_max_diario"
CIUDADES = {
    "CDMX": (19.43, -99.13),
    "Mexicali": (32.65, -115.47),
    "Mérida": (20.97, -89.62),
    "Monterrey": (25.69, -100.32),
}


def main(salida: str) -> None:
    ix = indices.get(INDICE)
    field = compute.field_for(FECHA, INDICE).load()
    cmap, norm = _cmap_norm(ix.categories)
    bb = config.MEXICO_BBOX

    fig, ax = plt.subplots(figsize=(10, 7))
    ax.pcolormesh(field["lon"], field["lat"], field.values, cmap=cmap, norm=norm, shading="auto")
    ax.set_aspect("equal")
    ax.set_xlim(bb.lon_min, bb.lon_max)
    ax.set_ylim(bb.lat_min, bb.lat_max)
    ax.set_xlabel("lon")
    ax.set_ylabel("lat")
    ax.set_title(f"{ix.label} — {FECHA}  (México, ERA5-HEAT)")

    for nombre, (lat, lon) in CIUDADES.items():
        ax.plot(lon, lat, "o", color="black", ms=4)
        ax.annotate(nombre, (lon, lat), textcoords="offset points", xytext=(4, 3), fontsize=8)

    parches = [mpatches.Patch(color=c.color, label=c.label) for c in ix.categories]
    ax.legend(handles=parches, loc="center left", bbox_to_anchor=(1.01, 0.5),
              fontsize=8, title="Estrés térmico (UTCI)", title_fontsize=9)

    fig.tight_layout()
    fig.savefig(salida, dpi=110, bbox_inches="tight")
    print(f"Imagen guardada en: {salida}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "demo_m3.png"
    main(out)
