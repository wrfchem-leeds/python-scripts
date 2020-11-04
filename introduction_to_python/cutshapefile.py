#!/usr/bin/env python3
import numpy as np
import xarray as xr
from rasterio import features
from affine import Affine

def transform_from_latlon(lat, lon):
    """ input 1D array of lat / lon and output an Affine transformation """
    lat = np.asarray(lat)
    lon = np.asarray(lon)
    trans = Affine.translation(lon[0], lat[0])
    scale = Affine.scale(lon[1] - lon[0], lat[1] - lat[0])
    return trans * scale


def rasterize(shapes, coords, latitude='latitude', longitude='longitude', fill=np.nan, **kwargs):
    """
    Description:    
        Rasterize a list of (geometry, fill_value) tuples onto the given
        xarray coordinates. This only works for 1D latitude and longitude
        arrays.

    Usage:
        1. read shapefile to geopandas.GeoDataFrame
               `states = gpd.read_file(shp_dir+shp_file)`
        2. encode the different shapefiles that capture those lat-lons as different
           numbers i.e. 0.0, 1.0 ... and otherwise np.nan
              `shapes = (zip(states.geometry, range(len(states))))`
        3. Assign this to a new coord in your original xarray.DataArray
              `ds['states'] = rasterize(shapes, ds.coords, longitude='X', latitude='Y')`

    Arguments:
        **kwargs (dict): passed to `rasterio.rasterize` function.

    Attributes:
        transform (affine.Affine): how to translate from latlon to ...?
        raster (numpy.ndarray): use rasterio.features.rasterize fill the values
                                outside the .shp file with np.nan
        spatial_coords (dict): dictionary of {"X":xr.DataArray, "Y":xr.DataArray()}
                               with "X", "Y" as keys, and xr.DataArray as values

    Returns:
        (xr.DataArray): DataArray with `values` of nan for points outside shapefile
                        and coords `Y` = latitude, 'X' = longitude.

    """
    transform = transform_from_latlon(coords[latitude], coords[longitude])
    out_shape = (len(coords[latitude]), len(coords[longitude]))
    raster = features.rasterize(
        shapes, 
        out_shape=out_shape,
        fill=fill,
        transform=transform,
        dtype=float, 
        **kwargs
    )
    spatial_coords = {latitude: coords[latitude], longitude: coords[longitude]}
    return xr.DataArray(raster, coords=spatial_coords, dims=(latitude, longitude))

