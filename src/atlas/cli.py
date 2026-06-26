"""Entry points de consola del paquete atlas."""

import argparse

from atlas import ingest as _ingest


def ingest() -> None:
    """Comando ``atlas-ingest``: NetCDF -> Zarr para un (tipo, año)."""
    parser = argparse.ArgumentParser(
        prog="atlas-ingest",
        description="Ingiere NetCDF de ERA5-HEAT a un cubo Zarr (append por tiempo).",
    )
    parser.add_argument("tipo", help="Tipo/variable, p. ej. UTCI")
    parser.add_argument("anio", type=int, help="Año a ingerir, p. ej. 2022")
    args = parser.parse_args()

    resumen = _ingest.ingest_year(args.tipo, args.anio)

    print(f"[{resumen['accion']}] {resumen['tipo']} {resumen['anio']}")
    print(f"  pasos escritos : {resumen['pasos_escritos']}")
    print(f"  pasos totales  : {resumen['pasos_totales']}")
    print(f"  store          : {resumen['store']}")
