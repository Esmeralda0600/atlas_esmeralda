"""
utci_categories.py

Categorias oficiales de estres termico UTCI (escala ECMWF, 10 clases),
mismos labels y colores usados en el proyecto atlas (indices.py), para
mantener consistencia visual entre proyectos.

El orden de esta tupla DEBE coincidir con el orden de la dimension
"category" (0-9) de los .nc stress_utci_anual_2022.nc y
stress_utci_seasonal_2022.nc.
"""

from dataclasses import dataclass


@dataclass(frozen=True)
class CategoriaUTCI:
    idx: int
    label: str
    color: str  # hex


UTCI_STRESS: tuple[CategoriaUTCI, ...] = (
    CategoriaUTCI(0, "Estrés por frío extremo", "#053061"),
    CategoriaUTCI(1, "Estrés por frío muy fuerte", "#2166ac"),
    CategoriaUTCI(2, "Estrés por frío fuerte", "#4393c3"),
    CategoriaUTCI(3, "Estrés por frío moderado", "#92c5de"),
    CategoriaUTCI(4, "Estrés por frío ligero", "#d1e5f0"),
    CategoriaUTCI(5, "Sin estrés térmico", "#d9f0d3"),
    CategoriaUTCI(6, "Estrés por calor moderado", "#fddbc7"),
    CategoriaUTCI(7, "Estrés por calor fuerte", "#f4a582"),
    CategoriaUTCI(8, "Estrés por calor muy fuerte", "#d6604d"),
    CategoriaUTCI(9, "Estrés por calor extremo", "#b2182b"),
)

ETIQUETAS_UTCI = [c.label for c in UTCI_STRESS]
COLORES_UTCI = [c.color for c in UTCI_STRESS]