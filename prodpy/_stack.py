from typing import Union, List, Dict

import pandas

class StackedTables():

    def __init__(self,printFlag:bool=True):
        """Initializes the StackedTables class.

        The class assumes that the Excel sheet contains tables listed from top to bottom, where:
        - Each table includes a title, column headers, and table entries.
        - The tables are separated by empty rows, which will be detected automatically by the function.
        - If the tables are not separated by empty rows, the user needs to manually specify the row numbers for the intervals using *args.
        
        Parameters:        
        - printFlag     : bool, if True, prints information during processing (default is True).

        """
        self.printFlag = printFlag

    def _extract(self,frame:pandas.DataFrame,*args) -> Dict[str,pandas.DataFrame]:
        """
        Function to read an Excel sheet, process the data, and return a dictionary of DataFrames for specified intervals.

        Parameters:
        - frame         : Raw DataFrame
        - *args 		: Optional row index intervals for manually specifying table locations.

        Returns:
        - A dictionary where keys are the first column's value from each interval, and values are the corresponding DataFrame.
        """

        # If no intervals are provided, identify intervals based on empty rows
        if len(args) == 0:

        	# Identify rows that are entirely empty (all values are NaN)
        	empty_rows = frame.index[frame.isnull().all(axis=1)].tolist()

        	# Ensure the first interval starts from the first row if there are no empty rows at the top
        	if empty_rows[0] != 0:
        		empty_rows.insert(0,-1)

        	# Ensure the last interval ends at the last row if there are no empty rows at the bottom
        	if empty_rows[-1] != len(frame):
        		empty_rows.append(len(frame))

        	# Create intervals by pairing up consecutive empty rows, ignoring single-row gaps
        	args = [[empty_rows[i]+1,empty_rows[i+1]] for i in range(len(empty_rows)-1) if empty_rows[i+1]-empty_rows[i]>1]

        # Dictionary to store tables (DataFrames) based on the first column value of each interval
        tables = {}

        # Loop through each interval and process the data
        for interval in args:
            # Extract rows from the specified interval and reset the index
            table = frame.iloc[interval[0]+1:interval[1]].reset_index(drop=True)

            # Set the first row as column headers
            table.columns = table.iloc[0].tolist()

            # Use the first column's value as the key and store the processed table
            tables[frame.iloc[interval[0]][0]] = table.iloc[1:].reset_index(drop=True)

        # If printFlag is True, print the titles of the frames
        if self.printFlag:
        	print(f"The title of frames are {list(tables.keys())}",end="\n\n")

        # Return the dictionary of tables
        return tables

    def _process(self,**kwargs) -> Dict[str,pandas.DataFrame]:
        """
        Function to process tables (output of the 'extract' function) by cleaning up any columns
        that contain only missing values and return the updated tables:
        - Removing columns that contain only NaN values.
        - Setting the first column as the index (assuming it's datetime).
        - Converting all values to numeric, coercing errors.

        Parameters:
        - **kwargs : dictionary of DataFrames, where each key is a table title, and each value is the corresponding table.

        Returns:
        - The updated tables with columns containing only NaN values removed, returned as separate arguments.
        """

        tables = {}

        # Loop through each table using the key (table title)
        for index,(key,frame) in enumerate(kwargs.items()):
            # Drop columns that contain only missing values (NaN)
            frame = frame.dropna(axis=1,how='all')

            if frame.empty:
                continue

            # Convert first column to datetime
            frame.loc[:,frame.columns[0]] = pandas.to_datetime(frame[frame.columns[0]],errors='coerce')

            # Set first column as index
            frame.set_index(frame.columns[0],inplace=True)  # Set datetime column as index

            # Convert all values to numeric (coerce errors)
            frame = frame.apply(pandas.to_numeric,errors='coerce')

            # If printFlag is True, print the shape of the updated table
            if self.printFlag:
                print(f"Processed {key} frame's shape is {frame.shape}")

                if index == len(kwargs)-1:
                    print("\n\n")

            # Update dictionary
            tables[key] = frame

        # Return the updated tables, unpacked as separate arguments
        return tables

    def __call__(self,file_path:str,sheet_name:Union[str,int],*args):
        """Calls the extraction and processing functions to return cleaned tables.

        Parameters:        
        - file_path     : str, path to the Excel file.
        - sheet_name    : str, the name of the sheet to read from.

        - *args         : Optional row index intervals for manual extraction.

        Returns:
        - The extracted tables after cleaning.
        """
        # Step 1: Read the specified sheet from the Excel file into a DataFrame, with no header
        frame = pandas.read_excel(file_path,sheet_name=sheet_name,header=None)

        # Step 2: Call the 'extract' function to read and process the tables from the Excel sheet
        tables = self._extract(frame,*args)

        # Step 3: Call the 'process' function to clean up the tables (remove columns with NaN values)
        return self._process(**tables)

    @staticmethod
    def rename(tables,func=None):
        """
        Renames the columns of all DataFrames in the tables based on a given function.
        """

        func = ProductionTable.extract_digits if func is None else func

        for key,value in tables.items():
            tables[key] = value.rename(columns={col:func(col) for col in value.columns})

        return tables

    @staticmethod
    def compare(frame1:pandas.DataFrame,frame2:pandas.DataFrame,printFlag:bool=False):
        """
        Compare the columns of two dataframes and find differences (columns that are only in one dataframe).

        Parameters:
        - frame1: pandas DataFrame, the first dataframe to compare.
        - frame2: pandas DataFrame, the second dataframe to compare.

        Returns:
        - A tuple of two lists: columns only in frame1, and columns only in frame2.
        """

        # Get the column names of both dataframes as sets for comparison
        columns_frame1 = set(frame1.columns)
        columns_frame2 = set(frame2.columns)

        # Find the differences between the two sets of columns
        only_in_frame1 = columns_frame1-columns_frame2
        only_in_frame2 = columns_frame2-columns_frame1

        # Report the differences if requested
        if printFlag:
            if only_in_frame1:
                print("Columns only in the first frame:", only_in_frame1, end="\n\n")
            if only_in_frame2:
                print("Columns only in the second frame:", only_in_frame2, end="\n\n")

        # Return the differences as lists
        return list(only_in_frame1), list(only_in_frame2)