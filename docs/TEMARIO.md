# Temario — Atlas v1 como proyecto de aprendizaje (2 semanas, 2 personas)

> Reconstruir el visor de estrés térmico UTCI (paso 1 del proyecto Atlas) como
> ruta de aprendizaje. Dos estudiantes de 7º semestre de ing. en ciencias
> computacionales (México), conocimientos básicos de series temporales, alta
> capacidad de aprendizaje. **4 h/día · 10 días hábiles · ~40 h por persona.**

## Filosofía del temario

1. **Reconstruir, no copiar.** El repo actual (`feat/utci-viewer-v1`) es la
   *solución de referencia* del instructor. Los estudiantes lo rebuild desde
   datos crudos; consultan la referencia solo tras intentar cada pieza.
2. **Cuestionar toda decisión.** Cada tecnología elegida (Zarr, xarray, Shiny,
   ipyleaflet, ImageOverlay, el chunking, el colormap…) se trató como "la opción
   más simple que funciona". El estudiante debe **verificar si sigue siendo la
   adecuada** contra alternativas y bibliografía, y escribirlo (ADR, ver abajo).
3. **Dos roles, una interfaz.** El éxito depende de que ambos respeten un
   **contrato** definido el Día 2 (el esquema del cubo). Es la lección central de
   ingeniería de software del proyecto.

---

## Los dos roles y su objetivo único

### Persona A — Datos & Store (ingesta → Zarr)
> **Objetivo:** construir un pipeline reproducible que convierta datos crudos de
> ERA5-HEAT (UTCI) en un cubo **Zarr** consultable de forma perezosa, escalable a
> varios años y variables, y **justificar por escrito** por qué Zarr y cada
> decisión de almacenamiento son —o no— las adecuadas para los patrones de acceso
> de esta app.

### Persona B — Visualización & App (mapa interactivo)
> **Objetivo:** construir una app web que pinte el campo UTCI sobre un mapa de
> México y grafique la serie temporal de una celda al hacer clic, y **justificar
> por escrito** por qué Shiny + ipyleaflet y cada decisión de visualización son
> —o no— las adecuadas.

---

## El contrato de interfaz (definir el Día 2, juntos)

Es el "API" entre las dos personas. Mientras se respete, cada quien trabaja en
paralelo. Persona B no necesita el cubo real de A: trabaja contra un **fixture**
(un Zarr pequeño sintético) que cumpla el contrato.

```
Store Zarr  utci_mexico.zarr
  dims:    (time, lat, lon)
  coords:  time  -> datetime64, horario, UTC, monótono creciente
           lat   -> float, ascendente (sur→norte)
           lon   -> float, ascendente (oeste→este)
  var:     utci(time, lat, lon)  float32   units="°C"
  acceso:  open_zarr(...).sel(time=<día>) -> 24 horas de ese día
           .sel(lat=, lon=, method="nearest") -> celda
```

**Tarea conjunta Día 2:** escribir un `tests/test_contrato.py` que valide estas
propiedades. Es la red de seguridad de la integración.

---

## Calendario

Leyenda: 🤝 = sesión conjunta · 📄 = entregable · 🔍 = tarea de cuestionamiento crítico.

### Semana 1 — fundamentos y reconstrucción del núcleo

| Día | Persona A (Datos & Store) | Persona B (Visualización & App) |
|---|---|---|
| **1** 🤝 | **Kickoff conjunto (4 h):** ¿qué es UTCI y por qué? (índice "feels-like"); ¿qué es ERA5-HEAT?; tour del problema y del repo; `uv` (sync/run/add); flujo de git con ramas y commits pequeños. 📄 entorno funcionando + primer commit. | (igual, conjunto) |
| **2** | NetCDF + xarray: abrir un archivo diario, inspeccionar `dims/coords/attrs`, convenciones CF, unidades (Kelvin→°C). 📄 notebook de exploración. 🤝 definir el **contrato** + `test_contrato.py`. | Shiny for Python: modelo reactivo (`input`/`output`/`reactive.calc`/`reactive.effect`). 📄 mini-app "hola reactividad". 🤝 contrato + crear el **fixture Zarr** sintético. |
| **3** | Series temporales con xarray: `resample` a máximo diario, selección `nearest`, ciclo diurno, el problema **UTC vs hora local**. 📄 campo de UTCI máx diario + serie de una celda (en notebook). | Mapas web: *tiles*, *basemaps*, **CRS** (EPSG:4326 vs 3857), conceptos de Leaflet; ipyleaflet dentro de Shiny vía `shinywidgets`. 📄 mapa con basemap centrado en México. |
| **4** | Zarr a fondo: *chunking*, compresión (codecs), layout en disco. Escribir un cubo de **un mes**. 🔍 **experimento de chunking**: medir tiempo de "leer un día" vs "leer la serie de una celda" con 2–3 chunkings distintos. 📄 mini-reporte del benchmark. | Rasterizar un campo 2D → imagen; **colormaps** (discreto vs continuo, perceptualmente uniformes, *colorblind-safe*); escala de estrés UTCI; `ImageOverlay`; el problema de **discretización/pixelado** y la distorsión por CRS. 📄 pintar un campo del fixture en el mapa. |
| **5** | Ingesta de un **año completo**: `open_mfdataset`, normalización, idempotencia y *append* por `time`. Descarga programática con la **CDS API** (`cdsapi`). 📄 `atlas-ingest UTCI <año>` funcionando e idempotente. | Reactividad real: selectores de fecha e índice, actualización del overlay **preservando zoom**, leyenda. 📄 campo interactivo por fecha (contra el fixture). |

