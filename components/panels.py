from shiny import ui

def select_index(variables):
    return ui.input_selectize("indice", "Índice", choices=variables, selected="Temperatura")
        
def select_basemap(BASEMAPS):
    return ui.input_selectize(
            "basemap",
            "Choose a basemap",
            choices=list(BASEMAPS.keys()),
            selected="WorldImagery",
        )


def sidebar_left(*args):
    return ui.sidebar(*args, bg="#f8f8f8", open="always")


def sidebar_right(*args):
    return ui.sidebar(*args, position="right", bg="#f8f8f8", open="always")


def page_two_sidebars(left, main, right):
    return ui.page_fillable(
        ui.layout_sidebar(
            left,
            ui.layout_sidebar(right, main),
        ),
        padding=0,
    )
