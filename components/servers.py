
import numpy as np
import matplotlib.pyplot as plt

from shiny import ui, render, reactive
from shinywidgets import render_widget
from ipyleaflet import Map, ImageOverlay, GeoJSON, WidgetControl
from ipywidgets import Output
from IPython.display import Image as IPImage, display

from components.shared import (
    REGION_GDF,
    PROMEDIO_ANUAL_SSRD,
    PROMEDIOS_ESTACIONALES_SSRD,
    VMIN_GLOBAL_SSRD,
    VMAX_GLOBAL_SSRD,
    VMIN_ANOM_SSRD,
    VMAX_ANOM_SSRD,
    ORDEN_ESTACIONES_SSRD,
    NOMBRES_ESTACIONES_SSRD,
    PAIS_ANOMALIA_ESTACIONAL_SSRD,
    BOUNDS_SSRD,
    BOUNDS_UTCI,
    CAPAS_UTCI,
    CATEGORIA_DOMINANTE_UTCI,
    COLORES_UTCI,
    UTCI_STRESS,
    obtener_capa_ssrd,
    array_a_data_url,
    array_categorico_a_data_url,
    crear_colorbar_png,
    leyenda_utci_html,
    porcentaje_promedio_pais,
    porcentaje_en_punto,
)


def server(input, output, session):
    # ---------------------- SSRD ----------------------
    punto_click_ssrd = reactive.Value(None)
    referencias_mapa_ssrd = {}

    @render_widget
    def mapa_ssrd():
        centro_lat = (BOUNDS_SSRD[0][0] + BOUNDS_SSRD[1][0]) / 2
        centro_lon = (BOUNDS_SSRD[0][1] + BOUNDS_SSRD[1][1]) / 2

        m = Map(center=(centro_lat, centro_lon), zoom=4, scroll_wheel_zoom=True)

        capa_inicial, es_anomalia = obtener_capa_ssrd("Anual")
        if es_anomalia:
            data_url, vmin, vmax = array_a_data_url(
                capa_inicial, cmap="RdBu_r", vmin=VMIN_ANOM_SSRD, vmax=VMAX_ANOM_SSRD
            )
            etiqueta_leyenda = "Anomalía estacional (W/m²)"
        else:
            data_url, vmin, vmax = array_a_data_url(
                capa_inicial, cmap="YlOrRd", vmin=VMIN_GLOBAL_SSRD, vmax=VMAX_GLOBAL_SSRD
            )
            etiqueta_leyenda = "SSRD promedio anual (W/m²)"

        overlay = ImageOverlay(url=data_url, bounds=BOUNDS_SSRD, opacity=0.85)
        m.add(overlay)

        m.add(
            GeoJSON(
                data=REGION_GDF.__geo_interface__,
                style={"color": "#333333", "weight": 1.2, "fillOpacity": 0},
            )
        )

        salida_leyenda = Output()
        with salida_leyenda:
            display(IPImage(crear_colorbar_png(vmin, vmax, etiqueta=etiqueta_leyenda)))
        m.add(WidgetControl(widget=salida_leyenda, position="bottomleft"))

        def al_hacer_click(**kwargs):
            if kwargs.get("type") == "click":
                lat, lon = kwargs.get("coordinates")
                punto_click_ssrd.set((lat, lon))

        m.on_interaction(al_hacer_click)

        referencias_mapa_ssrd["overlay"] = overlay
        referencias_mapa_ssrd["leyenda"] = salida_leyenda

        return m

    @reactive.effect
    def _actualizar_capa_mapa_ssrd():
        if "overlay" not in referencias_mapa_ssrd:
            return

        nombre_capa = input.capa_ssrd()
        array_2d, es_anomalia = obtener_capa_ssrd(nombre_capa)

        if es_anomalia:
            data_url, vmin, vmax = array_a_data_url(
                array_2d, cmap="RdBu_r", vmin=VMIN_ANOM_SSRD, vmax=VMAX_ANOM_SSRD
            )
            etiqueta_leyenda = f"Anomalía estacional — {nombre_capa} (W/m²)"
        else:
            data_url, vmin, vmax = array_a_data_url(
                array_2d, cmap="YlOrRd", vmin=VMIN_GLOBAL_SSRD, vmax=VMAX_GLOBAL_SSRD
            )
            etiqueta_leyenda = f"SSRD promedio — {nombre_capa} (W/m²)"

        referencias_mapa_ssrd["overlay"].url = data_url

        leyenda = referencias_mapa_ssrd["leyenda"]
        leyenda.clear_output()
        with leyenda:
            display(IPImage(crear_colorbar_png(vmin, vmax, etiqueta=etiqueta_leyenda)))

    @reactive.calc
    def punto_anomalia_ssrd():
        """Anomalía estacional (estación - anual) en el punto más
        cercano al click, usando el .nc precalculado de estaciones."""
        punto = punto_click_ssrd.get()
        if punto is None:
            return None
        lat, lon = punto
        anual_punto = float(
            PROMEDIO_ANUAL_SSRD.sel(lat=lat, lon=lon, method="nearest")
        )
        estacional_punto = PROMEDIOS_ESTACIONALES_SSRD.sel(
            lat=lat, lon=lon, method="nearest"
        )
        return estacional_punto - anual_punto

    @output
    @render.ui
    def info_punto_ssrd():
        punto = punto_click_ssrd.get()
        if punto is None:
            return ui.p("Ningún punto seleccionado todavía.", class_="text-muted")
        lat, lon = punto
        return ui.p(f"Punto seleccionado: {lat:.2f}°, {lon:.2f}°")

    @output
    @render.plot
    def grafica_climatologia_ssrd():
        fig, ax = plt.subplots(figsize=(5, 4))
        x = np.arange(len(ORDEN_ESTACIONES_SSRD))
        ancho = 0.35

        valores_pais = [
            float(PAIS_ANOMALIA_ESTACIONAL_SSRD.sel(season=s))
            for s in ORDEN_ESTACIONES_SSRD
        ]
        ax.bar(
            x - ancho / 2, valores_pais, ancho,
            label="Promedio país", color="#888888",
        )

        anomalia_punto = punto_anomalia_ssrd()
        if anomalia_punto is not None:
            valores_punto = [
                float(anomalia_punto.sel(season=s)) for s in ORDEN_ESTACIONES_SSRD
            ]
            lat_sel, lon_sel = punto_click_ssrd.get()
            ax.bar(
                x + ancho / 2, valores_punto, ancho,
                label=f"Punto ({lat_sel:.2f}, {lon_sel:.2f})", color="#e65100",
            )

        ax.axhline(0, color="black", linewidth=0.8)
        ax.set_xticks(x)
        ax.set_xticklabels([NOMBRES_ESTACIONES_SSRD[s] for s in ORDEN_ESTACIONES_SSRD])
        ax.set_ylabel("Anomalía SSRD vs. promedio anual (W/m²)")
        ax.set_title("¿Qué tanto se aleja cada estación\nde su propio promedio anual?")
        ax.legend()
        ax.grid(alpha=0.3, axis="y")
        fig.tight_layout()
        return fig

    # ---------------------- UTCI ----------------------
    punto_click_utci = reactive.Value(None)
    referencias_mapa_utci = {}

    @render_widget
    def mapa_utci():
        centro_lat = (BOUNDS_UTCI[0][0] + BOUNDS_UTCI[1][0]) / 2
        centro_lon = (BOUNDS_UTCI[0][1] + BOUNDS_UTCI[1][1]) / 2

        m = Map(center=(centro_lat, centro_lon), zoom=4, scroll_wheel_zoom=True)

        capa_inicial = CATEGORIA_DOMINANTE_UTCI["Anual"]
        data_url = array_categorico_a_data_url(capa_inicial, COLORES_UTCI)
        overlay = ImageOverlay(url=data_url, bounds=BOUNDS_UTCI, opacity=0.85)
        m.add(overlay)

        m.add(
            GeoJSON(
                data=REGION_GDF.__geo_interface__,
                style={"color": "#333333", "weight": 1.2, "fillOpacity": 0},
            )
        )

        def al_hacer_click(**kwargs):
            if kwargs.get("type") == "click":
                lat, lon = kwargs.get("coordinates")
                punto_click_utci.set((lat, lon))

        m.on_interaction(al_hacer_click)

        referencias_mapa_utci["overlay"] = overlay

        return m

    @reactive.effect
    def _actualizar_capa_mapa_utci():
        if "overlay" not in referencias_mapa_utci:
            return
        nombre_capa = input.capa_utci()
        capa = CATEGORIA_DOMINANTE_UTCI[nombre_capa]
        data_url = array_categorico_a_data_url(capa, COLORES_UTCI)
        referencias_mapa_utci["overlay"].url = data_url

    @output
    @render.ui
    def leyenda_utci():
        return leyenda_utci_html()

    @output
    @render.plot
    def grafica_utci_categorias():
        nombre_capa = input.capa_utci()
        capa_porcentajes = CAPAS_UTCI[nombre_capa]

        # 1. Obtener porcentajes del País
        promedio_pais = porcentaje_promedio_pais(capa_porcentajes)

        punto = punto_click_utci.get()
        hay_punto = punto is not None

        # 2. Configurar nombres de las 10 categorías de estrés
        categorias = [cat.label for cat in UTCI_STRESS]
        x = np.arange(len(categorias))  # Posiciones de los grupos en el eje X
        
        # Crear la figura
        fig, ax = plt.subplots(figsize=(6.5, 4.5))

        if hay_punto:
            # Si el usuario hizo click, dibujamos DOS barras agrupadas (País vs Punto)
            lat, lon = punto
            porcentaje_punto = porcentaje_en_punto(capa_porcentajes, lat, lon)
            
            ancho_barra = 0.35
            ax.bar(x - ancho_barra/2, promedio_pais, ancho_barra, label="País", color="#aec7e8", edgecolor="black", linewidth=0.5)
            ax.bar(x + ancho_barra/2, porcentaje_punto, ancho_barra, label=f"Punto ({lat:.2f}°, {lon:.2f}°)", color="#1f77b4", edgecolor="black", linewidth=0.5)
            
            ax.set_title(f"Distribución de estrés térmico — {nombre_capa}\nPunto: {lat:.2f}°, {lon:.2f}°", fontsize=10, fontweight="bold")
        else:
            # Si no hay click, solo dibujamos una barra central para el promedio País
            ancho_barra = 0.5
            ax.bar(x, promedio_pais, ancho_barra, label="País", color="#aec7e8", edgecolor="black", linewidth=0.5)
            ax.set_title(f"Distribución de estrés térmico — {nombre_capa}\n(Haz click en el mapa para comparar un punto)", fontsize=10, fontweight="bold")

        # 3. Estética y etiquetas del gráfico
        ax.set_ylabel("% del tiempo", fontsize=9, fontweight="bold")
        ax.set_xticks(x)
        ax.set_xticklabels(categorias, rotation=45, ha="right", fontsize=8)
        ax.set_ylim(0, 105)  # Escala de 0 a 100%
        ax.grid(axis="y", linestyle="--", alpha=0.4)
        ax.legend(frameon=True, loc="upper right", fontsize=8)
        
        fig.tight_layout()
        return fig
