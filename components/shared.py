

import base64
import io
import sys
from pathlib import Path

import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import xarray as xr

from ipyleaflet import Map, ImageOverlay, GeoJSON, WidgetControl
from ipywidgets import Output
from IPython.display import Image as IPImage, display
from shiny import ui

matplotlib.use("Agg")

BASE_DIR = Path(__file__).resolve().parent.parent
ROOT_DIR = Path(__file__).resolve().parent.parent

sys.path.insert(0, str(ROOT_DIR))

from scripts.mask_convert import load_region_geometry, mask_netcdf
from scripts.convert_ssrd import convert_ssrd_to_wm2
from scripts.utci_categories import UTCI_STRESS, ETIQUETAS_UTCI, COLORES_UTCI
from scripts.utci_stress import (
    cargar_stress_utci,
    categoria_dominante,
    porcentaje_promedio_pais,
    porcentaje_en_punto,
)

RUTA_NETCDF_SSRD = ROOT_DIR / "data" / "001_raw" / "ERA5_mexico_2022.nc"
RUTA_MASCARA = ROOT_DIR / "data" / "002_processed" / "mexico_mask.gpkg"
RUTA_NC_ESTACIONAL_SSRD = ROOT_DIR / "data" / "002_processed" / "ssrd_mexico_estacional.nc"

RUTA_UTCI_ANUAL = ROOT_DIR / "data" / "001_raw" / "stress_utci_anual_2022.nc"
RUTA_UTCI_SEASONAL = ROOT_DIR / "data" / "001_raw" / "stress_utci_seasonal_2022.nc"

REGION_GDF = load_region_geometry(RUTA_MASCARA)


DATOS_ESTACIONALES_SSRD = xr.open_dataset(RUTA_NC_ESTACIONAL_SSRD)
PROMEDIO_ANUAL_SSRD = DATOS_ESTACIONALES_SSRD.ssrd.sel(season="Anual")
PROMEDIOS_ESTACIONALES_SSRD = DATOS_ESTACIONALES_SSRD.ssrd.sel(
    season=["DJF", "MAM", "JJA", "SON"]
)

ETIQUETAS_CAPAS_SSRD = {
    "Anual": None,
    "Invierno (DJF)": "DJF",
    "Primavera (MAM)": "MAM",
    "Verano (JJA)": "JJA",
    "Otoño (SON)": "SON",
}

ORDEN_ESTACIONES_SSRD = ["DJF", "MAM", "JJA", "SON"]
NOMBRES_ESTACIONES_SSRD = {
    "DJF": "Invierno", "MAM": "Primavera", "JJA": "Verano", "SON": "Otoño",
}

VMIN_GLOBAL_SSRD = float(np.nanmin(DATOS_ESTACIONALES_SSRD.ssrd.values))
VMAX_GLOBAL_SSRD = float(np.nanmax(DATOS_ESTACIONALES_SSRD.ssrd.values))

# Anomalía = valor estacional - valor anual
ANOMALIA_ESTACIONAL_SSRD = PROMEDIOS_ESTACIONALES_SSRD - PROMEDIO_ANUAL_SSRD
VMAX_ANOM_SSRD = float(np.nanmax(np.abs(ANOMALIA_ESTACIONAL_SSRD.values)))
VMIN_ANOM_SSRD = -VMAX_ANOM_SSRD

# Anomalía a nivel país 
PAIS_PROMEDIO_ANUAL_SSRD = float(PROMEDIO_ANUAL_SSRD.mean(skipna=True))
PAIS_PROMEDIO_ESTACIONAL_SSRD = PROMEDIOS_ESTACIONALES_SSRD.mean(
    dim=["lat", "lon"], skipna=True
)
PAIS_ANOMALIA_ESTACIONAL_SSRD = PAIS_PROMEDIO_ESTACIONAL_SSRD - PAIS_PROMEDIO_ANUAL_SSRD


def obtener_capa_ssrd(nombre_capa):
    """Devuelve (array, es_anomalia).
    'Anual' -> valor absoluto de SSRD.
    Cualquier estación -> anomalía respecto al promedio anual.
    """
    etiqueta = ETIQUETAS_CAPAS_SSRD[nombre_capa]
    if etiqueta is None:
        return PROMEDIO_ANUAL_SSRD, False
    return ANOMALIA_ESTACIONAL_SSRD.sel(season=etiqueta), True


