import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.express as px

import xarray as xr
from prepare import load_route
import pandas as pd
import numpy as np
import base64

from io import StringIO


def get_wind_metrics(ds, lat, lon, hour):
    summary = ds.sel(latitude=lat, longitude=lon,
                     hour=hour, method='nearest')  # %%
    m = summary.mean_wind_speed.values * 3.6
    s = summary.std_wind_speed.values * 3.6
    wind_speeds = np.random.randn(2000) * s + m
    m = summary.mean_wind_angle.values
    s = summary.std_wind_angle.values
    wind_angles = np.random.randn(5000) * s + m
    return wind_speeds, wind_angles


def map_fig(df):
    fig = px.scatter_mapbox(lat=df.lat,
                            lon=df.lon,
                            color=df.speed.map(lambda x: x if x < 30 else 30).map(
                                lambda x: x if x > 15 else 15)
                            )
    fig.update_layout(mapbox_style="stamen-terrain",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def wind_speed_fig(agg_ds, lat, lon):
    hourly_wind_speed = {hour: get_wind_metrics(agg_ds, lat, lon, hour)[0]
                         for hour
                         in range(0, 24)}

    hourly_df = (pd.DataFrame(hourly_wind_speed)
                 .stack()
                 .reset_index()
                 .rename(columns={0: 'wind_speed', 'level_1': 'hour'}))

    fig = px.box(x=hourly_df.hour.map(lambda x: f"{x :02.0f}:00"),
                 y=hourly_df.wind_speed,
                 labels={'x': 'TOD',
                         'y': 'Intensity (m/s)'})
    return fig


def wind_radar_fig(agg_ds, lat, lon, hour):
    wind_speeds, wind_angles = get_wind_metrics(agg_ds, lat, lon, 12)
    df = pd.DataFrame(zip(wind_speeds, 360 * wind_angles / (3.14)),
                      columns=['speed', 'angle'])
    df = df.groupby(15 * (df.angle // 15)).speed.count().reset_index()
    df['speed'] /= len(df)
    fig = px.bar_polar(df, r="speed", theta="angle")
    return fig


df = load_route()
agg_ds = xr.open_dataset('../data/agg_ds.nc')
CSS_LINKS = ['https://codepen.io/danilolessa/pen/JjGxwmX.css']
app = dash.Dash(__name__,  external_stylesheets=CSS_LINKS)

default_lat = -10
default_lon = -30
default_hour = 12


app.layout = html.Div([
    html.Div([dcc.Upload(
        id='gpx_file',
        children=html.Div([
            'Drag and Drop or ',
            html.A('Select Files')
        ]),
        style={
            'width': '100%',
            'height': '60px',
            'lineHeight': '60px',
            'borderWidth': '1px',
            'borderStyle': 'dashed',
            'borderRadius': '5px',
            'textAlign': 'center',
            'margin': '10px'
        }
    )]),

    html.Div([dcc.Graph(id='graph_map',
                        figure=map_fig(df))]),

    html.Div([dcc.Graph(id='hourly_dist',
                        figure=wind_speed_fig(agg_ds, default_lat, default_lon)),
              dcc.Graph(id='wind_direction',
                        figure=wind_radar_fig(agg_ds, default_lat, default_lon, default_hour))],
             id='wind_row')
])


@app.callback(
    [Output('hourly_dist', 'figure'),
     Output('wind_direction', 'figure')],
    [Input('graph_map', 'clickData')])
def display_click_data(clickData):
    lat = default_lat
    lon = default_lon
    if clickData is not None:
        point = clickData['points'][0]
        lat = point['lat']
        lon = point['lon']
    hourly_dist_fig = wind_speed_fig(agg_ds, lat, lon)
    wind_direction_fig = wind_radar_fig(agg_ds, lat, lon, 12)
    return hourly_dist_fig, wind_direction_fig


@app.callback(
    Output("graph_map", "figure"),
    [Input("gpx_file", "filename"), Input("gpx_file", "contents")],
)
def update_output(_, content):
    """Save uploaded files and regenerate the file list."""
    if content is not None:
        _, content_string = content.split(',')
        decoded = base64.b64decode(content_string)
        df = load_route(decoded)
    else:
        df = load_route()
    return map_fig(df)


if __name__ == '__main__':
    app.run_server(debug=True,
                   host='0.0.0.0')
