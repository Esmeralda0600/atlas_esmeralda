"""
utci_stress.py

Carga y procesa los .nc de porcentaje de tiempo en cada categoria de
estres termico UTCI (ya enmascarados a Mexico), generados fuera de
esta app:
    - stress_utci_anual_2022.nc      dims (category, lat, lon)
    - stress_utci_seasonal_2022.nc   dims (season, category, lat, lon)

En ambos, la variable "utci" contiene PORCENTAJES (0-100, suman 100
por pixel a lo largo de la dimension "category"), no valores de UTCI
en grados. category_label trae el nombre de cada una de las 10 clases
de estres termico.
"""

import numpy as np
import xarray as xr

from scripts.utci_categories import UTCI_STRESS, ETIQUETAS_UTCI


def cargar_stress_utci(ruta_anual, ruta_seasonal):
    """
    Carga los dos .nc de estres UTCI (anual y estacional).

    Returns
    -------
    dict
        {"Anual": DataArray(category, lat, lon),
         "Invierno": DataArray(category, lat, lon),
         "Primavera": DataArray(category, lat, lon),
         "Verano": DataArray(category, lat, lon),
         "Otoño": DataArray(category, lat, lon)}
    """
    ds_anual = xr.open_dataset(ruta_anual)
    ds_seasonal = xr.open_dataset(ruta_seasonal)

    capas = {"Anual": ds_anual["utci"]}
    for temporada in ds_seasonal["season"].values:
        capas[str(temporada)] = ds_seasonal["utci"].sel(season=temporada)

    return capas


def categoria_dominante(capa_porcentajes):
    """
    Para cada pixel, encuentra el indice (0-9) de la categoria UTCI
    con mayor porcentaje de aparicion.

    Parameters
    ----------
    capa_porcentajes : xarray.DataArray
        Dims (category, lat, lon), con porcentajes 0-100.

    Returns
    -------
    xarray.DataArray
        Array 2D (lat, lon) con el indice de categoria dominante
        (float, con NaN donde no hay datos).
    """
    valores = capa_porcentajes.values  # (category, lat, lon)
    mascara_nan = np.all(np.isnan(valores), axis=0)

    valores_sin_nan = np.nan_to_num(valores, nan=-1)
    indice_dominante = np.argmax(valores_sin_nan, axis=0).astype(float)
    indice_dominante[mascara_nan] = np.nan

    resultado = xr.DataArray(
        indice_dominante,
        dims=("lat", "lon"),
        coords={"lat": capa_porcentajes["lat"], "lon": capa_porcentajes["lon"]},
        name="categoria_dominante",
    )
    return resultado


def porcentaje_promedio_pais(capa_porcentajes):
    """
    Promedio nacional (espacial) del porcentaje de cada categoria.

    Parameters
    ----------
    capa_porcentajes : xarray.DataArray
        Dims (category, lat, lon).

    Returns
    -------
    numpy.ndarray
        Array de 10 valores (uno por categoria, en el mismo orden que
        UTCI_STRESS), con el porcentaje promedio a nivel nacional.
    """
    promedio = capa_porcentajes.mean(dim=["lat", "lon"], skipna=True)
    return promedio.values


def porcentaje_en_punto(capa_porcentajes, lat, lon):
    """
    Porcentaje de cada categoria en el pixel mas cercano a (lat, lon).

    Returns
    -------
    numpy.ndarray
        Array de 10 valores (uno por categoria).
    """
    punto = capa_porcentajes.sel(lat=lat, lon=lon, method="nearest")
    return punto.values