def cargar_datos_crudos_ssrd():
    resultado = mask_netcdf(
        netcdf_path=RUTA_NETCDF_SSRD,
        shapefile_path=RUTA_MASCARA,
        dataset_type="era5",
        variable="ssrd",
        keep_variables=["ssrd"],
        drop=True,
    )
    # mask_netcdf ya convierte ssrd de J/m^2 a W/m^2 internamente
    return resultado


DATOS_CRUDOS_SSRD = cargar_datos_crudos_ssrd()

CAPAS_UTCI = cargar_stress_utci(RUTA_UTCI_ANUAL, RUTA_UTCI_SEASONAL)
ETIQUETAS_CAPAS_UTCI = ["Anual", "Invierno", "Primavera", "Verano", "Otoño"]

CATEGORIA_DOMINANTE_UTCI = {
    nombre: categoria_dominante(capa) for nombre, capa in CAPAS_UTCI.items()
}

def array_a_data_url(data_array, cmap="YlOrRd", vmin=None, vmax=None):
    """Convierte un DataArray 2D continuo (lat, lon) en un PNG (data URL)."""
    valores = data_array.values

    lat_vals = data_array["lat"].values
    if lat_vals[0] < lat_vals[-1]:
        valores = np.flipud(valores)

    if vmin is None:
        vmin = np.nanmin(valores)
    if vmax is None:
        vmax = np.nanmax(valores)

    normalizado = (valores - vmin) / (vmax - vmin)
    normalizado = np.clip(normalizado, 0, 1)

    colormap = plt.get_cmap(cmap)
    rgba = colormap(normalizado, bytes=True)
    mascara_nan = np.isnan(valores)
    rgba[mascara_nan, 3] = 0

    from PIL import Image

    imagen = Image.fromarray(rgba, mode="RGBA")
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{b64}", float(vmin), float(vmax)


def array_categorico_a_data_url(data_array, colores):
    """
    Convierte un DataArray 2D de INDICES de categoria (0..N-1, con NaN
    donde no hay dato) en un PNG (data URL), usando una lista fija de
    colores (uno por categoria).
    """
    valores = data_array.values

    lat_vals = data_array["lat"].values
    if lat_vals[0] < lat_vals[-1]:
        valores = np.flipud(valores)

    cmap = matplotlib.colors.ListedColormap(colores)
    mascara_nan = np.isnan(valores)

    indices_seguros = np.nan_to_num(valores, nan=0).astype(int)
    indices_seguros = np.clip(indices_seguros, 0, len(colores) - 1)

    rgba = (cmap(indices_seguros) * 255).astype(np.uint8)
    rgba[mascara_nan, 3] = 0

    from PIL import Image

    imagen = Image.fromarray(rgba, mode="RGBA")
    buffer = io.BytesIO()
    imagen.save(buffer, format="PNG")
    b64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

    return f"data:image/png;base64,{b64}"


def calcular_bounds(data_array):
    lat_vals = data_array["lat"].values
    lon_vals = data_array["lon"].values
    return [
        [float(lat_vals.min()), float(lon_vals.min())],
        [float(lat_vals.max()), float(lon_vals.max())],
    ]


def crear_colorbar_png(vmin, vmax, cmap="YlOrRd", etiqueta="SSRD promedio (W/m²)"):
    fig, ax = plt.subplots(figsize=(3.2, 0.4))
    fig.subplots_adjust(bottom=0.5)
    norm = matplotlib.colors.Normalize(vmin=vmin, vmax=vmax)
    cb = matplotlib.colorbar.ColorbarBase(
        ax, cmap=plt.get_cmap(cmap), norm=norm, orientation="horizontal"
    )
    cb.set_label(etiqueta, fontsize=8)
    buffer = io.BytesIO()
    fig.savefig(buffer, format="png", dpi=120, bbox_inches="tight")
    plt.close(fig)
    return buffer.getvalue()


BOUNDS_SSRD = calcular_bounds(PROMEDIO_ANUAL_SSRD)
BOUNDS_UTCI = calcular_bounds(CAPAS_UTCI["Anual"])


def leyenda_utci_html():
    """Genera la leyenda HTML de las 10 categorias UTCI (label + color)."""
    filas = []
    for cat in UTCI_STRESS:
        filas.append(
            ui.div(
                ui.div(
                    style=(
                        f"width:14px;height:14px;background:{cat.color};"
                        "border:1px solid #999;margin-right:8px;flex:none;"
                    )
                ),
                ui.div(cat.label, style="font-size:12px;"),
                style="display:flex;align-items:center;margin-bottom:3px;",
            )
        )
    return ui.div(*filas, style="margin-top:8px;")