import csv
import pandas as pd
import plotly.plotly as py
import plotly.graph_objs as go

from pandas.api.types import CategoricalDtype

from shared import prep_yoy_data


def plot_diffs(monthly_diffs):
    monthly_diffs['hover_text'] = monthly_diffs.apply(
        lambda row: '{} -> {}: {}\n2017:{} \n2018:{}'.format(
            row['from_station_full'],
            row['to_station_full'],
            row['diff_2017_to_2018'],
            row[2017],
            row[2018]
        ),
        axis=1
    )

    monthly_diffs = monthly_diffs.sort_values(by=['categorical_from_station', 'categorical_dest_station'])

    only_march = monthly_diffs[monthly_diffs['month_number'] == 3]
    max_diff = max(
        only_march['diff_2017_to_2018'].max(),
        -only_march['diff_2017_to_2018'].min()
    )

    trace = go.Heatmap(
        z=only_march['diff_2017_to_2018'],
        x=only_march['categorical_from_station'],
        y=only_march['categorical_dest_station'],

        # This is pretty confusing, but basically we pass two arguments to set the hover text:
        # 1. The actual thing to display, as the `text` attribute
        # 2. What field should be displayed upon hover - here, the `text` attribute, which we've
        # just set.
        text=only_march['hover_text'],
        hoverinfo='text',
        # https://plot.ly/python/reference/#scatter-marker-colorscale
        # colorscale=build_color_scale_from_z_vals(only_march['diff_2017_to_2018']),

        # EXPLAIN THIS
        zmin = -max_diff,
        zmax = max_diff

        # reversescale=True # default makes Blue == fewer riders, Red == more riders
    )

    data = [trace]
    layout = go.Layout(
        xaxis = {
            'tickangle': 45,
        }
    )
    figure = go.Figure(data=data, layout=layout)

    # ...could we animate this???
    print py.plot(figure, filename='python-yoy-diffs-heatmap-example')

if __name__ == '__main__':
    # plot_via_pandas()
    yoy_data = prep_yoy_data()
    yoy_data.to_csv('data/2017_2018_yoy_data.csv', index=False)
    plot_diffs(yoy_data)
