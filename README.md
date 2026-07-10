# Atlas Climático de México

Aplicación interactiva desarrollada con **Shiny para Python** para la exploración de variables climáticas derivadas de ERA5.

Actualmente la aplicación permite visualizar:

- **SSRD (Surface Solar Radiation Downwards):** radiación solar incidente en superficie.
- **UTCI (Universal Thermal Climate Index):** índice de estrés térmico.

La aplicación utiliza datos de ERA5 previamente procesados para generar mapas interactivos y visualizaciones que permiten comparar el comportamiento promedio nacional con un punto específico seleccionado por el usuario.

---

# Estructura del proyecto

```text
ATLAS/
│
├── app/
│   ├── app.py
│   └── components/
│       ├── panels.py
│       ├── servers.py
│       └── shared.py
│
├── data/
│   ├── 001_raw/
│   └── 002_processed/
│
├── docs/
├── notebooks/
├── pyproject.toml
├── uv.lock
└── README.md
```

---

# Requisitos

- Python 3.12 o superior
- Git
- uv

> **Nota:** Si aún no tienes instalado **uv**, puedes seguir la guía oficial de instalación:
>
> https://docs.astral.sh/uv/

---

# Instalación

## 1. Clonar el repositorio

La versión actual del proyecto se encuentra en la rama **`feat/utci-viewer-v1`**.

```bash
git clone --branch feat/utci-viewer-v1 https://github.com/Esmeralda0600/atlas_esmeralda.git
cd atlas_esmeralda
```

---

## 2. Instalar las dependencias

Desde la raíz del proyecto ejecutar:

```bash
uv sync
```

Este comando:

- Crea automáticamente un entorno virtual (si no existe).
- Instala todas las dependencias definidas en `pyproject.toml`.
- Utiliza `uv.lock` para garantizar un entorno reproducible.

---

# Gestión de dependencias

Este proyecto utiliza **uv** como gestor de paquetes y entornos virtuales.

Las dependencias se encuentran definidas en el archivo:

```text
pyproject.toml
```

Mientras que el archivo

```text
uv.lock
```

garantiza que todos los usuarios instalen exactamente las mismas versiones de las dependencias, favoreciendo la reproducibilidad del proyecto.

---

# Datos necesarios

Debido al tamaño de los archivos, el repositorio **no incluye** los siguientes datos:

```text
data/
├── 001_raw/
│   ├── ERA5_mexico_2022.nc
│   ├── stress_utci_anual_2022.nc
│   └── stress_utci_seasonal_2022.nc
│
└── 002_processed/
    ├── mexico_mask.gpkg
    └── ssrd_mexico_estacional.nc
```

Para ejecutar correctamente la aplicación, estos archivos deben generarse nuevamente mediante los notebooks y scripts incluidos en este repositorio, o bien copiarse manualmente los archivos los encontraras en : https://drive.google.com/file/d/1tPWJa8XgdH6Lbq8tvBAmf2TA6azlEkDJ/view?usp=sharing

---

# Descripción de los archivos de datos

## `ERA5_mexico_2022.nc`

Archivo NetCDF que contiene los datos meteorológicos originales de ERA5 utilizados para calcular las variables mostradas en la aplicación.

Ubicación:

```text
data/001_raw/
```

---

## `stress_utci_anual_2022.nc`

Archivo NetCDF con la clasificación anual de categorías de estrés térmico UTCI.

Ubicación:

```text
data/001_raw/
```

---

## `stress_utci_seasonal_2022.nc`

Archivo NetCDF con las categorías UTCI correspondientes a cada estación del año.

Ubicación:

```text
data/001_raw/
```

---

## `mexico_mask.gpkg`

Archivo GeoPackage que contiene la máscara geográfica de México utilizada para recortar los datos de ERA5.

Ubicación:

```text
data/002_processed/
```

---

## `ssrd_mexico_estacional.nc`

Archivo NetCDF procesado que almacena:

- Promedio anual de SSRD.
- Promedios estacionales (DJF, MAM, JJA y SON).

Ubicación:

```text
data/002_processed/
```

---

# Flujo de generación de datos

Los notebooks ubicados en la carpeta

```text
notebooks/
```

documentan el procesamiento realizado para generar los archivos utilizados por la aplicación.

## Procesamiento de SSRD

```text
ERA5
 │
 ▼
ERA5_mexico_2022.nc
 │
 ▼
mask_convert.py
 │
 ▼
convert_ssrd.py
 │
 ▼
ssrd_mexico_estacional.nc
 │
 ▼
Aplicación Shiny
```

## Procesamiento de UTCI

```text
ERA5
 │
 ▼
utci_stress.py
 │
 ├──► stress_utci_anual_2022.nc
 │
 └──► stress_utci_seasonal_2022.nc
         │
         ▼
   Aplicación Shiny
```

---

# Ejecutar la aplicación

Desde la raíz del proyecto ejecutar:

```bash
uv run shiny run app/app.py
```

Una vez iniciada la aplicación, abrir en el navegador la dirección mostrada por Shiny (generalmente `http://127.0.0.1:8000`).

---

# Tecnologías utilizadas

## Lenguaje

- Python

## Framework

- Shiny for Python

## Procesamiento de datos

- xarray
- NumPy
- GeoPandas
- Rasterio
- NetCDF4

## Visualización

- ipyleaflet
- Matplotlib
- Pillow

## Gestión del proyecto

- uv

---

# Nota

Este repositorio contiene únicamente el código fuente de la aplicación.

Los archivos NetCDF y GeoPackage utilizados durante el procesamiento fueron excluidos del control de versiones debido a su tamaño. Para reproducir completamente el proyecto es necesario generar dichos archivos mediante los notebooks y scripts incluidos en este repositorio, o colocarlos manualmente en las rutas indicadas.