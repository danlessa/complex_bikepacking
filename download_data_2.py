import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-land',
    {
        'format': 'grib',
        'variable': [
            '10m_u_component_of_wind', '10m_v_component_of_wind', 'skin_temperature',
            'total_precipitation',
        ],
        'year': [
            '2017', '2018', '2019',
        ],
        'month': [
            '07', '08', '09',
        ],
        'day': [
            '01', '07', '13',
            '19', '25',
        ],
        'time': [
            '00:00', '02:00', '04:00',
            '06:00', '08:00', '10:00',
            '12:00', '14:00', '16:00',
            '18:00', '20:00', '22:00',
        ],
        'area': [
            5.5, -70, -34,
            -48,
        ],
    },
    'download.grib')