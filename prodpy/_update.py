import numpy

class Update():

	@staticmethod
	def upload(state):

		df = pd.read_excel(uploaded_file)

		datecols = df.select_dtypes(include=('datetime64',)).columns
		numbcols = df.select_dtypes(include=('number',)).columns
		catgcols = df.select_dtypes(exclude=('number','datetime64')).columns

	@staticmethod
	def datekey(state):
		pass

	@staticmethod
	def ratekey(state):

		numbcols = numbcols.drop(rates_key)

	@staticmethod
	def groupkey(state):

		frame = decline.Analysis.groupby(frame,group_key)

		itemlist = frame[group_key].unique()

	@staticmethod
	def item(state):

		frame1 = dca.filter(frame,displayedItem)

		frame2,model = dca.predict(frame1,start=None,cease=None)

		title = f'{displayedItem} Rates'

	@staticmethod
	def opacity(state):

		date_min,date_max = state.time_interval_selected

		cond1 = state.datetimes >= numpy.datetime64(date_min)
		cond2 = state.datetimes <= numpy.datetime64(date_max)

		conds = numpy.logical_and(cond1,cond2)

		state['opacity'] = conds*0.7+0.3