### Semana 2 — cuestionar, extender, integrar

| Día | Persona A (Datos & Store) | Persona B (Visualización & App) |
|---|---|---|
| **6** 🤝 | 🔍 **ADR-1: "¿Zarr es la herramienta correcta?"** Comparar contra NetCDF directo, HDF5, TileDB, Parquet/Arrow, COG, GRIB, Icechunk — frente a *estos* patrones de acceso y escala. 📄 ADR-1 (borrador). | 🔍 **ADR-2: "¿ImageOverlay (cliente) o tiling servidor (TiTiler)? ¿Y por qué Shiny?"** Comparar Shiny vs Dash/Streamlit/Panel/JS puro; ImageOverlay vs TiTiler/titiler-xarray. 📄 ADR-2 (borrador). 🤝 30 min: cada quien presenta su ADR al otro. |
| **7** | El hueco real: **ingesta multi-variable / multi-año en cualquier orden.** Diseñar "un store por variable" vs "store compartido con NaN"; implementar uno. 📄 ingerir una 2ª variable o un año fuera de orden. | Clic → serie temporal: `on_interaction` → `reactive.Value` → celda *nearest* → gráfica con bandas de estrés, etiquetas en **UTC**. 📄 clic funcionando. |
| **8** | Robustez: validación de huecos/días faltantes, `pytest`, logging, manejo de errores claros. 📄 suite de pruebas verde. | 🔍 Evaluación práctica de **librerías de mapa alternativas**: reimplementar UNA feature en `leafmap` / `pydeck` / `maplibre` / `lonboard` y comparar. 📄 notas de comparación con código. |
| **9** 🤝 | **Integración:** conectar la app de B al cubo real de A; pulir la API del catálogo; chequeo de desempeño sobre el cubo completo. | **Integración:** consumir el cubo real; demostrar el **índice pluggable** registrando un 2º índice (p. ej. UTCI mínimo o media diaria) y verlo en la UI sin tocar la app. 📄 2º índice en el selector. |
| **10** 🤝 | **Demo final conjunta + cierre:** finalizar ADR-1/ADR-2, README de cada módulo, retro. 📄 demo de punta a punta + ADRs finales. | (igual, conjunto) |

---

## Entregables de cuestionamiento crítico (ADRs)

El formato es un **ADR** (*Architecture Decision Record*): 1–2 páginas con
**contexto → opciones consideradas → criterios → decisión → consecuencias**. No
se trata de "tenían razón los del repo", sino de defender o refutar con evidencia
(benchmarks propios + bibliografía).

**Persona A debe responder, con datos y citas:**
- ¿Zarr, o bastaba NetCDF/HDF5? ¿Cuándo gana TileDB o Icechunk (escrituras
  transaccionales, concurrencia)? ¿Y COG/GeoParquet para otros consumos?
- ¿El chunking `time=24` es óptimo, o conviene otro para la serie por celda?
  (respaldar con su benchmark del Día 4).
- ¿zstd es el mejor codec/nivel para este dato? ¿float32 o se puede cuantizar?
- Idempotencia por `time`: ¿es robusta? ¿*region writes* vs rebuild para insertar
  años previos?
- ¿`consolidated metadata` (deprecado en Zarr v3) ayuda o estorba aquí?

**Persona B debe responder, con datos y citas:**
- ¿Shiny for Python, o Dash/Streamlit/Panel/JS puro? Criterios: reactividad,
  curva, despliegue, que ClimaLab ya usa Shiny.
- ¿`ImageOverlay` de ~10k celdas, o tiling servidor (TiTiler/titiler-xarray)?
  ¿A qué tamaño de malla deja de escalar el enfoque cliente?
