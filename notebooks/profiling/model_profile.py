import cProfile, pstats, io
from pstats import SortKey
# pr = cProfile.Profile()
# pr.enable()


import sys 
sys.path.append("../..")

from cadCAD_tools import easy_run
from scipy.interpolate import interp1d

from model.functions import load_route, append_deltas
df = (load_route('../../data/uiramuta_chui.gpx').head(100)
      .pipe(append_deltas)
      .assign(total_distance=lambda df: df.delta.cumsum())
      )

elevation_interpolator = interp1d(df.total_distance, df.ele)
longitude_interpolator = interp1d(df.total_distance, df.lon)
latitude_interpolator = interp1d(df.total_distance, df.lat)

from model import initial_state, params, timestep_block


params.update(elevation_interpolator=[elevation_interpolator],
              latitude_interpolator=[latitude_interpolator],
              longitude_interpolator=[longitude_interpolator],
              dt=[0.3])

results = easy_run(initial_state,
                   params,
                   timestep_block,
                   5_000_000,
                   1,
                   assign_params=False)

# pr.disable()

# def prof_to_csv(prof: cProfile.Profile):
#     out_stream = io.StringIO()
#     pstats.Stats(prof, stream=out_stream).print_stats()
#     result = out_stream.getvalue()
#     # chop off header lines
#     result = 'ncalls' + result.split('ncalls')[-1]
#     lines = [','.join(line.rstrip().split(None, 5)) for line in result.split('\n')]
#     return '\n'.join(lines)

# csv = prof_to_csv(pr)
# with open("prof.csv", 'w+') as f:
#       f.write(csv)