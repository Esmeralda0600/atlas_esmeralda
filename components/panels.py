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


def sidebar_left(*args):
    return ui.sidebar(*args, bg="#f8f8f8", open="always")


def sidebar_right(*args):
    return ui.sidebar(*args, position="right", bg="#f8f8f8", open="always", width=320)


def page_two_sidebars(left, main, right):
    return ui.page_fillable(
        ui.layout_sidebar(
            left,
            ui.layout_sidebar(right, main),
        ),
        padding=0,
    )
