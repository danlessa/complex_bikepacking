import dash
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px

from prepare import load_route
import pandas as pd
import numpy as np

df = load_route()

app = dash.Dash(__name__)


def map_fig(df):
    fig = px.scatter_mapbox(lat=df.lat,
                            lon=df.lon,
                            color=df.speed.map(lambda x: x if x < 30 else 30).map(
                                lambda x: x if x > 15 else 15)
                            )
    fig.update_layout(mapbox_style="stamen-terrain",
                      margin={"r": 0, "t": 0, "l": 0, "b": 0})
    return fig


def wind_speed_fig(N=100):
    x = np.round(np.random.rand(N) * 23)
    y = np.sin(x / 3 + np.random.randn(N) / 1) + \
        np.cos(x / 3 + np.random.rand(N))
    df = pd.DataFrame(zip(x, y), columns=['x', 'y']).sort_values('x')
    fig = px.box(data_frame=df,
                 x=df.x.map(lambda x: f"{x :02.0f}:00"),
                 y='y',
                 labels={'x': 'TOD',
                              'y': 'Intensity (m/s)'})
    return fig


def wind_radar_fig():
    df = px.data.wind()
    fig = px.bar_polar(df, r="frequency", theta="direction",
                       color="strength",
                       color_discrete_sequence=px.colors.sequential.Plasma_r)
    return fig


app.layout = html.Div([
    dcc.Upload(
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
    ),
    dcc.Graph(id='graph_map',
              figure=map_fig(df)),
    dcc.Graph(id='hourly_dist',
              figure=wind_speed_fig()),
    dcc.Graph(id='wind_direction',
              figure=wind_radar_fig())
])


@app.callback(
    Output('hourly_dist', 'figure'),
    [Input('graph_map', 'clickData')])
def display_click_data(clickData):
    return wind_speed_fig()


if __name__ == '__main__':
    app.run_server(debug=True,
                   host='0.0.0.0')
