import ipyleaflet as L
from shinywidgets import render_widget

from components.shared import BASEMAPS


def map_server(input):
    @render_widget
    def map():
        m = L.Map(zoom=4, center=(0, 0))
        m.add_layer(L.basemap_to_tiles(BASEMAPS[input.basemap()]))
        return m
