"""Demo M2 — cómputo al vuelo sin Shiny.

Muestra el núcleo del paquete:
  1. campo de UTCI máximo diario para una fecha,
  2. su clasificación en categorías de estrés (distribución sobre México),
  3. el valor y la categoría en celdas de ciudades,
  4. la serie temporal horaria de una celda (nearest).

Uso:  uv run python scripts/demo_m2.py
"""

from __future__ import annotations

import datetime as dt

import numpy as np

from atlas import catalog, compute, indices

FECHA = dt.date(2022, 6, 15)
INDICE = "utci_max_diario"

CIUDADES = {
    "CDMX": (19.43, -99.13),
    "Mexicali": (32.65, -115.47),
    "Mérida": (20.97, -89.62),
}


def main() -> None:
    print("=" * 64)
    print("DEMO M2 — atlas")
    print("=" * 64)

    d0, d1 = catalog.date_bounds()
    print(f"Cubo: variables={catalog.available_vars()}  rango={d0} … {d1}")
    print(f"Índices registrados: {indices.keys()}")
    print()

    # 1) Campo del día
    campo = compute.field_for(FECHA, INDICE)
    campo = campo.load()  # materializa para el demo
    ix = indices.get(INDICE)
    print(f"[1] {ix.label} — {FECHA}")
    print(
        f"    campo {dict(campo.sizes)}  "
        f"min={float(campo.min()):.1f} {ix.units}  "
        f"media={float(campo.mean()):.1f}  "
        f"max={float(campo.max()):.1f}"
    )
    print()

    # 2) Distribución de categorías de estrés sobre el territorio
    cat = compute.classify_field(campo, INDICE).load()
    print("[2] Distribución de estrés térmico (celdas por categoría):")
    valores, conteos = np.unique(cat.values, return_counts=True)
    total = int(conteos.sum())
    for vi, n in zip(valores, conteos):
        c = ix.categories[int(vi)]
        barra = "█" * round(40 * n / total)
        print(f"    {c.label:<28} {n:>5} {barra}")
    print()

    # 3) Valor + categoría por ciudad
    print(f"[3] UTCI máximo diario por ciudad ({FECHA}):")
    for nombre, (lat, lon) in CIUDADES.items():
        clat, clon = compute.nearest_cell(lat, lon)
        val = float(campo.sel(lat=clat, lon=clon))
        c = indices.utci_category(val)
        print(f"    {nombre:<10} celda({clat:.2f},{clon:.2f})  {val:5.1f}°C  → {c.label}")
    print()

    # 4) Serie horaria en una celda
    nombre, (lat, lon) = "Mexicali", CIUDADES["Mexicali"]
    serie = compute.series_at(lat, lon).sel(time=str(FECHA)).load()
    horas = serie["time"].dt.hour.values
    i_min, i_max = int(np.argmin(serie.values)), int(np.argmax(serie.values))
    print(f"[4] Serie horaria de UTCI en {nombre} ({FECHA}, hora UTC):")
    print(
        f"    min={float(serie.min()):.1f}°C (h{int(horas[i_min])})  "
        f"max={float(serie.max()):.1f}°C (h{int(horas[i_max])})"
    )
    spark = "".join(
        "▁▂▃▄▅▆▇█"[min(7, max(0, int((v - serie.min()) / (serie.max() - serie.min() + 1e-9) * 7)))]
        for v in serie.values
    )
    print(f"    0h{spark}23h")
    print()
    print("OK — núcleo de cómputo funcionando.")


if __name__ == "__main__":
    main()
