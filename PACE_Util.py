import xarray as xr
import numpy as np
import sys,os,glob,datetime
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import cartopy.crs as ccrs
import cartopy.feature as cfeature

def normalize_rgb(R, G, B):
    """
    Normalize and stack the RGB components.
    """
    RGB = np.stack((R, G, B), axis=2)
    rhos_rgb = xr.DataArray(RGB, dims=("x", "y", "wavelength"))
    rhos_rgb_max = rhos_rgb.max()
    rhos_rgb_min = rhos_rgb.min()
    rhos_rgb_enhanced = (rhos_rgb - rhos_rgb_min) / (rhos_rgb_max - rhos_rgb_min)
    return rhos_rgb_enhanced

def discrete_matshow(data,cmap_name='jet'):
    # get discrete colormap
    cmap = plt.get_cmap(cmap_name, np.max(data) - np.min(data) + 1)
    # set limits .5 outside true range
    mat = plt.imshow(data, cmap=cmap, vmin=np.min(data) - 0.5, 
                      vmax=np.max(data) + 0.5, origin='lower')
    # tell the colorbar to tick at integers
    cax = plt.colorbar(mat, ticks=np.arange(np.min(data), np.max(data) + 1))

class OCI_Level1B(object):
    def __init__(self, granule_timestamp, data_version='V2', data_path='./'):
        file_pattern = f'{data_path}PACE_OCI.{granule_timestamp}.L1B*.nc'
        try:
            fn = glob.glob(file_pattern)[0]
        except IndexError:
            logging.error(f'Cannot find data file: {file_pattern}')
            return

        self.load_data(fn)
        self.set_timestamp(granule_timestamp)

    def load_data(self, filename):
        self.geo = xr.open_dataset(filename, group='geolocation_data', decode_cf=True)
        self.obs = xr.open_dataset(filename, group='observation_data', decode_cf=True)
        self.sbp = xr.open_dataset(filename, group='sensor_band_parameters', decode_cf=True)

    def set_timestamp(self, granule_timestamp):
        self.granule_timestamp = granule_timestamp
        self.datetime = datetime.datetime.strptime(granule_timestamp, '%Y%m%dT%H%M%S')

    def plot_true_color_RGB(self,x0_indices=None, y0_indices=None, save_RGB=True):
        B = self.obs.rhot_blue[56, :, :]
        G = self.obs.rhot_blue[97, :, :]
        R = self.obs.rhot_red[20, :, :]
        rhos_rgb_enhanced = normalize_rgb(R, G, B)
        
        #fig, ax = plt.subplots()
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())

        ax.pcolormesh(self.geo.longitude, self.geo.latitude, rhos_rgb_enhanced,
                      shading="nearest", rasterized=True, transform=ccrs.PlateCarree())
        ax.set_aspect("equal")
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        # ax.add_feature(cfeature.LAKES, alpha=0.5)
        # ax.add_feature(cfeature.RIVERS)
        
        ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        if x0_indices is not None:
            ax.scatter(self.geo.longitude[y0_indices,x0_indices],
                       self.geo.latitude[y0_indices,x0_indices], transform=ccrs.PlateCarree(),
                       c='r',alpha=0.5)
        if save_RGB:
            fig.savefig(f'PACE_OCI_L1B_RGB_{self.granule_timestamp}.png', dpi=300)

class OCI_Level1C(object):
    def __init__(self, granule_timestamp, data_version='V2', data_path='./'):
        file_pattern = f'{data_path}PACE_OCI.{granule_timestamp}.L1C*.nc'
        try:
            fn = glob.glob(file_pattern)[0]
        except IndexError:
            logging.error(f'Cannot find data file: {file_pattern}')
            return

        self.load_data(fn)
        self.set_timestamp(granule_timestamp)

    def load_data(self, filename):
        self.geo = xr.open_dataset(filename, group='geolocation_data', decode_cf=True)
        self.obs = xr.open_dataset(filename, group='observation_data', decode_cf=True)
        self.sbp = xr.open_dataset(filename, group='sensor_views_bands', decode_cf=True)

    def set_timestamp(self, granule_timestamp):
        self.granule_timestamp = granule_timestamp
        self.datetime = datetime.datetime.strptime(granule_timestamp, '%Y%m%dT%H%M%S')

    def plot_true_color_RGB(self,save_RGB=True):
        '''
        plot true color RGB using the following wavelength
        Blue: 450 nm
        Green: 552nm
        Red: 640 nm
        '''
        B=self.obs.i[:,:,0,56]
        G=self.obs.i[:,:,0,97]
        R=self.obs.i[:,:,0,140]
        rhos_rgb_enhanced = normalize_rgb(R, G, B)
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.pcolormesh(self.geo.longitude, self.geo.latitude, rhos_rgb_enhanced,
                      shading="nearest", rasterized=True,transform=ccrs.PlateCarree())
        ax.set_aspect("equal")
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        #ax.add_feature(cfeature.LAKES, alpha=0.5)
        #ax.add_feature(cfeature.RIVERS)
        
        ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        if save_RGB:
            fig.savefig(f'PACE_OCI_L1C_RGB_{self.granule_timestamp}.png', dpi=300)
            


