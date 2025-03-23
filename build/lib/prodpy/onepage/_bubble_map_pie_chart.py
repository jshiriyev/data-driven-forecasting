import matplotlib.pyplot as plt

from matplotlib.patches import Wedge

import numpy as np

import pandas as pd

data = {
 "wellname": ["NFD_1795", "NFD_2118","NFD_2226_S1", "NFD_2271", "NFD_2680", "NFD_1661"],
        "X": [ 494071.76,  493891.73,  494148.5621,  493431.01,  494558.86,  494093.34],
        "Y": [4453174.78, 4453090.25, 4453086.194 , 4453237.29, 4453124.6 , 4453097.31],
      "oil": [15811, 33903, 19752,  2496, 1650, 73228],
    "water": [    0,     0,     0, 18211,    0,  1922],
}

frame = pd.DataFrame(data)

frame['total'] = frame['oil'] + frame['water']

frame['oil_ratio'] = frame['oil']/frame['total']
frame['water_ratio'] = frame['water']/frame['total']

print(frame)

map_x1 = 493_000
map_x2 = 494_800

map_y1 = 4_451_700
map_y2 = 4_454_100

map_deltax = map_x2-map_x1
map_deltay = map_y2-map_y1

img_deltax = 2374
img_deltay = 1172

image = plt.imread("jeyhun.png")

scale_factor = 50_0000

fig,ax = plt.subplots(figsize=(15,5))

plt.imshow(np.flipud(image),origin='lower')

alpha = 0.7

for index,row in frame.iterrows():

    fractions = [row['oil'] / row['total'], row['water'] / row['total']]

    size = scale_factor * np.sqrt(row['total'])

    colors = [(144/255, 238/255, 144/255, alpha),
              (  0/255, 105/255, 148/255, alpha),]

    well_img_x = (row["X"]-map_x1)/map_deltax*img_deltax
    well_img_y = (row["Y"]-map_y1)/map_deltay*img_deltay

    # print((well_img_x,well_img_y))

    plt.pie(fractions,radius=np.sqrt(size)/100,colors=colors,startangle=90,center=(well_img_x,well_img_y))

    ax.text(well_img_x,well_img_y,row["wellname"],ha='center',va='center', color='black',fontsize=6)

    circle = plt.Circle((well_img_x,well_img_y), np.sqrt(size) / 100, edgecolor='black', fill=False, alpha = 0.3, linewidth=0.5)
    
    ax.add_artist(circle)

# plt.axis('off')

# plt.savefig('s2_well_distribution_bubble_map.png', dpi=300, format='png', bbox_inches='tight')

# ax.set_xlim([ 493000, 495000])
# ax.set_ylim([4453000,4453300])

ax.set_xlim([0, img_deltax])
ax.set_ylim([0, img_deltay])

# plt.tight_layout()

plt.show()