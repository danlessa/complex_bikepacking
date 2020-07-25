# %%


# %%
import plotly.express as px
import xarray as xr
import numpy as np
import pandas as pd
ds = xr.open_dataset('../data/agg_ds.nc')


def get_wind_metrics(ds, lat, lon, hour, month=None):
    if month is not None:
        summary = ds.sel(latitude=lat, longitude=lon,
                         hour=hour, month=month, method='nearest')  # %%
        m = summary.mean_wind_speed.values
        s = summary.std_wind_speed.values
        wind_speeds = np.random.randn(200) * s + m
        m = summary.mean_wind_angle.values
        s = summary.std_wind_angle.values
        wind_angles = np.random.randn(200) * s + m
        df = pd.DataFrame(zip(wind_speeds, 360 * wind_angles / (3.14)),
                          columns=['wind_speed', 'wind_angle'])
    else:
        df = ds.sel(latitude=lat, longitude=lon, hour=24,
                    method='nearest').to_dataframe().reset_index()
        N = 200
        months = []
        speeds = []
        angles = []
        for month, summary in df.iterrows():
            m = summary.mean_wind_speed * 3.6
            s = summary.std_wind_speed * 3.6
            wind_speeds = np.random.randn(N) * s + m
            m = summary.mean_wind_angle * (360 / 3.14)
            s = summary.std_wind_angle * (360 / 3.14)
            wind_angles = np.random.randn(N) * s + m
            months += (N * [month])
            speeds += (list(wind_speeds))
            angles += (list(wind_angles))
        data = [months, speeds, angles]
        df = pd.DataFrame(
            zip(*data),  columns=['month', 'wind_speed', 'wind_angle'])

    return df


# %%

# %%
lat = -10
lon = -30
df = get_wind_metrics(ds, lat, lon, 12).dropna()
df = df.groupby(15 * (df.wind_angle // 15)).wind_speed.count()
df /= len(df)
fig = px.bar_polar(df.reset_index(), r="wind_speed", theta="wind_angle")
fig.show()
# %%
# %%
hourly_df
# %%
hourly_wind_speed = {hour: get_wind_metrics(ds, lat, lon, hour).assign(hour=hour)
                     for hour
                     in range(0, 24)}

hourly_df = pd.concat(hourly_wind_speed.values())

fig = px.violin(hourly_df,
             x=hourly_df.hour.map(lambda x: f"{x :02.0f}:00"),
             y=hourly_df.wind_speed,
             labels={'x': 'TOD',
                     'y': 'Intensity (m/s)'})
fig.show()

# %%
hourly_df
# %%
pd.DataFrame(hourly_wind_speed.values())
# %%
px.histogram(wind_angles)
# %%
df.angle.min()

# %%
