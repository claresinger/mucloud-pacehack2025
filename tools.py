import numpy as np
import xarray as xr
import matplotlib as plt

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

def open_L2_CLOUD_GPC(path,N=-50,E=-120,S=-60,W=-170):
    dt = xr.open_datatree(path)
    ds = xr.merge(dt.to_dict().values())
    ds = time_from_attr(ds)
    ds = ds.set_coords(('latitude','longitude'))
    ds = ds[['cloud_bow_droplet_effective_radius','cloud_bow_droplet_effective_variance','cloud_bow_droplet_number_concentration_adiabatic','cloud_bow_liquid_water_path']]
    lat_mask = np.logical_and(ds.latitude<=N,ds.latitude>=S)
    lon_mask = np.logical_and(ds.longitude<=E,ds.longitude>=W)
    mask = np.logical_and(lat_mask,lon_mask)
    ds = ds.where(mask,drop=True)
    return(ds)

def plot_hist(cdnc,lwp):
    
    fig,ax = plt.subplots()
    
    xbins = np.logspace(0,2.5,50) # <- make a range from 10**xmin to 10**xmax
    #print(xbins)
    ybins = np.logspace(1,2.5,50) # <- make a range from 10**ymin to 10**ymax
    #print(xbins,ybins)
    h,xedge,yedge,im = ax.hist2d(cdnc,lwp,bins=(xbins,ybins))
    
    h_norm = h/h.sum(axis=1,keepdims=True)
    h_norm=np.transpose(h_norm)
    
    im = ax.pcolormesh(xedge,yedge,h_norm,cmap='turbo',vmax=0.055)
    fig.colorbar(im,shrink=0.75)
    ax.set_xlabel('CDNC',fontsize=15)
    ax.set_ylabel(r'LWP',fontsize=15)
    ax.set_yscale('log')
    ax.set_xscale('log')
    plt.show()