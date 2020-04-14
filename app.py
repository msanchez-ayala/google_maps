"""
This module controls the Dash app that can be viewed from the browser.

Author: M. Sanchez-Ayala (04/14/2020)
"""

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import pandas as pd
import plotly.graph_objs as go
import app_helpers


### LOAD DATA ###


tod_df = app_helpers.create_df()
time_series_fig = app_helpers.time_series_main(tod_df)
stats_figs = app_helpers.stats_main(tod_df, 'mean')


### APP ###

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
    color='rgb(66,133,244)'
)

# external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
body = dbc.Container(
    [
        dbc.Row(
            [
                html.H4('Overview'),
            ],
            justify='center',
            style={
                'padding':'15px 0px'
            }
        ),
        dbc.Row(
            dcc.Graph(
                id='time_series',
                figure = time_series_fig,
                style = {'width':'100%'}
            )
        ),
        dbc.Row(
            dcc.Graph(
                id='hour_breakdown',
                figure= stats_figs['hour'],
                style = {'width':'100%'}
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id = 'day_breakdown',
                        figure= stats_figs['day'],
                        style = {'width':'100%'}
                    ),
                    width = 7
                ),
                dbc.Col(
                    dcc.Graph(
                        id = 'is_weekday_breakdown',
                        figure= stats_figs['is_weekday'],
                        style = {'width':'100%'}
                    ),
                    width = 5
                )
            ]
        ),
    ]
)

app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])
app.layout = html.Div([navbar, body])

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
