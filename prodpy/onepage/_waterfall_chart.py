import matplotlib.pyplot as plt

import numpy as np

import pandas as pd

# Sample DataFrame
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

# Calculate the cumulative values to determine where each bar should start
df['cumulative'] = df['value'].cumsum()

df['shifted'] = df['cumulative'].shift(fill_value=0)

# Define colors for positive and negative bars
colors = ['#4CAF50' if x >= 0 else '#FF5733' for x in df['value']]

colors[ 0] = "#808080"
colors[-1] = "#808080"

df['colors'] = colors

print(df)

# Plotting the waterfall chart
fig, ax = plt.subplots(figsize=(10, 6))

# Add labels for each bar
for index,row in df.iloc[:-1].iterrows():
	ax.bar(row['category'],row['value'],bottom=row['shifted'],color=row['colors'],edgecolor='black')
	yy = row['cumulative']+1 if row['value'] >= 0 else row['cumulative']-2
	va = 'bottom' if row['value'] >= 0 else 'top'
	ax.text(index, yy, row['value'],ha='center',va=va)
else:
	index,row = index+1,df.iloc[-1]
	ax.bar(row['category'],row['shifted'],bottom=0,color=row['colors'],edgecolor='black')
	ax.text(index,row['shifted']+1,row['shifted'],ha='center',va='bottom')

ax.set_ylabel("value")

ax.set_ylim((0,df['shifted'].max()+10))

plt.xticks(rotation=45,ha='right')

plt.tight_layout()

plt.show()
