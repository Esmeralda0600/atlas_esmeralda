"""Figuras de serie temporal para una celda (consumidas por la app y los demos).

Mantiene el ploteo fuera de la capa Shiny: ``components.servers`` solo llama a
``hourly_series(...)`` y devuelve la figura desde ``@render.plot``.
"""

from __future__ import annotations

import datetime as dt

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from atlas import compute, indices
from atlas.indices import UTCI_STRESS


def _shade_categories(ax, ymin: float, ymax: float) -> None:
    """Pinta bandas horizontales tenues con los colores de las categorías de estrés."""
    for c in UTCI_STRESS:
        lo = max(c.lo, ymin)
        hi = min(c.hi, ymax)
        if lo < hi:
            ax.axhspan(lo, hi, color=c.color, alpha=0.18, zorder=0)


def hourly_series(
    lat: float,
    lon: float,
    fecha: dt.date | str,
    var: str = "utci",
) -> plt.Figure:
    """Figura de la serie horaria de ``var`` en la celda más cercana, para un día."""
    serie: xr.DataArray = compute.series_at(lat, lon, var).sel(time=str(fecha)).load()
    clat, clon = compute.nearest_cell(lat, lon)
    horas = serie["time"].dt.hour.values
    vals = serie.values

    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ymin, ymax = float(np.min(vals)) - 2, float(np.max(vals)) + 2
    _shade_categories(ax, ymin, ymax)
    ax.plot(horas, vals, marker="o", ms=3, color="#222", zorder=3)

    i_max = int(np.argmax(vals))
    vmax = float(vals[i_max])
    cat = indices.utci_category(vmax)
    ax.annotate(
        f"máx {vmax:.1f}°C\n{cat.label}",
        (horas[i_max], vmax),
        textcoords="offset points",
        xytext=(6, -4),
        fontsize=8,
    )

    ax.set_xlim(0, 23)
    ax.set_ylim(ymin, ymax)
    ax.set_xlabel("hora (UTC)")
    ax.set_ylabel("UTCI (°C)")
    ax.set_title(f"UTCI horario · celda ({clat:.2f}, {clon:.2f}) · {fecha}", fontsize=9)
    fig.tight_layout()
    return fig


def placeholder(mensaje: str) -> plt.Figure:
    """Figura vacía con un mensaje (estado inicial antes del primer clic)."""
    fig, ax = plt.subplots(figsize=(5.2, 3.0))
    ax.text(0.5, 0.5, mensaje, ha="center", va="center", fontsize=11, color="#666")
    ax.axis("off")
    fig.tight_layout()
    return fig
