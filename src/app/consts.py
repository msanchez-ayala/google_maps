"""
Constants for app.py (and also download_storage.py at the bottom).
"""

### COLORS ###

colors = dict(
    blue = 'rgb(66,133,244)',
    red = 'rgb(219,68,55)',
    yellow = 'rgb(244,180,0)',
    green = 'rgb(15,157,88)'
)

graph_colors = [colors['blue'], colors['yellow']]

### DROPDOWN ###

dropdown_options = [
    {'label': 'Max Trip Duration', 'value': 'max'},
    {'label': 'Mean Trip Duration', 'value': 'mean'},
    {'label': 'Median Trip Duration', 'value': 'median'},
    {'label': 'Min Trip Duration', 'value': 'min'},
]
dropdown_width = '50%'


### GRAPH LAYOUTS ###

title_x_pos = 0.5
title_x_anchor = 'center'
