from ipyleaflet import basemaps

from atlas import indices

# Índices disponibles para la UI: {etiqueta legible -> clave del registro}.
# Se deriva del registro pluggable: registrar un índice nuevo lo hace aparecer aquí.
INDICES = indices.labels()


BASEMAPS = {
    "WorldImagery": basemaps.Esri.WorldImagery,
    "Positron": basemaps.CartoDB.Positron,
    "DarkMatter": basemaps.CartoDB.DarkMatter,
    "Mapnik": basemaps.OpenStreetMap.Mapnik,
    "NatGeoWorldMap": basemaps.Esri.NatGeoWorldMap,
}
