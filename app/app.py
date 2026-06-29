import datetime as dt
import sys
from pathlib import Path

# Permite `shiny run app/app.py` desde cualquier cwd: la raíz del repo debe estar
# en sys.path para importar el paquete de UI `components`.
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from shiny import App
from shinywidgets import output_widget

from atlas import catalog
from components.shared import BASEMAPS, INDICES
from components.panels import (
    legend_panel,
    page_two_sidebars,
    select_basemap,
    select_date,
    select_index,
    sidebar_left,
    sidebar_right,
    socioeconomic_panel,
    timeseries_panel,
)
from components.servers import map_server

# Límites de fecha derivados del cubo. Por defecto, una fecha de verano (más vistosa).
_FECHA_MIN, _FECHA_MAX = catalog.date_bounds()
_FECHA_DEFECTO = min(max(dt.date(_FECHA_MIN.year, 6, 15), _FECHA_MIN), _FECHA_MAX)

app_ui = page_two_sidebars(
    left=sidebar_left(
        select_basemap(BASEMAPS),
        select_index(INDICES),
        select_date(_FECHA_MIN, _FECHA_MAX, value=_FECHA_DEFECTO),
        legend_panel(),
        timeseries_panel(),
    ),
    right=sidebar_right(
        socioeconomic_panel(),
    ),
    main=output_widget("map"),
)


def server(input, output, session):
    map_server(input)


app = App(app_ui, server)
