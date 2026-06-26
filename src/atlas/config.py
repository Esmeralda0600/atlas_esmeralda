"""Configuración central: rutas, bounding box de México y ubicación del store.

Un único lugar para resolver dónde viven los datos. La raíz del repo se deriva
relativa a este archivo, pero puede sobreescribirse con la variable de entorno
``ATLAS_DATA_DIR`` (útil cuando el paquete se instale vía pip y los datos vivan
fuera del árbol de fuentes).
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

# Raíz del repositorio: src/atlas/config.py -> repo/
REPO_ROOT = Path(__file__).resolve().parents[2]

# Directorio de datos (no versionado). Sobreescribible por entorno.
DATA_DIR = Path(os.environ.get("ATLAS_DATA_DIR", REPO_ROOT / "data"))

# NetCDF fuente, organizados por tipo y año: data/raw/<TIPO>/<AÑO>/*.nc
RAW_DIR = DATA_DIR / "raw"

# Cubo Zarr construido por la ingesta.
ZARR_STORE = DATA_DIR / "utci_mexico.zarr"


@dataclass(frozen=True)
class BBox:
    """Bounding box geográfico (grados decimales, EPSG:4326)."""

    lon_min: float
    lon_max: float
    lat_min: float
    lat_max: float


# México continental + mar adyacente, tal como viene recortado el ERA5-HEAT.
MEXICO_BBOX = BBox(lon_min=-119.0, lon_max=-86.0, lat_min=14.0, lat_max=33.0)

# Resolución del grid ERA5-HEAT.
GRID_RES_DEG = 0.25


def raw_dir(tipo: str, anio: int) -> Path:
    """Directorio de NetCDF fuente para un (tipo, año)."""
    return RAW_DIR / tipo / str(anio)
