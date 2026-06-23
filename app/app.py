from shiny import App
from shinywidgets import output_widget

from components.shared import BASEMAPS, VARS
from components.panels import (
    select_index,
    select_basemap,
    sidebar_left,
    sidebar_right,
    page_two_sidebars,
)
from components.servers import map_server

variables = list(VARS.keys())

app_ui = page_two_sidebars(
    left=sidebar_left(
        select_basemap(BASEMAPS),
    ),
    right=sidebar_right(
        select_index(variables),
    ),
    main=output_widget("map"),
)


def server(input, output, session):
    map_server(input)


app = App(app_ui, server)
