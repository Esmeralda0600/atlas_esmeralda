"""Ingesta NetCDF (ERA5-HEAT) -> cubo Zarr.

Convierte los NetCDF horarios de un ``(tipo, año)`` en el store Zarr del proyecto,
agregando por la dimensión ``time``. Es **idempotente**: re-ingerir un año ya
presente no duplica nada. Valida solapamientos parciales y los rechaza con un
mensaje claro en vez de corromper el cubo.

Diseño abierto a multi-año / multi-tipo:
- ``tipo`` (p. ej. ``"UTCI"``) selecciona la carpeta de fuente y nombra la variable.
- Años distintos se concatenan en orden temporal vía *append*.
"""

from __future__ import annotations

import glob
from pathlib import Path

import numpy as np
import xarray as xr

from atlas import config

# Pasos de tiempo por chunk del cubo. 24 = un día -> el campo diario (caso de uso
# principal) lee exactamente un chunk. El cubo completo es pequeño (~360 MB/año),
# así que la serie temporal por celda sigue siendo barata.
TIME_CHUNK = 24

# Umbral para detectar Kelvin: UTCI en °C nunca se acerca a 100; en K ronda 230-330.
_KELVIN_THRESHOLD = 100.0
_KELVIN_TO_CELSIUS = 273.15


def _var_name(tipo: str) -> str:
    """Nombre de la variable dentro del cubo para un tipo dado."""
    return tipo.lower()


def _source_files(tipo: str, anio: int) -> list[str]:
    """NetCDF fuente ordenados para un (tipo, año)."""
    pattern = str(config.raw_dir(tipo, anio) / "*.nc")
    files = sorted(glob.glob(pattern))
    if not files:
        raise FileNotFoundError(
            f"No hay NetCDF en {config.raw_dir(tipo, anio)} (patrón {pattern})."
        )
    return files


def _normalize(ds: xr.Dataset, tipo: str) -> xr.Dataset:
    """Normaliza un dataset crudo: variable renombrada, °C, lat ascendente, orden temporal."""
    if "utci" not in ds:
        raise KeyError(f"Variable 'utci' ausente; variables: {list(ds.data_vars)}")

    da = ds["utci"]

    # Kelvin -> °C si hace falta (el attr units viene vacío en ERA5-HEAT).
    if float(da.max()) > _KELVIN_THRESHOLD:
        da = da - _KELVIN_TO_CELSIUS
    da.attrs["units"] = "°C"
    da.attrs["long_name"] = "Universal Thermal Climate Index"

    out = da.to_dataset(name=_var_name(tipo))
    # lat ascendente y tiempo ordenado para escritura/append predecibles.
    out = out.sortby("lat").sortby("time")
    return out


def open_source_year(tipo: str, anio: int) -> xr.Dataset:
    """Abre y normaliza todos los NetCDF de un (tipo, año) como un dataset perezoso."""
    files = _source_files(tipo, anio)
    ds = xr.open_mfdataset(
        files,
        combine="nested",
        concat_dim="time",
        parallel=False,
    )
    return _normalize(ds, tipo)


def _existing_times(store: Path) -> np.ndarray | None:
    """Tiempos ya presentes en el cubo, o None si el store no existe."""
    if not store.exists():
        return None
    with xr.open_zarr(store, consolidated=False) as cube:
        return cube["time"].values


def ingest_year(
    tipo: str,
    anio: int,
    store: Path | None = None,
) -> dict:
    """Ingiere un (tipo, año) en el cubo Zarr.

    - Crea el store si no existe.
    - Si todos los tiempos del año ya están -> no-op (idempotente).
    - Si todos los tiempos nuevos son posteriores al cubo -> *append*.
    - Solapamiento parcial -> error (no se intenta reescribir regiones en v1).

    Devuelve un resumen con lo que ocurrió.
    """
    store = Path(store) if store is not None else config.ZARR_STORE
    var = _var_name(tipo)

    ds = open_source_year(tipo, anio)
    ds = ds.chunk({"time": TIME_CHUNK, "lat": -1, "lon": -1})
    new_times = ds["time"].values
    n_new = int(new_times.size)

    existing = _existing_times(store)

    # Store nuevo: escritura completa.
    if existing is None:
        ds.to_zarr(store, mode="w", consolidated=False)
        return {
            "accion": "creado",
            "tipo": tipo,
            "anio": anio,
            "pasos_escritos": n_new,
            "pasos_totales": n_new,
            "store": str(store),
        }

    existing_set = set(existing.astype("datetime64[ns]").tolist())
    new_set = set(new_times.astype("datetime64[ns]").tolist())

    # Idempotencia: todo ya presente -> no-op.
    if new_set <= existing_set:
        return {
            "accion": "sin_cambios",
            "tipo": tipo,
            "anio": anio,
            "pasos_escritos": 0,
            "pasos_totales": int(existing.size),
            "store": str(store),
        }

    overlap = new_set & existing_set
    # Solapamiento parcial: ni disjunto ni subconjunto -> rechazar.
    if overlap:
        raise ValueError(
            f"Solapamiento temporal parcial para {tipo} {anio}: "
            f"{len(overlap)} de {n_new} pasos ya existen. "
            "La reescritura por regiones no está soportada en v1; "
            "elimina el store o ingiere un rango disjunto."
        )

    # Disjunto: solo se permite append si lo nuevo es posterior a lo existente.
    if new_times.min() <= existing.max():
        raise ValueError(
            f"Los tiempos de {tipo} {anio} son anteriores/intercalados respecto al "
            "cubo; v1 solo agrega rangos posteriores (append). Ingiere los años en orden."
        )

    ds.to_zarr(store, mode="a", append_dim="time", consolidated=False)
    return {
        "accion": "agregado",
        "tipo": tipo,
        "anio": anio,
        "pasos_escritos": n_new,
        "pasos_totales": int(existing.size) + n_new,
        "store": str(store),
    }
