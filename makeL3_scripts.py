import numpy as np
import xarray as xr
from tqdm import tqdm
import cf_xarray  # noqa: F401
import rasterio
import rioxarray as rio
from rasterio.enums import Resampling
from tools import time_from_attr

def path_to_gridded_ds(path, bbox, ds_match):
    dt = xr.open_datatree(path)
    ds = xr.merge(dt.to_dict().values())
    ds = ds.set_coords(("longitude", "latitude"))
    ds_src = ds[['cloud_bow_droplet_effective_radius',
                 'cloud_bow_droplet_effective_variance',
                 'cloud_bow_droplet_number_concentration_adiabatic',
                 'cloud_bow_liquid_water_path']]
    ds_src = ds_src.rio.set_spatial_dims("bins_across_track", "bins_along_track")
    ds_src = ds_src.rio.write_crs("epsg:4326")

    ds_dst = ds_src.rio.reproject_match(
        match_data_array=ds_match,
        src_geoloc_array=(
            ds_src.coords["longitude"],
            ds_src.coords["latitude"],
        ),
        nodata=np.nan,
        resampling=Resampling.average,
    ).rename({"x":"longitude", "y":"latitude"})
    ds_dst = ds_dst.drop_vars(["spatial_ref"])
    ds_dst = time_from_attr(ds_dst)
    W,S,E,N = bbox
    ds_dst = ds_dst.sel(latitude=slice(S,N),longitude=slice(W,E))
    
    return ds_dst

def makeL3(paths, bbox, resolution=1.0):
    W,S,E,N = bbox
    ds_match = xr.Dataset(
                    coords={
                        "longitude":np.arange(W,E+resolution,step=resolution),
                        "latitude":np.arange(S,N+resolution,step=resolution),
                    },
    )
    ds_match.rio.write_crs("epsg:4326", inplace=True)
    
    ds_list = []
    for path in tqdm(paths):
        ds1 = path_to_gridded_ds(path, bbox, ds_match)
        ds_list.append(ds1)
    ds = xr.concat(ds_list, dim="time")
    return ds













    