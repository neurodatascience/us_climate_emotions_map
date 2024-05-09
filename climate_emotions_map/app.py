"""Main file to run the Dash app."""

import os

import dash_mantine_components as dmc
from dash import Dash

from .layout import construct_layout

# Currently needed by DMC, https://www.dash-mantine-components.com/getting-started#simple-usage
os.environ["REACT_VERSION"] = "18.2.0"

app = Dash(
    __name__,
    title="US Climate Emotions Map",
)

app.layout = dmc.MantineProvider(construct_layout(), forceColorScheme="light")

server = app.server

if __name__ == "__main__":
    app.run(debug=True)
