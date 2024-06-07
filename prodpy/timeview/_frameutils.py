import pandas

class FrameUtils():

	@staticmethod
	def heads(frame:pandas.DataFrame,*args,include:tuple[str]=None,exclude:tuple[str]=None)->list[str]:
		"""
		Returns the list of arguments that are in the DataFrame and after
		including & excluding the dtypes.

		Parameters:

		frame    : The input DataFrame.
		*args    : Positional column names to check in the DataFrame.

		include  : Include dtypes for the head selection.
		exclude  : Exclude dtypes for the head selection.

		Return:

		A list of column names that exist in the DataFrame and that match the
		specified include and exclude criteria.
		"""

		head_list = [head for head in args if head in frame.columns]

		if include is None and exclude is None:
			return head_list

		head_list += frame.select_dtypes(include=include,exclude=exclude).columns.tolist()

		return list(set(head_list))

	@staticmethod
	def join(frame,*args,**kwargs)->pandas.DataFrame:
		"""
		Joins the frame columns specified by the args and kwargs and
		returns a new joined frame.

		Parameters:

		frame    : The input DataFrame.

		*args    : Positional column names to check in the DataFrame.
		**kwargs : include and exclude dtypes for the head selection.

		Returns:

		The joined frame.
		"""

		heads = FrameUtils.heads(frame,*args,**kwargs)

		value = frame[heads].astype("str").agg(" ".join,axis=1)

		return pandas.DataFrame({" ".join(heads):value})