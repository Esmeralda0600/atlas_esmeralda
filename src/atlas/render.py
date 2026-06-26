"""Rasterización de un campo 2D a PNG para superponer en el mapa (ImageOverlay).

Colorea por categorías de estrés (ListedColormap + BoundaryNorm) y devuelve un
*data URI* PNG listo para ``ipyleaflet.ImageOverlay``, junto con los ``bounds``
geográficos (extendidos media celda para alinear con los bordes, no los centros).
"""

from __future__ import annotations

import base64
import datetime as dt
import io

import numpy as np
import xarray as xr
from matplotlib.colors import BoundaryNorm, ListedColormap
from PIL import Image

from atlas import compute, config, indices
from atlas.indices import StressCategory


def _cmap_norm(categories: tuple[StressCategory, ...]) -> tuple[ListedColormap, BoundaryNorm]:
    """ListedColormap + BoundaryNorm a partir de las categorías de estrés."""
    cmap = ListedColormap([c.color for c in categories])
    inner = [c.hi for c in categories[:-1]]  # cortes internos finitos
    boundaries = [-1e9, *inner, 1e9]
    norm = BoundaryNorm(boundaries, cmap.N)
    return cmap, norm


def field_to_rgba(
    field: xr.DataArray,
    categories: tuple[StressCategory, ...],
) -> np.ndarray:
    """Campo (lat asc, lon) -> arreglo RGBA uint8 con norte arriba y NaN transparente."""
    cmap, norm = _cmap_norm(categories)
    data = np.asarray(field.values, dtype="float64")
    rgba = (cmap(norm(data)) * 255).astype(np.uint8)
    rgba[np.isnan(data), 3] = 0  # celdas sin dato -> transparentes
    # lat viene ascendente (sur->norte); una imagen tiene la fila 0 arriba (norte).
    return np.flipud(rgba)


def field_to_data_uri(
    field: xr.DataArray,
    categories: tuple[StressCategory, ...],
) -> str:
    """Campo 2D -> data URI PNG base64."""
    rgba = field_to_rgba(field, categories)
    buf = io.BytesIO()
    Image.fromarray(rgba, mode="RGBA").save(buf, format="PNG")
    return "data:image/png;base64," + base64.b64encode(buf.getvalue()).decode("ascii")


def field_bounds(field: xr.DataArray) -> tuple[tuple[float, float], tuple[float, float]]:
    """Bounds ((sur, oeste), (norte, este)) extendidos media celda."""
    h = config.GRID_RES_DEG / 2.0
    return (
        (float(field["lat"].min()) - h, float(field["lon"].min()) - h),
        (float(field["lat"].max()) + h, float(field["lon"].max()) + h),
    )


def overlay_for(
    fecha: dt.date | str,
    index_key: str,
) -> tuple[str, tuple[tuple[float, float], tuple[float, float]]]:
    """Devuelve (data_uri_png, bounds) para el campo del índice en una fecha."""
    ix = indices.get(index_key)
    if ix.categories is None:
        raise ValueError(f"El índice '{index_key}' no define categorías para colorear.")
    field = compute.field_for(fecha, index_key).load()
    return field_to_data_uri(field, ix.categories), field_bounds(field)


def legend_items(index_key: str) -> list[tuple[str, str]]:
    """Lista [(etiqueta, color hex)] de las categorías del índice, para la leyenda."""
    ix = indices.get(index_key)
    if ix.categories is None:
        return []
    return [(c.label, c.color) for c in ix.categories]
