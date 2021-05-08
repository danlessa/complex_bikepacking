# %%
import pandas as pd
%load_ext autotime

# %%

col = 'filename:lineno(function)'


def f(x):
    if 'cadCAD' in x:
        return 'cadCAD'
    elif 'gpxpy' in x:
        return 'gpxpy'
    elif 'model/model.py' in x:
        return 'model'
    else:
        return 'other'


df = (pd.read_csv('prof.csv')
      .sort_values('tottime', ascending=False)
      .assign(kind=lambda df: df[col].map(f)))

df.groupby('kind').tottime.sum()

# %%