class OCI_L2_CLD_NRT:
    def __init__(self, granule_timestamp: str, data_path: str = './'):
        """
        Initialize the OCI_L2_CLD_NRT object with cloud mask and properties datasets.

        :param granule_timestamp: Timestamp of the granule in 'YYYYMMDDHHMMSS' format.
        :param data_path: Path to the data files (default is current directory).
        """
        cldmask_fn = f"{data_path}PACE_OCI.{granule_timestamp}.L2.CLDMASK.V2_0.NRT.nc"
        cldretr_fn = f"{data_path}PACE_OCI.{granule_timestamp}.L2.CLD.V2_0.NRT.nc"

        try:
            fn = glob.glob(cldmask_fn)[0]
        except IndexError:
            logging.error(f'Cannot find data file: {cldmask_fn}')
            return

        try:
            fn = glob.glob(cldretr_fn)[0]
        except IndexError:
            logging.error(f'Cannot find data file: {cldretr_fn}')
            return
        self.load_data(cldmask_fn,cldretr_fn)
        self.set_timestamp(granule_timestamp)
        
    def load_data(self,fn1,fn2):    
        self.cld_mask = xr.open_dataset(fn1, group='geophysical_data', decode_cf=True)
        self.cld_mask_geo = xr.open_dataset(fn1, group='navigation_data', decode_cf=True)

        self.cld_prop = xr.open_dataset(fn2, group='geophysical_data', decode_cf=True)
        self.cld_prop_sbp = xr.open_dataset(fn2, group='sensor_band_parameters', decode_cf=True)
        self.cld_prop_geo = xr.open_dataset(fn2, group='navigation_data', decode_cf=True)
    
    def set_timestamp(self,granule_timestamp):
        self.granule_timestamp = granule_timestamp
        self.datetime = datetime.datetime.strptime(granule_timestamp, '%Y%m%dT%H%M%S')

    def plot_cloud_mask(self,cmap_name='Greys_r'):
        """
        Plot the cloud mask using imshow.
        """
        # fig, ax = plt.subplots()
        # cloud_mask = self.cld_mask.cloud_flag.values
        # cf = ax.imshow(cloud_mask, origin='lower')
        # ax.set_title('Cloud Mask (0: clear, 1: cloudy)')
        # plt.colorbar(cf, ax=ax)


        # fig, ax = plt.subplots()
        # ax.pcolormesh(self.cld_mask_geo.longitude, self.cld_mask_geo.latitude, self.cld_mask.cloud_flag, shading="nearest", rasterized=True)
        # ax.set_aspect("equal")
        
        data = self.cld_mask.cloud_flag.values
        cmap = plt.get_cmap(cmap_name, np.nanmax(data) - np.nanmin(data) + 1)
        # set limits .5 outside true range
        fig,ax=plt.subplots()
        mat = ax.pcolormesh(self.cld_mask_geo.longitude, self.cld_mask_geo.latitude, data,
                             cmap=cmap, vmin=np.nanmin(data) - 0.5, 
                             vmax=np.nanmax(data) + 0.5,shading="nearest", rasterized=True)
        ax.set_aspect("equal")
        cax = plt.colorbar(mat, ax=ax,ticks=np.arange(np.nanmin(data), np.nanmax(data) + 1))
    
        plt.show()

    def plot_cloud_prop(self,cmap_name='jet'):
        """
        Plot cloud phase, cloud optical thickness, and cloud effective radius.
        """
        from matplotlib import colors
        fig, axes = plt.subplots(1, 3, figsize=(15, 4))  # Using one figure with multiple subplots
        
        # Cloud phase
        ax = axes[0]
        ax.set_title('Cloud Phase for 2.1µm retrievals \n 0 - no cloud mask, 1 - clear, 2 - water cloud, 3 - ice cloud, 4 - unknown')
        data = self.cld_prop.cld_phase_21.values
        cmap = plt.get_cmap(cmap_name, np.nanmax(data) - np.nanmin(data) + 1)
        # set limits .5 outside true range
        # fig,ax=plt.subplots()
        mat = ax.pcolormesh(self.cld_mask_geo.longitude, self.cld_mask_geo.latitude, data,
                             cmap=cmap, vmin=np.nanmin(data) - 0.5, 
                             vmax=np.nanmax(data) + 0.5,shading="nearest", rasterized=True)
        ax.set_aspect("equal")
        cax = plt.colorbar(mat, ax=ax,ticks=np.arange(np.nanmin(data), np.nanmax(data) + 1))

        
        # ax.imshow(self.cld_prop.cld_phase_21.values, origin='lower')
        # plt.colorbar(ax.imshow(self.cld_prop.cld_phase_21.values, origin='lower'), ax=ax)

        # Cloud optical thickness with logarithmic scale
        ax = axes[1]
        cf = ax.pcolormesh(self.cld_mask_geo.longitude, self.cld_mask_geo.latitude,self.cld_prop.cot_21.values,
                           norm=colors.LogNorm(),shading="nearest", rasterized=True)
        ax.set_title('Cloud Optical Thickness')
        plt.colorbar(cf, ax=ax)

        # Cloud effective radius
        ax = axes[2]
        cf = ax.pcolormesh(self.cld_mask_geo.longitude, self.cld_mask_geo.latitude, self.cld_prop.cer_21.values,
                          shading="nearest", rasterized=True)
        ax.set_title('Cloud Effective Radius')
        plt.colorbar(cf, ax=ax)

        plt.tight_layout()
        plt.show()
        

