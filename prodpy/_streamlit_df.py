import pandas as pd

df = pd.read_excel(r"C:\Users\3876yl\OneDrive - BP\Documents\ACG_decline_curve_analysis.xlsx")

# print(df.columns)

# print(df['Well'].unique())

# print(df[df['Well']=='D32'])

print((df['Date']-df['Date'][0])*5)

# print(df.head)

# print(dir(df))