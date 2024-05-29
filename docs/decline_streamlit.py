import datetime

import sys

sys.path.append(r'C:\Users\3876yl\Documents\prodpy')
# sys.path.append(r'C:\Users\user\Documents\GitHub\prodpy')

import time

import pandas

import plotly.graph_objects as go

import streamlit as st

import streamlit.components.v1 as components

from prodpy import timeview as tv

from prodpy import decline as dc

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

st.session_state = tv.Session(st.session_state).set()
st.session_state = dc.Session(st.session_state).set()

if "models" not in st.session_state:
	st.session_state["models"] = {}

with st.sidebar:

	st.header(
		body = 'Input Data',
		)

	file = st.file_uploader(
		label = 'Upload your input excel file',
		type = ['csv','xlsx'],
		)

	data = tv.Update.load_data(file)

	st.header(
		body = 'Feature Selection',
		)

	datehead = st.selectbox(
		label = "Choose Date Column:",
		options = data.datetimes,
		index = None,
		key = 'datehead',
		)

	if datehead is not None:
		data = data(datehead=datehead)

	ratehead = st.selectbox(
		label = 'Choose Rate Column:',
		options = data.numbers,
		index = None,
		key = 'ratehead',
		)

	nominals = st.multiselect(
		label = "Choose Groupby Columns:",
		options = data.nominals,
		key = 'nominals',
		)

	table = tv.Update.load_table(st.session_state,data)

	st.header(
		body = 'Item Selection:',
		)

	itemname = st.selectbox(
		label = 'Select Item:',
		options = table.items,
		index = None,
		key = 'itemname'
		)

	view = tv.Update.load_view(st.session_state,table)

	st.header(
		body = 'Timeseries View',
		)

	viewlist = st.multiselect(
		label = 'Add to the Plot:',
		options = data.minors(st.session_state.ratehead),
		key = 'viewlist',
		)

displayColumn, modelColumn = st.columns([0.7,0.3],gap='large')

with modelColumn:

	st.header('Decline Curve Analysis')

	analysis = dc.Update.load_analysis(st.session_state)

	st.slider(
		label = "Time Interval:",
		min_value = view.limit[0],
		max_value = view.limit[1],
		key = 'estimate',
		on_change = dc.Update.slider,
		args = (st.session_state,),
		)

	opacity = dc.Update.load_opacity(st.session_state,analysis(view.frame))

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

	FitGroupButton = st.button(
		label = "Fit Group",
		help = "Optimize all group items.",
		use_container_width = True,
		)

	if FitGroupButton:

		if table.empty:
			st.warning("No data to optimize.")

		else:

			st.session_state.models = {}

			optimization_text = "Optimization in progress. Please wait."

			bar1 = st.progress(0.,text=optimization_text)
			
			for index,scene in enumerate(table,start=1):

				model = dc.Update.load_best_model(
					st.session_state,analysis(scene.frame)
					)

				st.session_state.models[scene.items[0]] = model

				bar1.progress(value=index/table.num,text=optimization_text)

			time.sleep(1)
		
			bar1.empty()

			st.success(f"Models for {table.leadhead.replace("_"," ")} are calculated.")

	dc.Update.model(st.session_state,analysis(view.frame),itemname)

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

	estimate_curve = dc.Update.load_estimate_curve(st.session_state)

	SaveModelEditButton = st.button(
		label = "Save Edits",
		help = "Save decline attribute edits for the item.",
		use_container_width = True,
		)

	if SaveModelEditButton:

		if itemname is None:
			st.warning("No item is selected.")
		else:
			try:
				st.session_state.models[itemname] = dc.Update.load_user_model(st.session_state)
			except Exception as message:
				st.warning(message)
			else:
				st.success(f"The model for {itemname} is updated.")

	st.markdown("""---""")

	forecast_show = st.checkbox(
		label = "Display Forecasted Rates",
		)

	if forecast_show:
		xaxis_range = [
			min(st.session_state.forecast[0],view.limit[0]),
			max(st.session_state.forecast[1],view.limit[1])
			]
	else:
		xaxis_range = list(view.limit)

	nextyear = datetime.datetime.now().year+1

	forecast = st.date_input(
		"Forecast Interval",
		value = (datetime.date(nextyear,1,1),datetime.date(nextyear,12,31)),
		key = 'forecast',
		format="MM.DD.YYYY",
	)

	if len(forecast)!=2:
		st.warning("Input start and end of the forecast period.")

	forecast_frequency = st.selectbox(
		label = 'Forecast Frequency:',
		options = pandas.offsets.__all__,
		key = 'frequency'
		)

	freq = getattr(pandas.offsets,forecast_frequency)._prefix

	forecast_curve = dc.Update.load_forecast_curve(st.session_state)

	DownloadButton = st.button(
		label = 'Download Forecast',
		help = "Download predicted rates for all group items.",
		use_container_width = True,
		)

	if DownloadButton:

		if len(st.session_state.models)==0:
			st.warning('No model to forecast.')
		else:

			forecast_text = "Forecast in progress. Please wait."

			bar2 = st.progress(0.,text=forecast_text)

			for index,(name,model) in enumerate(st.session_state.models.items(),start=1):

				minor = analysis.run(model,forecast,freq=freq)

				minor.insert(0,'Names',name)

				if index==1:
					frame = minor.copy()
				else:
					frame = pandas.concat([frame,minor])

				frame = pandas.concat([frame,minor])

				bar2.progress(value=index/len(st.session_state.models),text=forecast_text)

			time.sleep(1)

			output = frame.to_csv(index=False).encode('utf-8')

			components.html(
				dc.Update.load_download(output,f"{table.leadhead}_forecast.csv"),
				height=0,
			)

			bar2.empty()

with displayColumn:

	if view.frame.empty:

		st.title("Welcome to the Decline Curve Analysis App.")
		st.markdown("""
			### Please upload your data to get started.

			1. **Upload your production test file** using the sidebar.
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

	if not view.frame.empty:

		st.header(f'{itemname} Rates')

		figMajor = go.Figure()

		observed_plot = go.Scatter(
			x = view.frame[datehead],
			y = view.frame[ratehead],
			mode = 'markers',
			marker = dict(opacity=opacity),
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
				marker = dict(opacity=opacity),
				)

			figMinor.add_trace(data_vis)

			figMinor.update_xaxes(range=xaxis_range)

			figMinor.update_layout(
				title = ratename,
				)

			st.plotly_chart(figMinor,use_container_width=True)
