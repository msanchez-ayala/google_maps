"""
This module controls the Dash app that can be viewed from the browser.

Author: M. Sanchez-Ayala (04/14/2020)
"""

import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output, State
import plotly.graph_objs as go
import app_helpers
from constants import *


### LOAD DATA ###


tod_df = app_helpers.create_df()
time_series_fig = app_helpers.time_series_main(tod_df)


### APP ###

navbar = dbc.NavbarSimple(
    children =
        [
            dbc.Button("Learn More", id="learn_more"),
            dbc.Modal(
            [
                dbc.ModalHeader("Welcome"),
                dbc.ModalBody(dcc.Markdown(
                """\
This dashboard serves to compare travel times at a glance. You can visualize
different statistics below!

Note: "Starting location A" implies that the trip describes going from location A
to location B and vice versa.
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
    brand = "Transit Travel Time Optimization",
    brand_href = 'https://github.com/msanchez-ayala/google_maps',
    dark = True,
    sticky = "top",
    color = colors['blue']
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
                'padding-top':'15px'
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
            dcc.Dropdown(
                id = 'stats_dropdown',
                options = dropdown_options,
                value = "mean",
                style={'width': dropdown_width}
            ),

        ),
        dbc.Row(
            dcc.Graph(
                id ='hour_breakdown',
                # figure = stats_figs['hour'],
                style = {'width':'100%'}
            )
        ),
        dbc.Row(
            [
                dbc.Col(
                    dcc.Graph(
                        id = 'day_breakdown',
                        # figure = stats_figs['day'],
                        style = {'width':'100%'}
                    ),
                    width = 7
                ),
                dbc.Col(
                    dcc.Graph(
                        id = 'is_weekday_breakdown',
                        # figure = stats_figs['is_weekday'],
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
    dash.dependencies.Output('hour_breakdown', 'figure'),
    [dash.dependencies.Input('stats_dropdown', 'value')]
)
def update_hour_breakdown(stat):
    return app_helpers.stats_main(tod_df, stat, 'hour')

@app.callback(
    dash.dependencies.Output('day_breakdown', 'figure'),
    [dash.dependencies.Input('stats_dropdown', 'value')]
)
def update_hour_breakdown(stat):
    return app_helpers.stats_main(tod_df, stat, 'day')

@app.callback(
    dash.dependencies.Output('is_weekday_breakdown', 'figure'),
    [dash.dependencies.Input('stats_dropdown', 'value')]
)
def update_hour_breakdown(stat):
    return app_helpers.stats_main(tod_df, stat, 'is_weekday')

if __name__ == '__main__':
    app.run_server(host='0.0.0.0', port=8050, debug=True)
