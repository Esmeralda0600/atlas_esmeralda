# Proyecto: visor de estrés térmico para México (estilo Thermal Trace), iteración 1

## Contexto
Soy investigador en confort térmico y energía en edificaciones (IER-UNAM).
Quiero reproducir, scopeado a México, la arquitectura de la app Thermal Trace de
Copernicus (https://thermaltrace.climate.copernicus.eu). Esa app explora el índice
UTCI (Universal Thermal Climate Index, "feels-like" que integra aire, humedad,
viento y radiación) del dataset ERA5-HEAT, usando un cubo Zarr que se agrega al
vuelo y se pinta en un mapa interactivo.

Esta es la PRIMERA iteración: el corte vertical más delgado que ya funcione de
punta a punta. No quiero que sobre-ingenieres.

## Objetivo de ESTA iteración (MVP)
Una app local que:
1. Tenga un cubo de UTCI para México como store **Zarr** (dims: time, lat, lon).
2. Permita elegir una **fecha** y una **variable/agregación** (empieza con UTCI
   máximo diario y su categoría de estrés térmico).
3. Compute el campo 2D al vuelo con **xarray** y lo **pinte sobre un mapa**.
4. Al hacer **click en un punto**, grafique la **serie temporal** de UTCI en esa
   celda (nearest).

Fuera de alcance en v1 (anotar como fases futuras, NO construir todavía):
- Tiling dinámico / TiTiler / COG (innecesario: México a 0.25° son ~77x133 ≈ 10k
  celdas, el campo entero se computa y pinta al instante).
- Anomalías vs climatología 1991-2020, escalas estacional/anual.
- Capas INEGI nivel ageb, cruces vulnerabilidad, DuckLake/Parquet, Icechunk.
- Sustituir UTCI por mi metodología de confort adaptativo (IMAC / grados-hora).
  PERO: deja la arquitectura abierta para meter un "índice pluggable" después;
  ese es mi diferenciador de investigación.

## Stack y restricciones (duras)
- Python gestionado **exclusivamente con `uv`** (`uv init`, `uv run`, `uv add`).
  Nunca pip, nunca venv manual.
- Frontend: **Shiny for Python** (ya tengo experiencia, mi proyecto ClimaLab lo usa).
- Mapa: la opción más simple que funcione dentro de Shiny (leafmap / ipyleaflet /
  pydeck / maplibre vía shinywidgets). Propón y justifica.
- Cómputo: **xarray** + **Zarr**. Datos perezosos.
- Reproducibilidad: repo limpio, `pyproject.toml` con uv, README, datos fuera de Git.

## Estrategia de datos

- En el folder data/ hay un archivos, correspondientes a un años. 
- Hay que desarrollar una estrategia de adicion de datos por año y por tipo.


## Qué quiero de ti AHORA (no escribas código todavía)
Entrégame un **plan** antes de implementar, e inicia  una rama nueva desde la planeacion:
1. Arquitectura propuesta y por qué (diagrama de módulos en texto).
2. Estructura de carpetas/archivos del repo.
3. Elección de librería de mapa para Shiny, con tradeoffs.
4. Hitos incrementales (cada uno demostrable por separado).
5. Decisiones que necesitan mi input y supuestos que estás haciendo.
6. Riesgos técnicos y cómo los mitigarías.

Hazme las preguntas que necesites antes de proponer. Cuando aprobemos el plan,
construimos hito por hito, con commits pequeños y un `uv run` que arranque la app.