class HARP2_L1(object):
    def __init__(self,granule_timestamp,data_level,data_path = './',spr=False): 
        
        self.data_level = data_level
        file_pattern = f'{data_path}PACE_HARP2.{granule_timestamp}.{data_level}*.nc'
        try:
            fn = glob.glob(file_pattern)[0]
        except IndexError:
            logging.error(f'Cannot find data file: {file_pattern}')
            return
        self.HARP2_L1C_fn = fn
        self.load_data(fn)
        self.set_timestamp(granule_timestamp)
        if (self.data_level.lower()=='l1c') and spr:
            self.__scattering_plane_rotation()
            
        

    def load_data(self, filename):
        self.sensors_views_bands = xr.open_dataset(self.HARP2_L1C_fn,group='sensor_views_bands',decode_cf=True)
        self.geolocation_data = xr.open_dataset(self.HARP2_L1C_fn,group='geolocation_data',decode_cf=True)
        self.observation_data = xr.open_dataset(self.HARP2_L1C_fn,group='observation_data',decode_cf=True)  

    def set_timestamp(self, granule_timestamp):
        self.granule_timestamp = granule_timestamp
        self.datetime = datetime.datetime.strptime(granule_timestamp, '%Y%m%dT%H%M%S')
        
    def __scattering_plane_rotation(self):
        # cosine and sine of rotation angles
        C2 = np.cos(2*np.deg2rad(self.geolocation_data.rotation_angle))
        S2 = np.sin(2*np.deg2rad(self.geolocation_data.rotation_angle))

        # cosine of solar and viewing zenith angle
        self.mu0=np.cos(np.deg2rad(self.geolocation_data.solar_zenith_angle))
        self.muv=np.cos(np.deg2rad(self.geolocation_data.sensor_zenith_angle))

        # rotated Q & U from local meridian plane to scattering plane
        # Eq. 6 of PACE technical report V12
        self.q_s =  self.observation_data.q[:,:,:,0]*C2+self.observation_data.u[:,:,:,0]*S2
        self.u_s = -self.observation_data.q[:,:,:,0]*S2+self.observation_data.u[:,:,:,0]*C2
        
        # normalization factor to covert the Q&U to P12 (Eq.2 of Bréon, F. M., & Doutriaux-Boucher)
        normalization_factor = -4*(self.mu0+self.muv)/(self.mu0 * self.sensors_views_bands.intensity_f0[:,0])
        
        self.q_s_norm = self.q_s * normalization_factor
        self.u_s_norm = self.u_s * normalization_factor
        
    def plot_true_color_RGB(self,
                            save_RGB=False,
                            x0_indices=None,y0_indices=None):
        if (self.data_level.lower()=='l1c'):
            R = self.observation_data.i[:,:,40,0]
            G = self.observation_data.i[:,:,4,0]
            B = self.observation_data.i[:,:,84,0]
        else:
            R = self.observation_data.i[40,:,:]
            G = self.observation_data.i[4,:,:]
            B = self.observation_data.i[84,:,:]

        RGB = np.stack((R, G, B), axis=2)
        rhos_rgb_enhanced = normalize_rgb(R, G, B)
        
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1, projection=ccrs.PlateCarree())
        ax.pcolormesh(self.geolocation_data.longitude, self.geolocation_data.latitude, rhos_rgb_enhanced,
                      shading="nearest", rasterized=True,transform=ccrs.PlateCarree())
        ax.set_aspect("equal")
        ax.add_feature(cfeature.LAND)
        ax.add_feature(cfeature.OCEAN)
        ax.add_feature(cfeature.COASTLINE)
        ax.add_feature(cfeature.BORDERS, linestyle=':')
        #ax.add_feature(cfeature.LAKES, alpha=0.5)
        #ax.add_feature(cfeature.RIVERS)
        
        ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                          linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
        ax.scatter(self.geolocation_data.longitude[y0_indices,x0_indices],
                   self.geolocation_data.latitude[y0_indices,x0_indices], transform=ccrs.PlateCarree(),
                   c='r',alpha=0.5)
        if save_RGB:
            fig.savefig(f'PACE_HARP2_L1C_RGB_{self.granule_timestamp}.png', dpi=300)

            
  
