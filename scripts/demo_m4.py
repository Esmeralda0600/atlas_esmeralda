"""Demo M4 — la serie temporal que produce un clic en el mapa.

Llama a la MISMA función que usa la app (`atlas.plots.hourly_series`) para la
celda más cercana a un punto, y guarda la figura.

Uso:  uv run python scripts/demo_m4.py [salida.png]
"""

from __future__ import annotations

import datetime as dt
import sys

from atlas import plots

FECHA = dt.date(2022, 6, 15)
# Punto pulsado (simula un clic): Mexicali, desierto del noroeste.
LAT, LON = 32.65, -115.47


def main(salida: str) -> None:
    fig = plots.hourly_series(LAT, LON, FECHA)
    fig.savefig(salida, dpi=120, bbox_inches="tight")
    print(f"Imagen guardada en: {salida}")


if __name__ == "__main__":
    out = sys.argv[1] if len(sys.argv) > 1 else "demo_m4.png"
    main(out)
