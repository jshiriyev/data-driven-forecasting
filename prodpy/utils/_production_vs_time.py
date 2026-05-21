import datetime

import pandas as pd

import plotly.graph_objects as go

from plotly.subplots import make_subplots

def plot1(frame:pd.DataFrame):

    d = frame.copy()

    fig = make_subplots(rows=6, cols=1, shared_xaxes=True, vertical_spacing=0.02,
        specs=[[{"secondary_y": True}]]*6)

    plot01 = go.Scatter(
        x = d.date, y = d.orate, mode = 'lines',
        line = dict(color='green'),
        name = 'Oil Tons/day'
        )

    plot02 = go.Scatter(
        x = d.date, y = d.wrate, mode = 'lines',
        line = dict(color='blue'),
        name = 'Water m3/day',
        )

    plot03 = go.Scatter(
        x = d.date, y = d.grate, mode = 'lines',
        line = dict(color='red'),
        name = 'Gas th. m3/day',
        )

    plot04 = go.Scatter(
        x = d.date, y = d.choke, mode = 'lines',
        line = dict(color='blue'),
        name = 'Choke',
        )

    plot05 = go.Scatter(
        x = d.date, y = d.days, mode = 'lines', 
        line = dict(color='black'),
        name = 'Operation Days',
        )

    plot06 = go.Scatter(
        x = d.date, y = d['mode'], mode = 'lines', 
        line = dict(color='blue',width=1),
        name = 'Lift Method',
        )

    fig.add_trace(plot01,row=1,col=1)
    fig.add_trace(plot02,row=2,col=1)
    fig.add_trace(plot03,row=3,col=1)
    fig.add_trace(plot04,row=4,col=1)
    fig.add_trace(plot05,row=5,col=1)
    fig.add_trace(plot06,row=6,col=1)

    fig.update_xaxes(showticklabels=True, row=1, col=1)  # Hide on top plot

    fig.update_yaxes(title_text="OIL TONS/DAY", row=1, col=1, secondary_y=False)
    fig.update_yaxes(title_text="WATER M3/DAY", row=2, col=1, secondary_y=False)
    fig.update_yaxes(title_text="GAS th. M3/DAY", row=3, col=1, secondary_y=False)
    fig.update_yaxes(title_text="CHOKE", row=4, col=1, secondary_y=False)
    fig.update_yaxes(title_text="DAYS", row=5, col=1, secondary_y=False)
    fig.update_yaxes(title_text="LIFT METHOD", row=6, col=1, secondary_y=False)

    fig.add_vline(x=datetime.date.today(),line=dict(color='red',dash='dash',width=0.5))

    fig.update_layout(height=1200,showlegend=False)

    return fig

def plot2(frame:pd.DataFrame):

    d = frame.copy()

    fig = make_subplots(specs=[[{"secondary_y": True}]])

    # Oil (primary)
    fig.add_trace(
        go.Scatter(
            x=d.date, y=d.orate,
            mode="lines",
            name="Oil (ton/day)",
            hovertemplate="%{x|%Y-%m-%d}<br>Oil: %{y:.2f} ton/day<extra></extra>",
            line=dict(color='green'),
        ),
        secondary_y=False,
    )

    # Water (primary)
    fig.add_trace(
        go.Scatter(
            x=d.date, y=d.wrate,
            mode="lines",
            name="Water (m³/day)",
            hovertemplate="%{x|%Y-%m-%d}<br>Water: %{y:.2f} m³/day<extra></extra>",
            line=dict(color='blue')
        ),
        secondary_y=False,
    )

    # Gas (secondary)
    fig.add_trace(
        go.Scatter(
            x=d.date, y=d.grate,
            mode="lines",
            name="Gas (km³/day)",
            hovertemplate="%{x|%Y-%m-%d}<br>Gas: %{y:.4f} km³/day<extra></extra>",
            line=dict(color='red'),
        ),
        secondary_y=True,
    )

    fig.update_layout(
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="left", x=0),
        hovermode="x unified",
        margin=dict(l=60, r=60, t=60, b=40),
        height=520,
        xaxis=dict(
            rangeselector=dict(
                buttons=list([
                    dict(count=1, label="1m", step="month", stepmode="backward"),
                    dict(count=3, label="3m", step="month", stepmode="backward"),
                    dict(count=6, label="6m", step="month", stepmode="backward"),
                    dict(count=1, label="YTD", step="year", stepmode="todate"),
                    dict(count=1, label="1y", step="year", stepmode="backward"),
                    dict(step="all")
                ]),
                x=0.95,xanchor="auto",
                y=1.05,yanchor="top",
            ),
            rangeslider=dict(visible=True,thickness=0.06),
            type="date",
        )
    )

    fig.update_yaxes(title_text="Oil (ton/day) & Water (m³/day)", secondary_y=False)
    fig.update_yaxes(title_text="Gas (km³/day)", secondary_y=True)

    return fig