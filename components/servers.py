import ipyleaflet as L
from htmltools import HTML, div
from shiny import reactive, render
from shinywidgets import render_widget

from atlas import compute, plots
from atlas import render as atlas_render
from components.shared import BASEMAPS, INDICES

# Centro y zoom para encuadrar México.
_MX_CENTER = (23.5, -102.5)
_MX_ZOOM = 5


def map_server(input):
    # Referencia mutable al ImageOverlay actual para poder reemplazarlo sin
    # reconstruir el mapa (preserva el zoom/paneo del usuario).
    estado = {"overlay": None}
    # Última celda pulsada (lat, lon); None hasta el primer clic.
    clic = reactive.Value(None)

    @reactive.calc
    def base_map():
        """Mapa base; se reconstruye solo al cambiar el mapa base."""
        m = L.Map(center=_MX_CENTER, zoom=_MX_ZOOM, scroll_wheel_zoom=True)
        m.add_layer(L.basemap_to_tiles(BASEMAPS[input.basemap()]))
        estado["overlay"] = None  # el mapa nuevo aún no tiene capa de campo

        def _on_click(**kwargs):
            if kwargs.get("type") == "click":
                lat, lon = kwargs["coordinates"]
                clic.set((float(lat), float(lon)))

        m.on_interaction(_on_click)
        return m

    @render_widget
    def map():
        return base_map()

    @reactive.effect
    def _pintar_campo():
        """Recalcula y reemplaza el ImageOverlay al cambiar fecha o índice."""
        m = base_map()
        index_key = INDICES[input.indice()]
        fecha = input.fecha()

        uri, bounds = atlas_render.overlay_for(fecha, index_key)
        nuevo = L.ImageOverlay(url=uri, bounds=bounds, opacity=0.75)

        anterior = estado["overlay"]
        if anterior is not None and anterior in m.layers:
            m.remove_layer(anterior)
        m.add_layer(nuevo)
        estado["overlay"] = nuevo

    @render.ui
    def leyenda():
        index_key = INDICES[input.indice()]
        filas = []
        for etiqueta, color in atlas_render.legend_items(index_key):
            filas.append(
                div(
                    div(
                        style=f"width:14px;height:14px;background:{color};"
                        "border:1px solid #999;margin-right:8px;flex:none;"
                    ),
                    div(etiqueta, style="font-size:12px;"),
                    style="display:flex;align-items:center;margin-bottom:3px;",
                )
            )
        return div(
            HTML("<b>Estrés térmico (UTCI)</b>"),
            div(*filas, style="margin-top:6px;"),
            style="margin-top:10px;",
        )

    @render.text
    def celda_info():
        c = clic()
        if c is None:
            return "Haz clic en el mapa para ver la serie horaria."
        clat, clon = compute.nearest_cell(c[0], c[1])
        return f"Celda seleccionada: {clat:.2f}, {clon:.2f}"

    @render.plot
    def serie():
        c = clic()
        if c is None:
            return plots.placeholder("Haz clic en el mapa")
        return plots.hourly_series(c[0], c[1], input.fecha())
