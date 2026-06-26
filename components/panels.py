import datetime as dt

from shiny import ui


def select_index(indices_labels, selected=None):
    return ui.input_selectize(
        "indice",
        "Índice",
        choices=list(indices_labels),
        selected=selected or (list(indices_labels)[0] if indices_labels else None),
    )


def select_date(min_date: dt.date, max_date: dt.date, value: dt.date | None = None):
    return ui.input_date(
        "fecha",
        "Fecha",
        value=value or max_date,
        min=min_date,
        max=max_date,
    )


def select_basemap(BASEMAPS):
    return ui.input_selectize(
        "basemap",
        "Mapa base",
        choices=list(BASEMAPS.keys()),
        selected="Positron",
    )


def legend_panel():
    return ui.output_ui("leyenda")


def timeseries_panel():
    return ui.div(
        ui.tags.hr(),
        ui.output_text("celda_info"),
        ui.output_plot("serie", height="240px"),
    )


def sidebar_left(*args):
    return ui.sidebar(*args, bg="#f8f8f8", open="always")


def sidebar_right(*args):
    return ui.sidebar(*args, position="right", bg="#f8f8f8", open="always", width=320)


# Renderizado pixelado (nearest-neighbor) de la capa de imagen del mapa: cada
# celda de 0.25° se ve como un bloque nítido, sin suavizado/interpolación del
# navegador. Deja claro que los datos están discretizados al grid.
_DISCRETE_RASTER_CSS = ui.tags.style(
    ".leaflet-image-layer{"
    "image-rendering:pixelated;"
    "image-rendering:-moz-crisp-edges;"
    "image-rendering:crisp-edges;"
    "}"
)


def page_two_sidebars(left, main, right):
    return ui.page_fillable(
        _DISCRETE_RASTER_CSS,
        ui.layout_sidebar(
            left,
            ui.layout_sidebar(right, main),
        ),
        padding=0,
    )
