import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

class Charts():

	@staticmethod
	def pie(
		labels,
		sizes,
		*,
		colors=None,
		explode=None,
		title="Well Stock History",
		shadow=True,
		startangle=140,
		figsize=(6, 6),
		autopct_values=True
	):
		"""
		Plot a pie chart showing well distribution.

		Parameters
		----------
		labels : list[str]
			Names of categories (e.g., ['Water Injector', 'Gas Producer', 'Oil Producer']).
		sizes : list[int or float]
			Values corresponding to each label.
		colors : list[str], optional
			Slice colors. If None, matplotlib default cycle is used.
		explode : tuple, optional
			Explode fraction for each slice (same length as labels).
		title : str
			Title of the pie chart.
		shadow : bool
			Whether to draw a shadow behind the pie.
		startangle : float
			Start angle of the first slice.
		figsize : tuple
			Size of the matplotlib figure.
		autopct_values : bool
			If True, display absolute numbers instead of percentages.
		"""

		def autopct_format(values):
			def my_format(pct):
				total = sum(values)
				val = int(round(pct * total / 100.0))
				return f"{val:d}"
			return my_format

		fig, ax = plt.subplots(figsize=figsize)

		ax.pie(
			sizes,
			explode=explode,
			labels=labels,
			colors=colors,
			shadow=shadow,
			startangle=startangle,
			autopct=autopct_format(sizes) if autopct_values else "%1.1f%%"
		)

		ax.axis("equal")  # Equal aspect ratio ensures the pie is circular
		plt.title(title)
		plt.show()

		return fig, ax

	@staticmethod
	def tornado(
		df: pd.DataFrame,
		*,
		activity_col: str = "activities",
		p10_col: str = "P10",
		p50_col: str = "P50",
		p90_col: str = "P90",
		p50s_col: str = "P50s",
		p10_total: str = "3497 MTon",
		p50_total: str = "3487 MTon",
		p90_total: str = "3480 MTon",
		colors: dict = None,
		xy_ticklabel_color: str = "#101628",
		figsize=(10, 6),
	):
		"""
		Plot a wing chart comparing P10 / P50 / P90 values for activities.

		Parameters
		----------
		df : DataFrame
			Must include activity_col, p10_col, p50_col, p90_col, p50s_col
		activity_col, p10_col, p50_col, p90_col, p50s_col : str
			Column names for chart components.
		p10_total, p50_total, p90_total : str
			Text annotations for totals.
		colors : dict
			Example: {"P10": "#00A86B", "P90": "#FF2800"}
		xy_ticklabel_color : str
			Color for labels and ticks.
		figsize : tuple
			Size of the matplotlib figure.
		"""
		if colors is None:
			colors = {"P10": "#00A86B", "P90": "#FF2800"}

		# Sort values by P50 for visual consistency
		df_sorted = df.sort_values(by=p50_col, ascending=True).reset_index(drop=True)

		# Compute symmetric wing axis range
		max_wing_value = df_sorted[[p90_col, p10_col]].max().max()
		power = -int(np.floor(np.log10(abs(max_wing_value))))
		max_wing_value = (np.ceil(max_wing_value * 10**power) / 10**power).tolist()

		fig, ax = plt.subplots(figsize=figsize)

		# Plot each row as a wing
		for idx, row in df_sorted.iterrows():
			ax.barh(row[activity_col], -row[p90_col], align="center", height=0.5, facecolor=colors["P90"])
			ax.barh(row[activity_col],  row[p10_col], align="center", height=0.5, facecolor=colors["P10"])

			# Labels for wings
			ax.text(-row[p90_col] - 0.4, idx, row[p90_col],
					ha="left", va="center", color=xy_ticklabel_color, size=11)
			ax.text(row[p10_col] + 0.4, idx, row[p10_col],
					ha="right", va="center", color=xy_ticklabel_color, size=11)

			# Activity name
			ax.text(0., idx + 0.35, s=row[activity_col],
					ha="center", size=11, color=xy_ticklabel_color)

			# P50 string inside bar
			ax.text(0.2, idx, row[p50s_col],
					ha="center", va="center", size=11,
					weight="bold", color="white")

		N = len(df_sorted)

		# Headings for P10 / P90
		ax.text(max_wing_value,  N, "P10", size=16, weight="bold", ha="center")
		ax.text(-max_wing_value, N, "P90", size=16, weight="bold", ha="center")

		# Arrow markers
		ax.add_patch(plt.Arrow(0, N, -1, 0, width=0.2, color=colors["P90"]))
		ax.plot(0, N + 0.0001, "o", markersize=6, color="white")
		ax.add_patch(plt.Arrow(0, N, 1, 0, width=0.2, color=colors["P10"]))

		# Totals
		ax.text(max_wing_value,  N - 0.3, p10_total, ha="center", size=11)
		ax.text(0,			   N + 0.2, p50_total, ha="center", size=11)
		ax.text(-max_wing_value, N - 0.3, p90_total, ha="center", size=11)

		# Axis cosmetics
		ax.set_ylim((-1, N + 1))
		ax.set_yticks([])
		ax.set_xticks([])
		ax.set_xlim((-max_wing_value - 1, max_wing_value + 1))

		plt.show()

		return fig, ax

	@staticmethod
	def waterfall(
		df: pd.DataFrame,
		*,
		category_col: str = "category",
		value_col: str = "value",
		start_color: str = "#808080",	 # starting bar color
		increase_color: str = "#4CAF50",  # positive deltas
		decrease_color: str = "#FF5733",  # negative deltas
		final_color: str = "#808080",	 # final/total bar color
		edgecolor: str = "black",
		linewidth: float = 1.0,
		figsize=(10, 6),
		rotation: int = 45,
		value_fmt: str = "{:.0f}",		# format string for value labels
		show_values: bool = True,
		ylim_pad: float = 0.08			# padding fraction on y-limits
	):
		"""
		Plot a waterfall chart.

		Expects df with:
		  - category_col: ordered categories (start ... steps ... final)
		  - value_col: deltas; if the last row is NaN, it will be treated as the final total bar.

		Returns
		-------
		fig, ax : matplotlib Figure, Axes
		"""

		# Work on a copy
		data = df[[category_col, value_col]].copy().reset_index(drop=True)

		# Determine if last row is a "final" total bar (value is NaN)
		has_final = data[value_col].isna().iloc[-1]

		# Compute cumulative and shifted (starting point for each bar)
		data["value_filled"] = data[value_col].fillna(0.0)
		data["cumulative"] = data["value_filled"].cumsum()
		data["shifted"] = data["cumulative"].shift(fill_value=0.0)

		n = len(data)
		x = np.arange(n)

		# Heights & bottoms for bars
		heights = data["value_filled"].to_numpy().copy()
		bottoms = data["shifted"].to_numpy().copy()

		# If final bar exists (last value NaN), draw it as total = last shifted
		if has_final:
			heights[-1] = data["shifted"].iloc[-1]
			bottoms[-1] = 0.0

		# Colors
		colors = np.where(heights >= 0, increase_color, decrease_color).tolist()
		colors[0] = start_color
		if has_final:
			colors[-1] = final_color

		# Plot
		fig, ax = plt.subplots(figsize=figsize)
		ax.bar(x, heights, bottom=bottoms, color=colors, edgecolor=edgecolor, linewidth=linewidth)

		# Labels on bars
		if show_values:
			for i, (h, b, v) in enumerate(zip(heights, bottoms, data[value_col].fillna(data["shifted"]).to_numpy())):
				# For final bar, label the total; for others, label the delta
				label_value = data["shifted"].iloc[i] if (has_final and i == n - 1 and pd.isna(df[value_col].iloc[-1])) else v
				if h >= 0:
					yy = b + h
					va = "bottom"
					offset = 3
				else:
					yy = b + h
					va = "top"
					offset = -3
				ax.text(
					x[i],
					yy + (offset if offset > 0 else 0),
					value_fmt.format(label_value),
					ha="center",
					va=va
				)

		# Cosmetics
		ax.set_ylabel("value")
		ax.set_xticks(x)
		ax.set_xticklabels(data[category_col], rotation=rotation, ha="right")

		# Compute y-limits with padding
		y_min = np.minimum(bottoms, bottoms + heights).min()
		y_max = np.maximum(bottoms, bottoms + heights).max()
		pad = (y_max - y_min) * float(ylim_pad) if y_max > y_min else 1.0
		ax.set_ylim(y_min - pad, y_max + pad)

		plt.tight_layout()

		return fig, ax

