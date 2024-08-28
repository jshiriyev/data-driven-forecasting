import pandas as pd

import matplotlib.pyplot as plt
import seaborn as sns

df = pd.read_excel("Guneshli_main_1978_2022_1-MAY-2024 Chocke.xlsx")

gunashly = df[df["STANDARDOILFIELD"].isin(("Günəşli",))].reset_index(drop=True); gunashly.shape

def get_days_in_month(frame,datehead):
    # Convert the input date string to a datetime object
    date = frame[datehead]
    
    # Calculate the start of the next month
    next_month = (date + pd.offsets.MonthBegin(1))

    next_month = pd.to_datetime(next_month).dt.to_period('M').dt.to_timestamp()
    
    # Calculate the start of the given month
    start_of_month = pd.to_datetime(date).dt.to_period('M').dt.to_timestamp()
    
    # Calculate the number of days in the month
    days_in_month = (next_month - start_of_month).dt.days

    frame["days_in_month"] = days_in_month
    
    return frame

group = gunashly[["MEASUREMENTDATE","HORIZON","Gundelik_neft, t/gun"]].groupby(["MEASUREMENTDATE","HORIZON"])

GUN = group.sum('Gundelik_neft, t/gun').reset_index()

GUN = get_days_in_month(GUN,"MEASUREMENTDATE")

GUN['Monthly Oil Production ton/month'] = GUN['Gundelik_neft, t/gun']*GUN['days_in_month']

replacement_dict = {
    'III': 'Others',
    'IV': 'Others',
    'QA': 'Others',
    'QÜG': 'Others',
    'V': 'Others',
    'VI': 'Others',
    'VII': 'Others',
    'VIII': 'Others',
}

GUN['HORIZON'] = GUN['HORIZON'].replace(replacement_dict)

GUN['Year'] = GUN['MEASUREMENTDATE'].dt.year

annual_horizon_production = GUN.groupby(['Year', 'HORIZON'])['Monthly Oil Production ton/month'].sum().unstack().fillna(0)

annual = annual_horizon_production[["SP","X","IX","QÜQ","Others"]]

annual["SP"] = annual["SP"]/1_000_000
annual["X"] = annual["X"]/1_000_000
annual["IX"] = annual["IX"]/1_000_000
annual["QÜQ"] = annual["QÜQ"]/1_000_000
annual["Others"] = annual["Others"]/1_000_000


plt.figure(figsize=(14, 8))

sns.set(style="dark")

sns.set_context("poster", font_scale = 1, rc={"grid.linewidth": 5})

# Create stacked bar plot
annual.plot(kind='bar', stacked=True, width = 1., colormap='Paired', edgecolor='black', linewidth=1)

plt.gcf().set_size_inches(14, 6)

# Add title and labels with increased font size for better readability
# plt.title('Annual Production with Horizon Contribution', fontsize=14)
plt.xlabel('', fontsize=14)

plt.ylabel('Annual Oil Production, MMTon', fontsize=12)

# Customize legend
plt.legend(title='Horizon', title_fontsize='12', fontsize='12')

# Rotate x-axis labels for better readability
plt.xticks(rotation=90, fontsize=12)
plt.yticks(fontsize=12)

# Add grid lines for better readability
plt.grid(True, which='both', linestyle='--', linewidth=0.5)

# Adjust layout to prevent clipping of ylabel
plt.tight_layout()

# Show the plot
plt.show()