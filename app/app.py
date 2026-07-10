"""
app.py

1. SSRD: mapa interactivo (ipyleaflet) con el promedio anual de
   radiación solar (W/m^2), y anomalía estacional (estación - anual)
   para DJF/MAM/JJA/SON. Al hacer click en el mapa se muestra una
   gráfica de barras con la anomalía estacional del punto vs. el
   promedio nacional.

2. Estrés térmico (UTCI): mapa de la categoria de estres termico UTCI
   mas frecuente en cada pixel (anual o por estacion), y grafica de
   barras con el % de tiempo en cada una de las 10 categorias, a nivel
   nacional y (al hacer click) para el punto seleccionado.

La lógica está dividida en components/:
    - shared.py  -> datos, rutas y utilidades comunes
    - panels.py  -> definicion de la interfaz (app_ui)
    - servers.py -> logica reactiva (server)

"""

from shiny import App

from components.panels import app_ui
from components.servers import server

app = App(app_ui, server)