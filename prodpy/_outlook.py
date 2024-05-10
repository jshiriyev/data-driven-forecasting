import pandas

class Outlook():
	
	@staticmethod
	def dates(frame:pandas.DataFrame):
		return [] if frame is None else frame.select_dtypes(
			include=('datetime64',)).columns.tolist()

	@staticmethod
	def numbers(frame:pandas.DataFrame):
		return [] if frame is None else frame.select_dtypes(
			include=('number',)).columns.tolist()
	
	@staticmethod
	def groups(frame:pandas.DataFrame):
		return [] if frame is None else frame.select_dtypes(
			exclude=('number','datetime64')).columns.tolist()

	@staticmethod
	def items(frame:pandas.DataFrame,groupkey:str=None):
		return [] if frame is None or groupkey is None else frame[groupkey].unique()

	@staticmethod
	def groupby(frame:pandas.DataFrame,*args,datekey:str=None):
		"""Groupby the frame for the groupkey (args) and datekey."""
		return frame if frame is None or datekey is None else frame.groupby(list(args)+[datekey])

	@staticmethod
	def merge(frame:pandas.DataFrame,*args):
		"""Sums the number columns (args) of grouped frame and resets the index."""
		return frame[list(args)].sum().reset_index()

	@staticmethod
	def plottable(frame:pandas.DataFrame,*args):
		"""Return columns with number excluding the key column"""
		return Bundle.numbers(frame).drop(list(args)).tolist()

	def get(self,frame,**kwargs):
		"""Groupby and filters input frame based on key-value pair of the first optional argument.

		frame 	: panda DataFrame

		Returns a new frame with the given value in the first column, date in the second column, and
		Analysis heads in the rest of the columns.
		"""

		for key,value in kwargs.items():
			break

		frame = self.groupby(frame,key)
			
		return self.filter(frame,value)

	def filter(self,frame,value:str):
		"""Filters input frame based on the first column and the input value.

		frame 	: panda DataFrame

		Returns a new frame with the given value in the first column, date in the second column, and
		Analysis heads in the rest of the columns.
		"""
		return frame[frame.iloc[:,0]==value].reset_index(drop=True)

if __name__ == "__main__":

	df = pandas.read_excel(r"C:\Users\user\Downloads\ACG_decline_curve_analysis.xlsx")

	# columns = Bundle.plottable(df,'Actual Oil, Mstb/d','Actual Gas Lift, MMscf/d')

	print(Bundle.items(df,'Field'))
	print(type(Bundle.items(df,'Field').tolist()))

