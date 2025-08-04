def time_from_attr(ds):
    """Set the time attribute as a dataset variable
    Args:
        ds: a dataset corresponding to one or multiple Level-2 granules
    Returns:
        the dataset with a scalar "time" coordinate
    """
    datetime = ds.attrs["time_coverage_start"].replace("Z", "")
    ds["date"] = ((), np.datetime64(datetime, "ns"))
    ds = ds.set_coords("date")
    return ds

def open_L2_CLOUD_GPC(path,N=-120,E=-50,S=-170,W=-50):
    dt = xr.open_datatree(path)
    ds = xr.merge(dt.to_dict().values())
    ds = time_from_attr(ds)
    ds = ds.set_coords(('latitude','longitude'))
    ds = ds[['cloud_bow_droplet_effective_radius','cloud_bow_droplet_effective_variance','cloud_bow_droplet_number_concentration_adiabatic','cloud_bow_liquid_water_path']]
    lat_mask = np.logical_and(ds.latitude<=W,ds.latitude>=E)
    lon_mask = np.logical_and(ds.longitude<=N,ds.longitude>=S)
    mask = np.logical_and(lat_mask,lon_mask)
    ds = ds.where(mask,drop=True)
    return(ds)