"""
mask_convert.py

Masks a NetCDF file to a geographic region (using a shapefile).

Optionally converts a selected variable:
    - "utci"  -> Kelvin to Celsius
    - "era5"  -> ssrd from J/m^2 (accumulated) to W/m^2 (average power)

Originally built for UTCI (ERA5-HEAT), but the masking is generic:
it works for any region as long as you provide the appropriate
shapefile (country, state, municipality, etc.).
"""

import argparse
import geopandas as gpd
import rioxarray
import xarray as xr


def load_region_geometry(shapefile_path, dissolve=True, crs="EPSG:4326"):
    """
    Loads a region shapefile and returns its geometry.

    Parameters
    ----------
    shapefile_path : str
        Path to the shapefile or vector file defining the region.
    dissolve : bool, default=True
        If True, merges all geometries into a single polygon.
    crs : str, default="EPSG:4326"
        Coordinate reference system to reproject the geometry to.

    Returns
    -------
    geopandas.GeoDataFrame
        Region geometry in the requested CRS.
    """
    region = gpd.read_file(shapefile_path)
    region = region.to_crs(crs)

    if dissolve:
        region = region.dissolve()

    return region


def prepare_dataset(dataset, x_dim="lon", y_dim="lat", crs="EPSG:4326"):
    """
    Prepares a dataset for spatial operations with rioxarray.

    Parameters
    ----------
    dataset : xarray.Dataset
        Input dataset.
    x_dim : str, default="lon"
        Name of the longitude dimension.
    y_dim : str, default="lat"
        Name of the latitude dimension.
    crs : str, default="EPSG:4326"
        Coordinate reference system of the dataset.

    Returns
    -------
    xarray.Dataset
        Dataset configured for spatial clipping.
    """
    dataset = dataset.rio.set_spatial_dims(x_dim=x_dim, y_dim=y_dim)
    dataset = dataset.rio.write_crs(crs)

    return dataset


def clip_to_region(dataset, region_gdf, drop=False):
    """
    Clips a dataset to the supplied region.

    Parameters
    ----------
    dataset : xarray.Dataset
        Dataset prepared with ``prepare_dataset``.
    region_gdf : geopandas.GeoDataFrame
        Region geometry.
    drop : bool, default=False
        If False, preserves the original grid and fills cells outside
        the region with NaN. If True, crops the dataset to the region's
        bounding box.

    Returns
    -------
    xarray.Dataset
        Clipped dataset.
    """
    return dataset.rio.clip(region_gdf.geometry, region_gdf.crs, drop=drop)


def kelvin_to_celsius(data):
    """
    Converts temperatures from Kelvin to Celsius.

    Parameters
    ----------
    data : xarray.Dataset or xarray.DataArray
        Input data.

    Returns
    -------
    xarray.Dataset or xarray.DataArray
        Data converted to degrees Celsius.
    """
    return data - 273.15


def ssrd_to_wm2(data, accumulation_seconds=3600):
    """
    Converts an accumulated radiation variable from J/m^2 to average
    power in W/m^2.

    Parameters
    ----------
    data : xarray.Dataset or xarray.DataArray
        Input data (accumulated J/m^2).
    accumulation_seconds : int, default=3600
        Length of the accumulation period in seconds. Use 3600 for
        hourly ERA5 data.

    Returns
    -------
    xarray.Dataset or xarray.DataArray
        Data converted to W/m^2.
    """
    return data / accumulation_seconds


def mask_netcdf(
    netcdf_path,
    shapefile_path,
    dataset_type="utci",
    variable=None,
    x_dim="lon",
    y_dim="lat",
    crs="EPSG:4326",
    drop=False,
    keep_variables=None,
    accumulation_seconds=3600,
):
    """
    Clips a NetCDF dataset to a geographic region, and applies the
    unit conversion that corresponds to the dataset type.

    Parameters
    ----------
    netcdf_path : str
        Path to the input NetCDF file.
    shapefile_path : str
        Path to the region shapefile.
    dataset_type : {"utci", "era5"}, default="utci"
        Which kind of source dataset this is, and therefore which
        conversion to apply:
            - "utci": converts ``variable`` from Kelvin to Celsius.
            - "era5": converts ``variable`` (ssrd) from J/m^2
              (accumulated) to W/m^2 (average power).
    variable : str, optional
        Name of the variable to convert. Defaults to "utci" when
        ``dataset_type="utci"``, and to "ssrd" when
        ``dataset_type="era5"``. Only needed if your variable has a
        different name than these defaults.
    x_dim : str, default="lon"
        Name of the longitude dimension.
    y_dim : str, default="lat"
        Name of the latitude dimension.
    crs : str, default="EPSG:4326"
        Coordinate reference system.
    drop : bool, default=False
        Whether to crop the dataset to the region's bounding box.
    keep_variables : list of str, optional, default=None
        If provided, only these variables are kept before clipping.
        Useful to reduce memory usage when the source NetCDF has many
        variables but only a few are needed. If None (default), all
        variables in the dataset are kept.
    accumulation_seconds : int, default=3600
        Only used when ``dataset_type="era5"``. Length of the
        accumulation period in seconds for the ssrd conversion (3600
        for hourly ERA5 data).

    Returns
    -------
    xarray.Dataset
        Dataset clipped to the selected region, with the
        corresponding variable already converted:
            - "utci" -> degrees Celsius
            - "era5" -> W/m^2 (ssrd)
    """
    if dataset_type not in ("utci", "era5"):
        raise ValueError(
            f"dataset_type debe ser 'utci' o 'era5', se recibio: {dataset_type!r}"
        )

    # Nombre de variable por defecto segun el tipo de dataset
    if variable is None:
        variable = "utci" if dataset_type == "utci" else "ssrd"

    with xr.open_dataset(netcdf_path) as dataset:
        if keep_variables is not None:
            dataset = dataset[keep_variables]

        dataset = prepare_dataset(dataset, x_dim=x_dim, y_dim=y_dim, crs=crs)
        region = load_region_geometry(shapefile_path, crs=crs)
        dataset = clip_to_region(dataset, region, drop=drop)
        dataset = dataset.load()

    if dataset_type == "utci":
        dataset[variable] = kelvin_to_celsius(dataset[variable])
    elif dataset_type == "era5":
        dataset[variable] = ssrd_to_wm2(
            dataset[variable], accumulation_seconds=accumulation_seconds
        )
        if "units" in dataset[variable].attrs:
            dataset[variable].attrs["units"] = "W m**-2"

    return dataset