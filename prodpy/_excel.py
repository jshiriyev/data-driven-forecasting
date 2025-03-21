import pandas

def toexcel(filename,base,**kwargs):
	"""
    Calculate the difference between the last rows of multiple cases and a base DataFrame, 
    then export the results to an Excel file.

    Parameters:
    - filename (str): Name of the output Excel file (saved in the 'dropbox' directory).
    - base (pd.DataFrame): The reference DataFrame for comparison.
    - **kwargs: Additional DataFrames to compare against the base. The keys are used as column names.

    Output:
    - Saves an Excel file containing well names and oil gain (converted to tons).
    """

	sm3_to_ton = 0.862 # Conversion factor from sm3 to tons

	result_frames = []

	for key,case in kwargs.items():
		# Find common columns between base and case DataFrames
		common_columns = case.columns.intersection(base.columns)

		# Extract the last row (excluding first column) for comparison
        base_row = base.loc[:,common_columns].iloc[-1, 1:]
        case_row = case.loc[:,common_columns].iloc[-1, 1:]

        # Compute the difference and sort values in descending order
        difference = (case_row-base_row).sort_values(ascending=False)

        # Extract well labels and convert oil gain to tons
        cleaned_labels = difference.index.map(digits)

        oil_gain_in_ton = difference.values*sm3_to_ton

        # Store results in a DataFrame
        result_frames.append(pd.DataFrame({'Quyu Adı': cleaned_labels, key: oil_gain_in_ton}))

	# Merge all results side by side
    final_frame = pd.concat(result_frames, axis=1)

    # Save to Excel file
    output_path = f"dropbox/{filename}.xlsx"
    final_frame.to_excel(output_path,index=False)
    
    print(f"File saved: {output_path}")

