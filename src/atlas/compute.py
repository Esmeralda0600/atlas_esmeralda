"""Cómputo al vuelo sobre el cubo: campo 2D por fecha/índice y serie por celda.

Capa fina sobre ``catalog`` + ``indices``. No sabe nada de Shiny: la app la
consume, pero también es usable desde un script o notebook.
"""

from __future__ import annotations

import datetime as dt

import xarray as xr

from atlas import catalog, indices


def field_for(
    fecha: dt.date | str,
    index_key: str,
    cube: xr.Dataset | None = None,
) -> xr.DataArray:
    """Campo 2D (lat, lon) del índice ``index_key`` para un día.

    Selecciona las horas de ese día del cubo y aplica el ``aggregate`` del índice.
    """
    ix = indices.get(index_key)
    cube = cube if cube is not None else catalog.open_cube()
    dia = cube[ix.var].sel(time=str(fecha))  # indexado parcial: todas las horas del día
    if dia.sizes.get("time", 0) == 0:
        raise KeyError(f"No hay datos para {fecha} en el cubo.")
    campo = ix.aggregate(dia)
    campo.attrs["units"] = ix.units
    campo.attrs["indice"] = ix.key
    campo.attrs["fecha"] = str(fecha)
    return campo


def classify_field(field: xr.DataArray, index_key: str) -> xr.DataArray:
    """Aplica la clasificación de estrés del índice a un campo ya computado."""
    ix = indices.get(index_key)
    if ix.classify is None:
        raise ValueError(f"El índice '{index_key}' no define clasificación.")
    return ix.classify(field)


def series_at(
    lat: float,
    lon: float,
    var: str = "utci",
    cube: xr.Dataset | None = None,
) -> xr.DataArray:
    """Serie temporal horaria de ``var`` en la celda más cercana a (lat, lon)."""
    cube = cube if cube is not None else catalog.open_cube()
    serie = cube[var].sel(lat=lat, lon=lon, method="nearest")
    return serie


def nearest_cell(
    lat: float,
    lon: float,
    cube: xr.Dataset | None = None,
) -> tuple[float, float]:
    """Coordenadas (lat, lon) reales de la celda más cercana al punto pedido."""
    cube = cube if cube is not None else catalog.open_cube()
    sel = cube[["lat", "lon"]].sel(lat=lat, lon=lon, method="nearest")
    return float(sel["lat"]), float(sel["lon"])