- ¿ipyleaflet, o leafmap/pydeck/maplibre/lonboard? (respaldar con el Día 8).
- CRS: pintar dato 4326 sobre mapa 3857 — ¿cuánta distorsión a lat 14–33° N?
  ¿reproyectar con rioxarray vale la pena?
- Colormap: ¿la escala discreta de 10 clases es la correcta? ¿es *colorblind-safe*?
  ¿perceptualmente uniforme?

---

## Bibliografía / recursos

**Persona A — Datos & Store**
- Xarray — docs y tutorial "Xarray in 45 min" (`tutorial.xarray.dev`); proyecto Pangeo.
- Zarr-python docs; especificación **Zarr v3** (`zarr-specs.readthedocs.io`).
- Cloud-Native Geospatial Foundation — guía de formatos (`guide.cloudnativegeo.org`): Zarr, COG, GeoParquet.
- Copernicus **CDS**: página del dataset ERA5-HEAT y docs de `cdsapi` (`cds.climate.copernicus.eu`).
- **CF Conventions** (`cfconventions.org`) — metadatos climáticos estándar.
- **Icechunk** (Earthmover, `icechunk.io`) — Zarr transaccional/versionado.
- **TileDB** docs — arrays densos/dispersos como alternativa.
- Bröde et al. (2012), *Deriving the operational procedure for the UTCI* (Int. J. Biometeorol.) — escala de estrés.
- Resample/series: docs de pandas y xarray; McKinney, *Python for Data Analysis* (cap. de series).

**Persona B — Visualización & App**
- **Shiny for Python** (`shiny.posit.co/py`) — guía de reactividad; `shinywidgets` docs.
- **ipyleaflet** (`ipyleaflet.readthedocs.io`) y **Leaflet.js** (`leafletjs.com`).
- **leafmap** (`leafmap.org`) y curso GeoPython de Qiusheng Wu (YouTube).
- Alternativas: Folium; **pydeck**/deck.gl; **MapLibre GL JS**; **lonboard** (Development Seed).
- **TiTiler** y **titiler-xarray** (`developmentseed.github.io/titiler`); spec **COG** (`cogeo.org`).
- CRS: explicaciones de **EPSG:3857 vs 4326** (`spatialreference.org`); por qué Web Mercator.
- Colormaps: docs de matplotlib; **Scientific colour maps** de F. Crameri; **ColorBrewer** (`colorbrewer2.org`); racional de *viridis*.
- Comparación de frameworks: docs de Dash, Streamlit y Panel.

---

## Resultados de aprendizaje

Al terminar, cada estudiante puede:
- **A:** modelar datos N-dimensionales, razonar sobre *chunking*/compresión/acceso
  perezoso, construir un pipeline ETL reproducible e idempotente, y justificar una
  elección de almacenamiento con benchmarks y literatura.
- **B:** construir una app reactiva no trivial, entender mapas web y CRS,
  rasterizar y colorear datos científicos correctamente, y justificar una elección
  de stack de visualización con evidencia.
- **Ambos:** definir y respetar un contrato de interfaz, trabajar en paralelo con
  git, e integrar dos módulos en un sistema que funcione de punta a punta.

## Rúbrica sugerida (100 pts)

| Criterio | Pts |
|---|---|
| El módulo funciona y cumple el contrato (demo Día 10) | 30 |
| Calidad de código (estructura, nombres, pruebas) | 20 |
| ADRs: profundidad del cuestionamiento + evidencia (benchmark + bibliografía) | 30 |
| Integración conjunta de punta a punta | 10 |
| Higiene de proceso (commits pequeños, README, reproducibilidad con `uv`) | 10 |

## Retos opcionales (para su "alta capacidad de aprendizaje")
- **A:** *region writes* para insertar años en cualquier orden; cuantización para
  reducir tamaño; probar Icechunk; descarga incremental desde CDS.
- **B:** hora local de México; reproyección a 3857 con rioxarray; *spike* de TiTiler
  para comparar con ImageOverlay; ver la rejilla de celdas como capa vectorial.

---

## Riesgos del temario y mitigación
- **Bloqueo en credenciales de la CDS API** (tarda en aprobarse): que A pida la
  cuenta el Día 1; mientras, trabajar con los NetCDF de 2022 ya descargados.
- **B esperando datos de A:** evitado con el **fixture Zarr** del Día 2.
- **Ámbito demasiado grande:** los retos opcionales son opcionales; el núcleo
  (Semana 1) es el mínimo demostrable.
- **Series temporales nuevas para ellos:** el Día 3 de A es el andamiaje; reforzar
  con el cap. de series de McKinney.
```
