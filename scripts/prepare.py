
import requests as req
import gpxpy
from geopy.distance import geodesic
import pandas as pd
import numpy as np
from scipy.optimize import brentq
import plotly.express as px
import plotly.graph_objects as go
from tqdm.auto import tqdm

# Parameters
route_path = '../data/rodotreta.gpx'
TOTAL_WEIGHT = 70
CRR = 0.007
CDA = 0.32
INEFFICIENCY = 1.03
RHO = 1.226

# Pacing strategies
STRATEGIES = {'uphill': {'filter': lambda x: x >= 0.5,
                         'power': 125},
              'flat': {'filter': lambda x: (x < 0.5) & (x > -0.5),
                       'power': 100},
              'downhill': {'filter': lambda x: x <= -0.5,
                           'power': 25}}


def power_gravitational(speed, grad, weight=TOTAL_WEIGHT):
    """
    Power for winning gravity
    """
    return 9.8067 * weight * speed * np.sin(np.arctan(grad))


def power_wind(speed, cda=CDA, rho=RHO):
    """
    Power for winning wind
    """
    return 0.5 * rho * cda * (speed ** 3)


def power_rolling(speed, grad, crr=CRR, weight=TOTAL_WEIGHT):
    """
    Power for winning tyres
    """
    return 9.8067 * crr * speed * np.cos(np.arctan(grad)) * weight


def power(speed, grad):
    """
    Overral power
    """
    return (power_gravitational(speed, grad)
            + power_wind(speed)
            + power_rolling(speed, grad)) * INEFFICIENCY


def speed(_power, grad):
    """
    Speed given an power and a grad.
    """
    def optimize_function(speed, grad): return _power - power(speed, grad)
    return brentq(optimize_function, -0.01, 100.0, grad)


def gradient(df):
    N = 15
    return 100 * df.ele.diff().rolling(N).mean() / df.delta.rolling(N).mean()


def calculate_speeds(df):
    # Get the speeds for the route given the pacing strategies
    output = {}
    for strategy, params in tqdm(STRATEGIES.items()):
        grads = df.where(lambda df: params['filter'](df.grad)).grad.dropna()
        speeds = grads.apply(lambda grad: speed(
            params['power'], grad / 100) * 3.6)
        output[strategy] = speeds
        df.loc[grads.index, 'speed'] = speeds
    # Summary
    for strategy, out in output.items():
        print("{}: {:.0f} ({:.0f} to {:.0f}) km/h".format(strategy,
                                                          out.median(), out.quantile(0.05), out.quantile(0.95)))
    speeds = pd.concat(output.values())
    return speeds


def calculate_deltas(df):
    deltas = {}
    for i, (ind, row) in tqdm(enumerate(df.iterrows()),
                              total=len(df),
                              desc='Calculating deltas'):
        lat2 = row.lat
        lon2 = row.lon
        if i > 0:
            delta = geodesic((lat1, lon1), (lat2, lon2)).meters
            deltas[ind] = delta
        (lat1, lon1) = (lat2, lon2)
    return deltas


def load_route(content=False):
    if content is False:
        with open(route_path, 'r') as fid:
            content = fid.read()
    gpx = gpxpy.parse(content)

    route_points = gpx.tracks[0].segments[0].points
    df = (pd.DataFrame([(p.longitude, p.latitude, p.elevation) for p in route_points],
                       columns=['lon', 'lat', 'ele'])
          .drop_duplicates(subset=['lat', 'lon'])
          )
    deltas = calculate_deltas(df)
    df = df.join(pd.Series(deltas, name='delta'))
    df = df.assign(grad=gradient)
    df['grad'] = df.grad
    speeds = df.pipe(calculate_speeds)

    df = df.assign(total_distance=df.delta.cumsum() / 1000)
    df = df.assign(duration=df.delta / (1000 * df.speed))
    df = df.assign(total_duration=df.duration.cumsum())
    df = df.assign(days=df.total_duration // 8)
    df = df.assign(hours=df.total_duration // 1)
    return df
