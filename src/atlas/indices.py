"""Registro de índices térmicos *pluggable* — el diferenciador del proyecto.

Un **índice** define cómo reducir el cubo horario de un día a un campo 2D
(``aggregate``) y, opcionalmente, cómo clasificar ese campo en categorías de
estrés. La UI se construye a partir del registro: agregar un índice nuevo
(p. ej. IMAC o grados-hora) es registrar un ``Index`` más, sin tocar la app.

    register(Index(key=..., label=..., aggregate=..., ...))
"""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field

import numpy as np
import xarray as xr


# --------------------------------------------------------------------------- #
# Categorías de estrés térmico
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class StressCategory:
    """Una clase de estrés térmico con su rango [lo, hi) en °C y color."""

    idx: int
    label: str
    lo: float  # límite inferior inclusivo (°C)
    hi: float  # límite superior exclusivo (°C)
    color: str  # hex para el mapa/leyenda


# Escala UTCI estándar de ECMWF (10 clases), etiquetas en español, paleta azul→rojo.
UTCI_STRESS: tuple[StressCategory, ...] = (
    StressCategory(0, "Estrés por frío extremo", -np.inf, -40, "#053061"),
    StressCategory(1, "Estrés por frío muy fuerte", -40, -27, "#2166ac"),
    StressCategory(2, "Estrés por frío fuerte", -27, -13, "#4393c3"),
    StressCategory(3, "Estrés por frío moderado", -13, 0, "#92c5de"),
    StressCategory(4, "Estrés por frío ligero", 0, 9, "#d1e5f0"),
    StressCategory(5, "Sin estrés térmico", 9, 26, "#d9f0d3"),
    StressCategory(6, "Estrés por calor moderado", 26, 32, "#fddbc7"),
    StressCategory(7, "Estrés por calor fuerte", 32, 38, "#f4a582"),
    StressCategory(8, "Estrés por calor muy fuerte", 38, 46, "#d6604d"),
    StressCategory(9, "Estrés por calor extremo", 46, np.inf, "#b2182b"),
)

# Cortes internos para np.digitize (los hi de todas menos la última).
_UTCI_BINS = [c.hi for c in UTCI_STRESS[:-1]]


def classify_utci(field: xr.DataArray) -> xr.DataArray:
    """Mapea un campo de UTCI (°C) a índices de categoría 0..9 (mismo shape)."""
    idx = xr.apply_ufunc(np.digitize, field, kwargs={"bins": _UTCI_BINS})
    idx.attrs["categorias"] = "UTCI_STRESS"
    return idx.rename("categoria_estres")


def utci_category(value: float) -> StressCategory:
    """Categoría de estrés para un valor escalar de UTCI (°C)."""
    return UTCI_STRESS[int(np.digitize(value, _UTCI_BINS))]


# --------------------------------------------------------------------------- #
# Registro de índices
# --------------------------------------------------------------------------- #
@dataclass(frozen=True)
class Index:
    """Un índice registrable.

    ``aggregate`` recibe el cubo horario **de un día** (dims time, lat, lon) y
    devuelve el campo 2D (lat, lon). ``categories`` y ``classify`` son opcionales.
    """

    key: str
    label: str
    units: str
    var: str
    aggregate: Callable[[xr.DataArray], xr.DataArray]
    categories: tuple[StressCategory, ...] | None = None
    classify: Callable[[xr.DataArray], xr.DataArray] | None = None


REGISTRY: dict[str, Index] = {}


def register(index: Index) -> Index:
    """Registra un índice (sobrescribe si la clave ya existe)."""
    REGISTRY[index.key] = index
    return index


def get(key: str) -> Index:
    if key not in REGISTRY:
        raise KeyError(f"Índice '{key}' no registrado. Disponibles: {list(REGISTRY)}")
    return REGISTRY[key]


def keys() -> list[str]:
    return list(REGISTRY)


def labels() -> dict[str, str]:
    """Mapa {label legible -> key} para poblar selectores de la UI."""
    return {ix.label: k for k, ix in REGISTRY.items()}


# --------------------------------------------------------------------------- #
# Índices de v1
# --------------------------------------------------------------------------- #
register(
    Index(
        key="utci_max_diario",
        label="UTCI máximo diario",
        units="°C",
        var="utci",
        aggregate=lambda da: da.max("time", keep_attrs=True),
        categories=UTCI_STRESS,
        classify=classify_utci,
    )
)
