import datetime

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import pandas

import plotly.graph_objects as go

import streamlit as st

from prodpy import timeview as tv

from prodpy import decline as dc

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

# st.session_state = tv.Session(st.session_state).set()
st.session_state = dc.Session(st.session_state).set()

with st.sidebar:

	st.header(body='Data Input')

	with st.expander("Upload File",expanded=True):

		file = st.file_uploader(
			label = "Input csv or excel file",
			type = ['csv','xlsx'],
			)
	
		data = tv.Request.data(file)

	st.header(body='Data Preparation')

	with st.expander("Feature Selection",expanded=True):

		datehead = st.selectbox(
			label = "Choose Date Column:",
			options = data.datetimes,
			index = None,
			key = 'datehead',
			)

		data = data(datehead=datehead)
		
		ratehead = st.selectbox(
			label = 'Choose Rate Column:',
			options = data.numbers,
			index = None,
			key = 'ratehead',
			)

	with st.expander("Grouping and Filtering",expanded=False):

		leadlist = st.multiselect(
			label = "Choose Group-by Item:",
			options = data.nominals,
			key = 'leadlist',
			)

		itemlist = st.multiselect(
			label = 'Choose Filter Item:',
			options = data.items(*leadlist),
			key = 'itemlist'
			)

		view = tv.Request.view(data,*leadlist)

	st.header(body='Display Options')

	with st.expander("Timeseries Display",expanded=True):

		viewlist = st.multiselect(
			label = 'Add to the Plot:',
			options = data.heads(st.session_state.ratehead),
			key = 'viewlist',
			)

displayColumn, modelColumn = st.columns([0.7,0.3],gap='large')

with modelColumn:

	st.header('Decline Curve Analysis')

	# analysis = dc.Request.analysis(st.session_state)

	# st.subheader(body='Estimation Settings',divider='gray')

	with st.expander("Estimation Settings",expanded=True):

		st.slider(
			label = "Time Interval:",
			min_value = view.limit[0],
			max_value = view.limit[1],
			key = 'estimate',
			on_change = dc.Update.slider,
			args = (st.session_state,),
			)

		# opacity = dc.Request.opacity(st.session_state,analysis(view.frame))

		st.selectbox(
			label = "Decline Mode",
			options = dc.Model.options,
			key = 'mode',
			on_change = dc.Update.mode,
			args = (st.session_state,),
			)

		st.number_input(
			label = 'Decline Exponent %',
			min_value = 0,
			max_value = 100,
			key = 'exponent',
			step = 5,
			on_change = dc.Update.exponent,
			args = (st.session_state,),
			)

		optimize_group_button = st.button(
			label = "Fit Group",
			help = "Optimize all group items.",
			use_container_width = True,
			)

		# model = dc.Request.best_model(st.session_state,analysis(view.frame))
		model = dc.Model()

		# dc.Update.model(st.session_state,model)

		st.text_input(
			label = 'Initial Rate',
			key = 'rate0',
			on_change = dc.Update.attributes,
			args = (st.session_state,),
			)

		st.text_input(
			label = 'Initial Decline Rate',
			key = 'decline0',
			on_change = dc.Update.attributes,
			args = (st.session_state,),
			)

		# estimate_curve = dc.Request.estimate_curve(st.session_state)

		save_edits_button = st.button(
			label = "Save Edits",
			help = "Save decline attribute edits for the item.",
			use_container_width = True,
			)

	# st.subheader(body='Forecast Settings',divider='gray')

	with st.expander("Forecast Settings"):

		forecast_show = st.checkbox(
			label = "Display Forecasted Rates",
			)

		nextyear = datetime.datetime.now().year+1

		forecast = st.date_input(
			label = "Forecast Interval",
			value = (datetime.date(nextyear,1,1),datetime.date(nextyear,12,31)),
			key = 'forecast',
			format="MM.DD.YYYY",
		)

		forecast_frequency = st.selectbox(
			label = 'Forecast Frequency:',
			options = pandas.offsets.__all__,
			key = 'frequency'
			)

		# forecast_curve = dc.Request.forecast_curve(st.session_state)

		forecast_group_button = st.button(
			label = 'Run Group Forecast',
			help = "Calculates predicted rates for all group items.",
			use_container_width = True,
			)

		download_button = st.download_button(
			label = "Download Forecast",
			data = pandas.DataFrame().to_csv().encode("utf-8"),#st.session_state.output,
			help = "Download predicted rates for all group items.",
			# file_name = f"{table.leadhead}_forecast.csv",
			disabled = True, #disabled
			use_container_width = True,
			)

with displayColumn:

	if view.frame.empty:

		st.title("Welcome to the Production Data Analysis App.")
		st.markdown("""
			### Please upload your data to get started.

			1. **Upload your production test file** using the sidebar to the left.
			2. **Select the necessary features** for analysis.
			3. **Generate the forecast** in the analysis column to the right.

			### Tips for Best Results:
			- Select relevant features that significantly impact your analysis.

			### Need Help?
			- Contact me at shiriyevcavid@gmail.com.

			""")

			# - Check out the [sample dataset](sample_dataset.xlsx) to try the app.
			# - Watch the tutorial video below.

		# st.video("https://www.youtube.com/watch?v=your_tutorial_video")

	else:

		st.header(f'{itemname} Rates')

		figMajor = go.Figure()

		observed_plot = go.Scatter(
			x = view.frame[datehead],
			y = view.frame[ratehead],
			mode = 'markers',
			# marker = dict(opacity=opacity),
			)

		figMajor.add_trace(observed_plot)

		if estimate_curve is not None:

			estimate_plot = go.Scatter(
				x = estimate_curve['Dates'],
				y = estimate_curve['Rates'],
				mode = 'lines',
				line = dict(color="black"),
				)

			figMajor.add_trace(estimate_plot)

		if forecast_show and forecast_curve is not None:
			forecast_plot = go.Scatter(
				x = forecast_curve['Dates'],
				y = forecast_curve['Rates'],
				mode = 'lines',
				line = dict(color="red"),
				)

			figMajor.add_trace(forecast_plot)

		figMajor.update_xaxes(range=xaxis_range)

		figMajor.update_layout(
			title = f'{st.session_state.ratehead}',
			showlegend = False,
	        )

		st.plotly_chart(figMajor,use_container_width=True)

		for ratename in viewlist:

			figMinor = go.Figure()

			data_vis = go.Scatter(
				x = view.frame[datehead],
				y = view.frame[ratename],
				mode = 'markers',
				# marker = dict(opacity=opacity),
				)

			figMinor.add_trace(data_vis)

			figMinor.update_xaxes(range=xaxis_range)

			figMinor.update_layout(
				title = ratename,
				)

			st.plotly_chart(figMinor,use_container_width=True)
