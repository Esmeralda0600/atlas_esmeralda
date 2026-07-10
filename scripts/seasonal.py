"""
seasonal.py

Funciones para dividir un xarray.Dataset en estaciones del año y
analizar patrones estacionales (ej. en que estacion es mayor el SSRD
en cada punto del mapa).

Estaciones usadas (hemisferio norte, meteorologicas, no astronomicas):
    DJF -> Invierno (Dic, Ene, Feb)
    MAM -> Primavera (Mar, Abr, May)
    JJA -> Verano (Jun, Jul, Ago)
    SON -> Otonio (Sep, Oct, Nov)
"""

import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

NOMBRES_ESTACIONES = {
    "DJF": "Invierno",
    "MAM": "Primavera",
    "JJA": "Verano",
    "SON": "Otoño",
}


def split_by_season(dataset, variable=None):
    """
    Divide un dataset en las 4 estaciones del anio y calcula el
    promedio temporal de cada una.

    Parameters
    ----------
    dataset : xarray.Dataset
        Dataset con una dimension "time" (necesita datetime64).
    variable : str, optional
        Si se especifica, solo se calcula el promedio estacional de
        esa variable (devuelve un DataArray). Si es None, se calculan
        todas las variables del dataset (devuelve un Dataset).

    Returns
    -------
    xarray.Dataset or xarray.DataArray
        Promedios estacionales, con una nueva dimension "season" con
        valores ["DJF", "MAM", "JJA", "SON"].
    """
    datos = dataset[variable] if variable is not None else dataset

    promedios_estacionales = datos.groupby("time.season").mean(dim="time")

    # Reordena las estaciones en orden cronologico del anio
    orden = ["DJF", "MAM", "JJA", "SON"]
    promedios_estacionales = promedios_estacionales.sel(season=orden)

    return promedios_estacionales


def estacion_pico(dataset, variable):
    """
    Encuentra, para cada punto (lat, lon), cual es la estacion del
    anio en la que la variable alcanza su valor promedio mas alto.

    Parameters
    ----------
    dataset : xarray.Dataset
        Dataset con una dimension "time" (necesita datetime64).
    variable : str
        Nombre de la variable a analizar (ej. "ssrd").

    Returns
    -------
    xarray.DataArray
        Array 2D (lat, lon) de tipo texto, con la estacion ("DJF",
        "MAM", "JJA" o "SON") donde esa variable tiene su promedio
        mas alto en cada punto.
    xarray.DataArray
        Los promedios estacionales completos (lat, lon, season), por
        si se quieren revisar los valores numericos detras de la
        clasificacion.
    """
    promedios = split_by_season(dataset, variable=variable)

    # idxmax encuentra, a lo largo de la dimension "season", cual
    # etiqueta tiene el valor mas alto en cada punto (lat, lon)
    pico = promedios.idxmax(dim="season")
    pico.name = f"{variable}_estacion_pico"

    return pico, promedios


def split_by_custom_dates(dataset, rangos_estaciones, variable=None):
    """
    Divide un dataset en estaciones usando rangos de fecha (mes, dia)
    personalizados, en lugar de meses completos.

    Util para usar estaciones astronomicas (solsticios/equinoccios) o
    cualquier definicion propia de "estacion", ya que
    groupby("time.season") solo permite trimestres fijos (DJF/MAM/JJA/SON).

    Parameters
    ----------
    dataset : xarray.Dataset
        Dataset con una dimension "time" (datetime64).
    rangos_estaciones : dict
        Diccionario {nombre_estacion: (mes_inicio, dia_inicio, mes_fin, dia_fin)}.
        Si (mes_inicio, dia_inicio) es "mayor" que (mes_fin, dia_fin), se
        asume que la estacion cruza el fin de anio (ej. invierno: Dic 21
        -> Mar 20). Ejemplo (estaciones astronomicas, hemisferio norte):
            {
                "Invierno":  (12, 21, 3, 20),
                "Primavera": (3, 21, 6, 20),
                "Verano":    (6, 21, 9, 22),
                "Otoño":     (9, 23, 12, 20),
            }
    variable : str, optional
        Si se especifica, solo se calcula el promedio de esa variable
        (devuelve un DataArray). Si es None, se calculan todas las
        variables del dataset (devuelve un Dataset).

    Returns
    -------
    xarray.Dataset or xarray.DataArray
        Promedios por estacion, con una nueva dimension "season" cuyos
        valores son las llaves de ``rangos_estaciones``.
    """
    datos = dataset[variable] if variable is not None else dataset

    tiempos = datos["time"].dt
    mes = tiempos.month
    dia = tiempos.day
    clave_actual = mes * 100 + dia

    resultados = []
    nombres = []

    for nombre, (mes_ini, dia_ini, mes_fin, dia_fin) in rangos_estaciones.items():
        clave_ini = mes_ini * 100 + dia_ini
        clave_fin = mes_fin * 100 + dia_fin

        if clave_ini <= clave_fin:
            # rango normal, no cruza fin de anio (ej. Mar 21 -> Jun 20)
            mascara = (clave_actual >= clave_ini) & (clave_actual <= clave_fin)
        else:
            # rango que cruza fin de anio (ej. Dic 21 -> Mar 20)
            mascara = (clave_actual >= clave_ini) | (clave_actual <= clave_fin)

        subconjunto = datos.where(mascara, drop=True)
        promedio = subconjunto.mean(dim="time")

        resultados.append(promedio)
        nombres.append(nombre)

    combinado = xr.concat(resultados, dim="season")
    combinado = combinado.assign_coords(season=nombres)

    return combinado


