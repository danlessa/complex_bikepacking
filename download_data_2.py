import cdsapi

c = cdsapi.Client()

c.retrieve(
    'reanalysis-era5-pressure-levels',
    {
        'product_type': 'reanalysis',
        'format': 'grib',
        'variable': [
            'relative_humidity', 'temperature', 'u_component_of_wind',
            'v_component_of_wind',
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
            '00:00', '03:00', '06:00',
            '09:00', '12:00', '15:00',
            '18:00', '21:00',
        ],
        'area': [
            5.5, -70, -48,
            -34,
        ],
    },
    'download.grib')