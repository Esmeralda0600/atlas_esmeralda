"""
build_seasonal_ssrd.py

Genera un archivo .nc "listo para usar" con el promedio estacional de
SSRD (radiacion solar) para Mexico, en W/m^2.

Pipeline:
    1. Recorta el NetCDF crudo de ERA5 a la mascara de Mexico
       (solo se conserva la variable ssrd, para ahorrar memoria).
    2. Convierte ssrd de J/m^2 (acumulado) a W/m^2 (potencia promedio).
    3. Calcula el promedio por estacion (DJF/MAM/JJA/SON) y tambien el
       promedio anual, y los guarda juntos en un solo Dataset.
    4. Guarda el resultado como un nuevo archivo .nc.

El .nc resultante ya no tiene dimension "time": en su lugar tiene una
dimension "season" con 5 valores ("Anual", "DJF", "MAM", "JJA", "SON"),
listo para cargarse directo en la app sin tener que reprocesar el
NetCDF crudo cada vez que arranca.

Ejecutar con:
    uv run python scripts/build_seasonal_ssrd.py
"""

import sys
from pathlib import Path

import numpy as np
import xarray as xr

# Permite importar desde scripts/ sin importar desde donde se ejecute
sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from scripts.mask_convert import mask_netcdf
from scripts.convert_ssrd import convert_ssrd_to_wm2
from scripts.seasonal import split_by_season


def generar_nc_estacional(
    netcdf_path,
    shapefile_path,
    output_path,
    variable="ssrd",
    x_dim="lon",
    y_dim="lat",
    crs="EPSG:4326",
):
    """
    Genera un .nc con el promedio anual y estacional de una variable
    de radiacion, ya recortada a una region y convertida de J/m^2 a
    W/m^2.

    Parameters
    ----------
    netcdf_path : str or Path
        Ruta al NetCDF crudo de ERA5.
    shapefile_path : str or Path
        Ruta al shapefile/gpkg de la region (ej. mexico_mask.gpkg).
    output_path : str or Path
        Ruta donde se guardara el .nc resultante.
    variable : str, default="ssrd"
        Nombre de la variable de radiacion a procesar.
    x_dim, y_dim : str
        Nombres de las dimensiones espaciales en el NetCDF de origen.
    crs : str, default="EPSG:4326"
        Sistema de referencia de coordenadas.

    Returns
    -------
    xarray.Dataset
        Dataset con dimension "season" (Anual, DJF, MAM, JJA, SON) y
        la variable convertida a W/m^2, ya guardado en disco.
    """
    # 1. Recorta el NetCDF a la region, quedandose solo con la
    #    variable de interes (ahorra memoria al no cargar variables
    #    que no se van a usar).
    recortado = mask_netcdf(
        netcdf_path=netcdf_path,
        shapefile_path=shapefile_path,
        variable=variable,
        #convert_to_celsius=False,   # no aplica a ssrd, solo es para t2m/utci
        keep_variables=[variable],
        drop=True,
        x_dim=x_dim,
        y_dim=y_dim,
        crs=crs,
    )

    # 2. Convierte de J/m^2 (acumulado) a W/m^2 (potencia promedio)
    recortado = convert_ssrd_to_wm2(recortado, variable=variable)

    # 3. Promedio anual y promedios estacionales
    promedio_anual = recortado[variable].mean(dim="time")
    promedio_anual = promedio_anual.expand_dims(season=["Anual"])

    promedios_estacionales = split_by_season(recortado, variable=variable)

    # 4. Junta anual + estaciones en un solo DataArray (dimension season)
    combinado = xr.concat([promedio_anual, promedios_estacionales], dim="season")
    combinado.name = variable
    combinado.attrs["units"] = "W m**-2"
    combinado.attrs["long_name"] = "Surface solar radiation downwards (promedio)"
    combinado.attrs["description"] = (
        "Promedio anual y estacional (DJF/MAM/JJA/SON) de SSRD, "
        "recortado a la region indicada y convertido de J/m^2 a W/m^2."
    )

    dataset_final = combinado.to_dataset()
    dataset_final.attrs["source"] = "ERA5 (ECMWF), procesado con mask_convert + seasonal"
    dataset_final.attrs["crs"] = crs

    # 5. Guarda a disco
    output_path = Path(output_path)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    dataset_final.to_netcdf(output_path)

    return dataset_final


if __name__ == "__main__":
    ROOT_DIR = Path(__file__).resolve().parent.parent

    RUTA_NETCDF = ROOT_DIR / "data" / "001_raw" / "ERA5_mexico_2022.nc"
    RUTA_MASCARA = ROOT_DIR / "data" / "002_processed" / "mexico_mask.gpkg"
    RUTA_SALIDA = ROOT_DIR / "data" / "002_processed" / "ssrd_mexico_estacional_2022.nc"

    dataset = generar_nc_estacional(
        netcdf_path=RUTA_NETCDF,
        shapefile_path=RUTA_MASCARA,
        output_path=RUTA_SALIDA,
        variable="ssrd",
    )

    print(f"Archivo generado en: {RUTA_SALIDA}")
    print(dataset)