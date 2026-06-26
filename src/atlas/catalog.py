"""Acceso perezoso al cubo Zarr y descubrimiento de lo disponible.

Una única puerta de entrada al store: el resto del paquete (y la app) abren el
cubo desde aquí, nunca con rutas sueltas.
"""

from __future__ import annotations

import datetime as dt
import functools
from pathlib import Path

import pandas as pd
import xarray as xr

from atlas import config


@functools.lru_cache(maxsize=2)
def open_cube(store: str | None = None) -> xr.Dataset:
    """Abre el cubo Zarr de forma perezosa (cacheado por ruta).

    ``store`` es una ruta opcional; por defecto ``config.ZARR_STORE``.
    """
    path = Path(store) if store else config.ZARR_STORE
    if not path.exists():
        raise FileNotFoundError(
            f"No existe el cubo en {path}. Córrelo con: atlas-ingest <tipo> <año>."
        )
    return xr.open_zarr(path, consolidated=False)


def available_vars(cube: xr.Dataset | None = None) -> list[str]:
    """Variables presentes en el cubo."""
    cube = cube if cube is not None else open_cube()
    return list(cube.data_vars)


def available_dates(cube: xr.Dataset | None = None) -> list[dt.date]:
    """Días con datos en el cubo (fechas únicas, ordenadas)."""
    cube = cube if cube is not None else open_cube()
    days = pd.to_datetime(cube["time"].values).normalize().unique()
    return [d.date() for d in sorted(days)]


def date_bounds(cube: xr.Dataset | None = None) -> tuple[dt.date, dt.date]:
    """Primera y última fecha disponibles."""
    fechas = available_dates(cube)
    return fechas[0], fechas[-1]
