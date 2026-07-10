
from shiny import ui
from shinywidgets import output_widget

from components.shared import ETIQUETAS_CAPAS_SSRD, ETIQUETAS_CAPAS_UTCI

app_ui = ui.page_navbar(
    ui.nav_panel(
        "SSRD",
        ui.page_sidebar(
            ui.sidebar(
                ui.h4("Radiación solar (SSRD)"),
                ui.p(
                    "'Anual' muestra el promedio absoluto de "
                    "radiación (W/m²). Cada estación muestra la "
                    "anomalía respecto al promedio anual: rojo = esa "
                    "estación recibe más radiación de lo normal en "
                    "ese punto, azul = recibe menos. Click en el mapa "
                    "para comparar la estacionalidad de ese punto "
                    "contra el promedio nacional."
                ),
                ui.input_radio_buttons(
                    "capa_ssrd",
                    "Capa del mapa",
                    choices=list(ETIQUETAS_CAPAS_SSRD.keys()),
                    selected="Anual",
                ),
                ui.hr(),
                ui.output_ui("info_punto_ssrd"),
                width=320,
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Mapa — SSRD: nivel anual / anomalía estacional"),
                    output_widget("mapa_ssrd"),
                    full_screen=True,
                ),
                ui.card(
                    ui.card_header("Anomalía estacional: país vs. punto"),
                    ui.output_plot("grafica_climatologia_ssrd"),
                ),
                col_widths=[7, 5],
            ),
            fillable=True,
        ),
    ),
    ui.nav_panel(
        "Estrés térmico (UTCI)",
        ui.page_sidebar(
            ui.sidebar(
                ui.h4("Estrés térmico (UTCI)"),
                ui.p(
                    "Categoría de estrés térmico más frecuente por "
                    "punto (anual o por estación). Click en el mapa "
                    "para ver el % de tiempo en cada categoría en ese "
                    "punto, comparado con el promedio nacional."
                ),
                ui.input_radio_buttons(
                    "capa_utci",
                    "Periodo",
                    choices=ETIQUETAS_CAPAS_UTCI,
                    selected="Anual",
                ),
                ui.hr(),
                ui.h5("Categorías"),
                ui.output_ui("leyenda_utci"),
                width=320,
            ),
            ui.layout_columns(
                ui.card(
                    ui.card_header("Categoría dominante de UTCI"),
                    output_widget("mapa_utci"),
                    full_screen=True,
                ),
                ui.card(
                    ui.card_header("% de tiempo en cada categoría"),
                    ui.output_plot("grafica_utci_categorias"),
                ),
                col_widths=[7, 5],
            ),
            fillable=True,
        ),
    ),
    title="Atlas México",
    fillable=True,
)