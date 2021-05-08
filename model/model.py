
from cadCAD_tools import easy_run
import plotly.express as px
import numpy as np
from math import degrees, radians, atan2
from random import random

N_timestep = 1000
N_samples = 10

initial_state = {
    'position': 0.0, # m
    'speed': 0.0, # m/s
    'energy': 0.0, # J
    'wind_speed': 0.0, # m/s
    'wind_angle': 0.0, # rad
    'incline': radians(-5) # rad
}

params = {
    'gravity': 9.81, # m/s^2
    'rolling_resistance': 0.005, # 
    'wind_resistance': 0.25, # m^2, Also know as CdA 
    'mass': 65, # kg
    'dt': 0.1 # Seconds
}

params = {k: [v] for k, v in params.items()}

def p_rolling_resistance(params, _2, _3, state):
    m = params['mass']
    g = params['gravity']
    R = params['rolling_resistance']
    v = state['speed']
    
    power = -1 * m * g * R * v
    return {'power': power}
    

def p_wind_resistance(params, _2, _3, state):
    A = params['wind_resistance']
    w = state['wind_speed']
    phi = state['wind_angle']
    v = state['speed']
    
    power = -1 * v * A * (v - w * np.cos(phi)) ** 2
    return {'power': power}


def p_gravity(params, _2, _3, state):
    m = params['mass']
    g = params['gravity']
    theta = state['incline']
    v = state['speed']
    
    power = -1 * m * g * v * np.sin(theta)  
    return {'power': power}
    
    
def p_power_output(params, _2, _3, state):
    v = state['speed']
    theta = state['incline']
    
    speed_in_km_h = v * 3.6 
    gradient = degrees(theta)
    
    if gradient > 2.0:
        output = 170
    elif gradient > 0.5:
        output = 140
    elif gradient > -0.5:
        output = 90
    elif gradient < -2.0:
        output = 30
    elif gradient < -4.0:
        output = 0
    else:
        output = 50 * (v + 4) # This is going to be negative
             
    if output > 0:
        if speed_in_km_h > 40:
            output = -1 * 5 * (speed_in_km_h - 40)
        else:
            pass
    else:
        pass
    
    return {'power': output}

def s_integrate_energy(params, _2, _3, state, p_i):
    energy_change = p_i['power'] * params['dt']
    new_energy = state['energy'] + energy_change
    return ('energy', new_energy)


def s_position(params, _2, _3, state, _5):
    dt = params['dt']
    x = state['position']
    v = state['speed']
    new_x = x + v * dt
    return ('position', new_x)

def s_speed(params, _2, _3, state, _5):
    m = params['mass']
    E = state['energy']
    v = np.sqrt(2 * E / m)
    return ('speed', v)


def s_seconds(params, _2, _3, state, _5):
    seconds_per_t = params['dt']
    t = state['timestep']
    seconds = seconds_per_t * t
    return ('seconds_passed', seconds)


def s_incline(params, _2, history, state, _5):

    if interpolator := params.get('elevation_interpolator', False):
        past_x = history[-1][0]['position']
        current_x = state['position']
        dx = current_x - past_x

        past_elevation = interpolator(current_x - dx)
        current_elevation = interpolator(current_x)
        dy = current_elevation - past_elevation
        value = atan2(dy, dx)
    else:
        scale = 2
        random_value = (random() - 0.5) * scale # between -1 and +1
        value = radians(random_value)
    return ('incline', value)
    

def s_wind_speed(_1, _2, _3, _4, _5):
    scale = 6
    random_value = (random() - 0.5) * scale # between -3 and +3
    value = random_value
    return ('wind_speed', value)


def s_wind_angle(_1, _2, _3, _4, _5):
    scale = 360
    random_value = (random() - 0.5) * scale # between -180 and +180
    value = radians(random_value)
    return ('wind_angle', value)
    
    
timestep_block = [
    {
        'label': 'Time',
        'policies': {
            
        },
        'variables': {
            'seconds_passed': s_seconds
        }
    },
    {
        'label': 'Environment',
        'policies': {
            
        },
        'variables': {
            'incline': s_incline,
            'wind_speed': s_wind_speed,
            'wind_angle': s_wind_angle
        }
    },
    {
        'label': 'Energy',
        'policies': {
            'rolling_resistance': p_rolling_resistance,
            'wind_resistance': p_wind_resistance,
            'gravity': p_gravity,
            'output_power': p_power_output 
            
        },
        'variables': {
            'energy': s_integrate_energy
        }
        
    },
    {
        'label': 'Motion',
        'policies': {

        },
        'variables': {
            'position': s_position,
            'speed': s_speed
        }
    }
]