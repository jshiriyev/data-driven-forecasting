import pandas

class utils:
	
	def heads(frame,*args,include:tuple[str]=None,exclude:tuple[str]=None)->list[str]:
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
		head_list = [head for head in args if head in frame.columns]

		if include is None and exclude is None:
			return head_list

		head_list += frame.select_dtypes(include=include,exclude=exclude).columns.tolist()

		return list(set(head_list))

	def join(frame,*args,separator=None,**kwargs)->pandas.DataFrame:
		"""
		Joins the frame columns specified by the args and kwargs and
		returns a new joined frame.

		Parameters:

		*args    : Positional column names to check in the DataFrame.
		**kwargs : include and exclude dtypes for the head selection.

		Returns:

		The joined frame.

		"""
		heads = utils.heads(*args,**kwargs)

		separator = " " if separator is None else separator

		value = frame[heads].astype("str").agg(separator.join,axis=1)

		return pandas.DataFrame({separator.join(heads):value})

	def filter(frame,column:str,*args)->pandas.DataFrame:
		"""
		Filters the non-empty input frame by checking the 
		series specified by column for args.
		
		Parameters:
		----------
		column   : Column name where to search for args
		*args    : Positional values to keep in the column series.

		Returns:
		-------
		A new filtered frame.
		
		"""
		return frame[frame[column].isin(args)].reset_index(drop=True)

	def groupsum(frame,column:str,*args,separator=None):
		"""
		Groups the non-empty input frame based on column and
		returns a new frame after summing the other columns.
		
		Parameters:
		----------
		column   : Column name which to group
		*args    : Positional values to keep in the column series.

		Returns:
		-------
		A new summed frame.

		"""
		frame = utils.filter(frame,column,*args)

		separator = " " if separator is None else separator

		frame[column] = separator.join(frame[column].unique())

		frame = frame.groupby(column).sum().reset_index(drop=True)

		return frame

if __name__ == "__main__":

	import pandas as pd

	frame = {
		"name" : ["john","smith","python","john","georgina"],
		"age"  : [32,47,23,25,23],
		"rate" : [1.,5.,6.,8.5,9],
		}

	frame = pd.DataFrame(frame)

	utils = FrameUtils()

	print(frame)

	print(utils(frame).heads('name','age',exclude='number'))

	print(utils(frame).join('name','age',separator="#"))

	print(utils(frame).filter("name","john","georgina"))

	print(utils(frame).groupsum("name","john","georgina"))