import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State

import pandas as pd
import plotly.graph_objs as go
import numpy as np
import sys
sys.path.append('/Users/Marco/Documents/Flatiron/Course_Materials/Projects/google_maps/data')
import helpers

"""
LOAD DATA
"""

trips_df, trips_dfs = helpers.get_dfs('trips')
instr_df, instr_dfs = helpers.get_dfs('instructions')

subsets = ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon', 'Evening', 'Early Morning']

navbar = dbc.NavbarSimple(
    children=
        [
            dbc.Button("Learn More", id="learn_more"),
            dbc.Modal(
            [
                dbc.ModalHeader("Welcome"),
                dbc.ModalBody(dcc.Markdown(
                """\
My girlfriend and I live in two different NYC boroughs, making traveling between
our apartments a real pain. Although an Uber is not too expensive at off-peak
times, my method of choice is public transit since I already have a monthly
unlimited pass. It usually feels that it takes around an hour to get between
our apartments, given that I typically only make the trip on the weekends. I
propose this study to determine when are the quickest and most efficient times
to travel between our apartments using Google Maps.
                """)
                ),
                dbc.ModalFooter(
                    dbc.Button("Close", id="close", className="ml-auto")
                ),
            ],
            id="modal",
            centered=True
        ),
        ],
    brand="Transit Travel Time Optimization",
    brand_href='https://github.com/msanchez-ayala/google_maps',
    dark=True,
    sticky="top",
    color='rgb(247,181,41)'
)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
body = dbc.Container(
    [
        dbc.Row(
            [
                html.H4('Trip Breakdown'),
            ],
            justify='center',
            style={
                'padding':'15px 0px'
            }
        ),
        dbc.Row(
            [
                dbc.Col([
                    dcc.Dropdown(
                        id='subset',
                        options=[{'label':subset, 'value':subset} for subset in subsets],
                        value='All Trips')
                ])
            ]
        ),
        dbc.Row(
            [
                dbc.Col(
                    [
                        dcc.Graph(
                            id="trip_ts",
                            hoverData={'points':'data'},
                            )
                    ],
                    width=7,
                ),
                dbc.Col(
                    [
                        dcc.Graph(id="box_plots")
                    ],
                    width=5
                )
            ]
        ),
        dbc.Row(
            [
                html.H4('Instructions Breakdown')
            ],
            justify='center',
            style={
                'padding':'15px 0px'
            }
        ),
    ]
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([navbar, body])

"""
CALLBACKS
"""
@app.callback(
    Output("modal", "is_open"),
    [Input("learn_more", "n_clicks"), Input("close", "n_clicks")],
    [State("modal", "is_open")],
)
def toggle_modal(n1, n2, is_open):
    if n1 or n2:
        return not is_open
    return is_open

@app.callback(
    dash.dependencies.Output('trip_ts', 'figure'),
    [dash.dependencies.Input('subset', 'value')]
    )

def update_ts(subset):
    """
    RETURNS
    -------
    A time series of trip durations for the two DataFrames within trips_dfs.

    PARAMETERS
    ----------
    subset: [str] Denotes the subset these dfs belong to. Can be one of:
            ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon',
            Evening', 'Early Morning']

    trips_dfs: [list] two DataFrames, one being the trip to gf slice and the
        other being trip to me slice. These dfs must already have all of the
        engineered features from create_features().
    """
    trace = []

    for df in trips_dfs:

        trace.append(go.Scatter(
            x = df.departure_time,
            y = df.trip_duration,
            name = df['trip_direction_text'].values[0], # Legend labels for this trace
        ))

    layout = go.Layout(dict(
                        title = f'Transit Trip Duration for {subset}' if subset else 'Transit Trip Duration',
                        template = "plotly_white",
                        # margin={'t':70,'l':60,'b':40},
                        xaxis_title = 'Departure Time',
                        yaxis_title = 'Minutes',
                        legend_orientation='h',
                        legend=dict(x=0.1, y=1.1)
                        # xaxis_showgrid=False,
                        # yaxis_ticks='outside',
                        # yaxis_tickcolor='white',
                        # yaxis_ticklen=10,
                        # yaxis_zeroline=True,
                        # legend={'orientation':'h',},
                        # xaxis_range=xaxis_range,
                        # height = height,  #600
                        ))

    return {'data': trace, 'layout': layout}

@app.callback(
    dash.dependencies.Output('box_plots', 'figure'),
    [dash.dependencies.Input('subset', 'value')]
    )

def update_box_plots(subset):
    """
    RETURNS
    -------
    A figure comparing box plots of trip duration for the two DataFrames in
    trips_dfs.

    PARAMETERS
    ----------
    trips_dfs: [list] two DataFrames, one being the trip to gf slice and the other being trip to me slice.
         These dfs must already have all of the engineered features from create_features().

    subset: [str] Denotes the subset these dfs belong to. Can be one of:
            ['All Trips', 'Weekdays', 'Weekends', 'Morning', 'Afternoon', 'Evening', 'Early Morning']

    """
    trace = []

    for df in trips_dfs:

        trace.append(go.Box(
            y = df.trip_duration,                    # y values for this trace
            name = df.trip_direction_text.values[0], # x label for this trace
        ))


    layout = go.Layout(dict(
                        title = f'Transit Trip Duration for {subset}' if subset else 'Transit Trip Duration',
                        template = "plotly_white",
                        # margin={'t':70,'l':60,'b':40},
                        xaxis_title = 'Minutes',
                        showlegend=False,
                        # yaxis_ticks='outside',
                        # yaxis_tickcolor='white',
                        # yaxis_ticklen=10,
                        # yaxis_zeroline=True,
                        # legend={'orientation':'h',},
                        # xaxis_range=xaxis_range,
                        # height = height,  #600
                        ))

    return {'data': trace, 'layout': layout}


if __name__ == '__main__':
    app.run_server(debug=True)