if __name__ == "__main__":

	# # PIE CHART

	# labels = ['Water Injector', 'Gas Producer', 'Oil Producer']
	# sizes = [53, 105, 339]
	# colors = ['#66b3ff','#99ff99','#ff9999']
	# explode = (0.1, 0.1, 0.1)  # Explode the 1st slice (i.e. 'Category A')

	# Charts.pie(
	# 	labels,
	# 	sizes,
	# 	colors=colors,
	# 	explode=explode,
	# 	title="Well Stock History"
	# )

	# # TORNADO CHART

	# data = {
	# 	"activities": ["Baza Hasilatı", "Geoloji tədbirlər", "Qazma+Yan lülə", "Texniki tədbirlər"],
	# 	"P90": [3.7, 0.6, 1.5, 1.6],
	# 	"P50": [3256., 194., 8., 30.],
	# 	"P10": [3.8, 2.7, 1.0, 2.1],
	# 	"P50s": ["3256 MTon", "194 MTon", "8 MTon", "30 MTon"]
	# }

	# df = pd.DataFrame(data)

	# Charts.tornado(
	# 	df,
	# 	p10_total="3497 MTon",
	# 	p50_total="3487 MTon",
	# 	p90_total="3480 MTon"
	# )

	# WATERFALL CHART

	data = {
		'category': [
			'Starting Value',
			'Increase A',
			'Decrease B',
			'Increase C',
			'Decrease D',
			'Final Value'],
		'value': [100, 30, -20, 40, -10, np.nan]
	}

	df = pd.DataFrame(data)

	fig, ax = Charts.waterfall(
	    df,
	    category_col="category",
	    value_col="value",
	    start_color="#808080",
	    increase_color="#4CAF50",
	    decrease_color="#FF5733",
	    final_color="#808080",
	    value_fmt="{:.0f}",     # change to "{:.1f}" if you want decimals
	)

	plt.show()