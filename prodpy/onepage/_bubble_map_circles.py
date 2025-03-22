import matplotlib.pyplot as plt

import numpy as np

import pandas as pd

from prodpy.pipeline import FrameUtils

utils = FrameUtils()

frame = pd.read_excel("Guneshli_main_1978_2022_1-MAY-2024 Chocke.xlsx")

frame = frame[frame["STANDARDOILFIELD"].isin(("Günəşli",))].reset_index(drop=True)

frame = frame[frame["HORIZON"].isin(("SP",))].reset_index(drop=True)

frame = frame[["MEASUREMENTDATE","WELLNAME","Gundelik_neft, t/gun","X-CM", "Y-CM"]]

DaysInMonth = utils(frame).days_in_month("MEASUREMENTDATE")

frame.loc[:,'Monthly Oil Production ton/month'] = frame['Gundelik_neft, t/gun']*DaysInMonth

frame = frame.groupby('WELLNAME').agg({
    'X-CM': 'first',
    'Y-CM': 'first',
    'Monthly Oil Production ton/month': 'sum'
}).reset_index()

frame.rename(columns={'Monthly Oil Production ton/month':'Cum. Production'},inplace=True)

frame = frame.sort_values("Cum. Production",ascending=False)

frame = frame.reset_index(drop=True)

map_x1 = 501_500
map_x2 = 510_500

map_y1 = 4_448_000
map_y2 = 4_456_000

map_deltax = map_x2-map_x1
map_deltay = map_y2-map_y1

img_deltax = 10_403
img_deltay =  8_753

image = plt.imread("s2_Gunashly_SP_surface_map.jpg")

plt.figure(figsize=(10.403,8.753))

plt.imshow(np.flipud(image),origin='lower')

well_x = frame["X-CM"]
well_y = frame["Y-CM"]

well_img_x = (well_x-map_x1)/map_deltax*img_deltax
well_img_y = (well_y-map_y1)/map_deltay*img_deltay

plt.scatter(well_img_x,well_img_y,s=frame["Cum. Production"]/5_000,c='red',alpha=0.2)

for index,row in frame.iterrows():
    plt.text(well_img_x[index],well_img_y[index],row["WELLNAME"][4:].lstrip('0'),ha='center',va='center', color='black',fontsize=6)

plt.axis('off')

plt.savefig('s2_well_distribution_bubble_map.png', dpi=300, format='png', bbox_inches='tight')

# plt.show()