ESTACIONES_ASTRONOMICAS = {
    "Invierno": (12, 21, 3, 20),
    "Primavera": (3, 21, 6, 20),
    "Verano": (6, 21, 9, 22),
    "Otoño": (9, 23, 12, 20),
}


def graficar_estacion_pico(pico, titulo="Estación con el pico de SSRD"):
    """
    Grafica el mapa categorico de "estacion pico" con un color fijo
    por estacion (para que Invierno/Primavera/Verano/Otonio siempre
    se vean con el mismo color en distintos mapas).

    Parameters
    ----------
    pico : xarray.DataArray
        Resultado de estacion_pico() (array 2D de texto con "DJF",
        "MAM", "JJA" o "SON").
    titulo : str
        Titulo del grafico.
    """
    orden = ["DJF", "MAM", "JJA", "SON"]
    colores = ["#4a90d9", "#7cb342", "#f9a825", "#e07b39"]  # azul, verde, amarillo, naranja

    # Convierte las etiquetas de texto a indices numericos (0-3) para
    # poder graficar con un colormap discreto
    codigos = xr.apply_ufunc(
        lambda arr: np.vectorize(orden.index)(arr),
        pico,
    )

    cmap = plt.matplotlib.colors.ListedColormap(colores)

    fig, ax = plt.subplots(figsize=(7, 5))
    im = codigos.plot(ax=ax, cmap=cmap, vmin=-0.5, vmax=3.5, add_colorbar=False)

    barra = fig.colorbar(im, ax=ax, ticks=[0, 1, 2, 3])
    barra.ax.set_yticklabels([NOMBRES_ESTACIONES[s] for s in orden])

    ax.set_title(titulo)
    fig.tight_layout()
    return fig


# ---------------------------------------------------------------------------
# Ejemplo de uso
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    from scripts.mask_convert import mask_netcdf
    from scripts.convert_ssrd import convert_ssrd_to_wm2

    resultado = mask_netcdf(
        netcdf_path="../data/001_raw/ERA5_mexico_2022.nc",
        shapefile_path="../data/002_processed/mexico_mask.gpkg",
        variable="t2m",
        convert_to_celsius=False,
        keep_variables=["t2m", "ssrd"],
        drop=True,
    )
    resultado = convert_ssrd_to_wm2(resultado, variable="ssrd")

    # 1a. Promedios estacionales por meses completos (DJF/MAM/JJA/SON)
    promedios_ssrd = split_by_season(resultado, variable="ssrd")
    print(promedios_ssrd)

    # 1b. Promedios estacionales por fechas exactas (estaciones astronomicas)
    promedios_ssrd_astro = split_by_custom_dates(
        resultado,
        rangos_estaciones=ESTACIONES_ASTRONOMICAS,
        variable="ssrd",
    )
    print(promedios_ssrd_astro)

    # 2. Estacion pico por punto (una sola vista, categorica)
    pico, _ = estacion_pico(resultado, variable="ssrd")
    fig = graficar_estacion_pico(pico, titulo="Estación con mayor SSRD promedio")
    fig.savefig("estacion_pico_ssrd.png", dpi=150)