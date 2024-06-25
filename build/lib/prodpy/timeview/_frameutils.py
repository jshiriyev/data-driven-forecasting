import pandas

class FrameUtils():

	def __init__(self):

		pass

	def __call__(self,frame:pandas.DataFrame):
		"""frame    : The input DataFrame."""

		self._frame = frame

		return self

	@property
	def frame(self):

		return self._frame
	
	def heads(self,*args,include:tuple[str]=None,exclude:tuple[str]=None)->list[str]:
		"""
		Returns the list of arguments that are in the DataFrame and after
		including & excluding the dtypes.

		Parameters:

		*args    : Positional column names to check in the DataFrame.

		include  : Include dtypes for the head selection.
		exclude  : Exclude dtypes for the head selection.

		Return:

		A list of column names that exist in the DataFrame and that match the
		specified include and exclude criteria.
		"""

		head_list = [head for head in args if head in self.frame.columns]

		if include is None and exclude is None:
			return head_list

		head_list += self.frame.select_dtypes(include=include,exclude=exclude).columns.tolist()

		return list(set(head_list))

	def join(self,*args,**kwargs)->pandas.DataFrame:
		"""
		Joins the frame columns specified by the args and kwargs and
		returns a new joined frame.

		Parameters:

		*args    : Positional column names to check in the DataFrame.
		**kwargs : include and exclude dtypes for the head selection.

		Returns:

		The joined frame.
		"""

		heads = FrameUtils.heads(self.frame,*args,**kwargs)

		value = self.frame[heads].astype("str").agg(" ".join,axis=1)

		return pandas.DataFrame({" ".join(heads):value})

	def filter(self,column:str,*args)->pandas.DataFrame:
		"""
		Filters the non-empty input frame by checking the 
		series specified by column for args.
		
		Parameters:

		column   : Column name where to search for args
		*args    : Positional values to keep in the column series.

		Returns:

		A new filtered frame.
		"""

		bools = self.frame[column].isin(args)

		return self.frame[bools].reset_index(drop=True)

	def groupsum(self,column:str,*args):
		"""
		Groups the non-empty input frame based on column and
		returns a new frame after summing the other columns.
		
		Parameters:

		column   : Column name which to group

		Returns:

		A new summed frame.
		"""

		frame = self.filter(column,*args)

		leads = " ".join(frame[column].unique())

		frame = frame.groupby(column).sum().reset_index()

		frame[column] = leads

		return frame