import datetime

import pandas

import plotly.graph_objects as go

from plotly.subplots import make_subplots

def plotly_template(frame:pandas.DataFrame):

    fig = make_subplots(rows=4, cols=1, shared_xaxes=True, vertical_spacing=0.02,
        specs=[[{}], [{"secondary_y": True}], [{"secondary_y": True}], [{}]])

    plot1 = go.Scatter(
        x = frame["DATE"],
        y = frame["OIL TONS/DAY"],
        mode = 'markers',
        marker = dict(color='blue', size=2),
        name = 'Oil Tons/day'
        )

    plot21 = go.Scatter(
        x = frame["DATE"],
        y = frame["WATER M3/DAY"],
        mode = 'markers',
        marker = dict(size=2,color='blue'),
        name = 'Water m3/day',
        )

    plot22 = go.Scatter(
        x = frame["DATE"],
        y = frame["GAS KM3/DAY"],
        mode = 'markers',
        marker = dict(size=3, color='red'),
        name = 'Gas km3/day',
        yaxis = 'y2'
        )

    plot31 = go.Scatter(
        x = frame["DATE"],
        y = frame["CHOCKE"],
        mode = 'markers',
        marker = dict(size=2,color='blue'),
        name = 'Chocke')

    plot32 = go.Scatter(
        x = frame["DATE"],
        y = frame["DAYS"],
        mode = 'markers', 
        marker = dict(size=3,color='red'),
        name = 'Operation Days',
        yaxis = 'y2')

    plot4 = go.Scatter(
        x = frame["DATE"],
        y = frame["METHOD"],
        mode = 'lines', 
        line = dict(color='blue',width=1),
        name = 'Lift Method',
        )

    fig.add_trace(plot1,row=1,col=1)
    fig.add_trace(plot21,row=2,col=1)
    fig.add_trace(plot22,row=2,col=1,secondary_y=True)
    fig.add_trace(plot31,row=3,col=1)
    fig.add_trace(plot32,row=3,col=1,secondary_y=True)
    fig.add_trace(plot4,row=4,col=1)

    fig.update_xaxes(showticklabels=True, row=1, col=1)  # Hide on top plot

    fig.update_yaxes(title_text="OIL TONS/DAY", row=1, col=1)
    fig.update_yaxes(title_text="WATER M3/DAY", row=2, col=1)
    fig.update_yaxes(title_text="GAS KM3/DAY", row=2, col=1, secondary_y=True, showgrid=False)
    fig.update_yaxes(title_text="CHOCKE", row=3, col=1)
    fig.update_yaxes(title_text="DAYS", row=3, col=1, secondary_y=True, showgrid=False)
    fig.update_yaxes(title_text="LIFT METHOD", row=4, col=1)

    fig.add_vline(x=datetime.date.today(),line=dict(color='red',dash='dash',width=0.5))

    fig.update_layout(height=1200,showlegend=False)

    return fig