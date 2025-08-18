import pandas as pd

import plotly.graph_objects as go

def plot3(tops: pd.DataFrame, perfs: pd.DataFrame):
	"""
	Plot formation tops and perforation intervals on a single depth track.

	tops columns (default):
		- formation (str)
		- depth_md (float)

	perfs columns (default):
		- perf_top_md (float)
		- perf_bot_md (float)

	Returns: Plotly Figure

	"""
	# Defensive copies and sorting
	T = tops[["formation", "depth"]].dropna().copy()
	T = T.sort_values("depth")

	P = perfs[["top", "base", "guntype"]].dropna().copy()
	P = P.sort_values("top")

	fig = go.Figure()

	# --- 1) Add formation tops as horizontal dashed lines with labels on the left
	for _, row in T.iterrows():
		y = float(row["depth"])
		name = str(row["formation"])

		fig.add_shape(
			type="line",
			x0=0.16, x1=1.0,
			y0=y, y1=y,
			line=dict(dash="dash", width=1.5),
			)

		fig.add_annotation(
			x=0.15, y=y,
			text=name,
			showarrow=False,
			xanchor="right",
			yanchor="middle"
		)

	# --- 2) Add perforation intervals as a right-side vertical bar (rectangle shapes)
	# We'll place the bar between x=0.65 and x=0.95
	x0, x1 = 0.17, 0.95
	for _, row in P.iterrows():
		y0 = float(row["top"])
		y1 = float(row["base"])
		# Ensure correct ordering
		if y1 < y0:
			y0, y1 = y1, y0

		# Shape for the interval
		fig.add_shape(
			type="rect", xref="x", yref="y",
			x0=x0, x1=x1, y0=y0, y1=y1,
			line=dict(width=1),
			fillcolor="firebrick",
			opacity=0.35,
		)

	# --- 3) Dummy legend entries
	fig.add_trace(go.Scatter(
		x=[None], y=[None], mode="lines",
		line=dict(dash="dash"),
		name="Formation Top"
	))
	fig.add_trace(go.Scatter(
		x=[None], y=[None], mode="lines",
		line=dict(width=10, color="firebrick"),
		name="Perforation Interval"
	))

	# --- 4) Layout / axes
	fig.update_layout(
		height=600,
		margin=dict(l=80, r=80, t=70, b=40),
		hovermode="closest",
		legend=dict(orientation="h", x=0, y=1.08, xanchor="left", yanchor="bottom"),
	)

	# Depth axis: reversed (increasing downwards)
	fig.update_yaxes(
		autorange="reversed",
		showgrid=True,
		zeroline=False
	)

	# X axis: hide ticks/labels (just a track)
	fig.update_xaxes(
		range=[0, 1],
		showgrid=False,
		showticklabels=False,
		zeroline=False,
		title_text=""
	)

	return fig