# %%
import numpy as np
# %%
import xarray as xr
PATH = '../data/wind.grib'
raw_ds = xr.load_dataset(PATH, engine='cfgrib')

# %%
ds = raw_ds.isel(step=0)

# %%
I = (ds.u10 ** 2 + ds.v10 ** 2) ** (1 / 2)
# %%
ang = np.arctan2(ds.u10, ds.v10) % 3.14

# %%
ds = xr.merge([I.rename('wind_speed'), ang.rename('wind_angle')])
output = []
for month, monthly_ds in ds.groupby(ds.time.dt.month):
    hourly_ds = monthly_ds.groupby(monthly_ds.time.dt.hour)
    mean_data = hourly_ds.mean()
    std_data = hourly_ds.std()

    agg_ds = xr.merge([mean_data.wind_speed.rename('mean_wind_speed'),
                    std_data.wind_speed.rename('std_wind_speed'),
                    mean_data.wind_angle.rename('mean_wind_angle'),
                    std_data.wind_angle.rename('std_wind_angle')])
    agg_ds = agg_ds.assign_coords(month=month)
    output.append(agg_ds)
# %%
output_xr = xr.concat(output, dim='month')
# %%
output_xr.to_netcdf('../data/agg_ds.nc')


# %%
