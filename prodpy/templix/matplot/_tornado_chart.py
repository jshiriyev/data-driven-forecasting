import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

color_dict = {"P10": "#00A86B", "P90": "#FF2800", }

p10_total = 6005405
p50_total = 5994083
p90_total = 5983336

p10_total_string = '6005 MTon'
p50_total_string = '5994 MTon'
p90_total_string = '5983 MTon'

xy_ticklabel_color ='#101628'

data = {
    "probabilities": ['P90','P10', 'P90','P10', 'P90','P10', 'P90','P10'],
    "activities" : ["Baza Hasilatı", "Baza Hasilatı", "Geoloji tədbirlər", "Geoloji tədbirlər", "Qazma+Yan lülə", "Qazma+Yan lülə","Texniki tədbirlər","Texniki tədbirlər"],
    "oil_amount" : [4.9,4.3,1.3,3.1,2.4,1.5,2.2,2.4]
}

df = pd.DataFrame(data)

sort_order_dict = {"Baza Hasilatı":4, "Geoloji tədbirlər":3, "Qazma+Yan lülə":2, "Texniki tədbirlər":1, 'P10':5, 'P90':6}

df = df.sort_values(by=['probabilities','activities',], key=lambda x: x.map(sort_order_dict))

#map the colors of a dict to a dataframe
df['color']= df.probabilities.map(color_dict)

probabilities = df.probabilities.unique()
oil_amounts = df.oil_amount
activities = df.activities.unique()
colors = df.color.unique()

fig, ax = plt.subplots(figsize=(10, 6))

direction = [1,-1]
for probability, d, color in zip(probabilities, direction, colors): 
    temp_df = df[df.probabilities == probability]
    ax.barh(temp_df.activities, temp_df.oil_amount*d, align='center', height = 0.6,facecolor=color,)

offset_labels = [0.1]*4 + [-0.1]*4

ccc = ['left','left','left','left','right','right','right','right']

for index,(bar, amount, off) in enumerate(zip(ax.patches, oil_amounts, offset_labels)):
    ax.text(
        bar.get_x() + bar.get_width() +off ,
        bar.get_height()/2 + bar.get_y(),
        amount,
        ha=ccc[index],va="center", color=xy_ticklabel_color,  size=11
          )

# Show sum on each stacked bar
for bar, activity in zip(ax.patches, activities):
    width = bar.get_width()
    label_y = bar.get_y() + bar.get_height() +0.1
    ax.text(0, label_y, s=f'{activity}', ha='center',size = 11, color = xy_ticklabel_color)

ax.text(0,3.,"5473 MTon", ha='center',va='center',size = 11,weight='bold',color='white')
ax.text(0,2.,"356 MTon", ha='center',va='center',size = 11,weight='bold',color='white')
ax.text(0,1.,"46 MTon", ha='center',va='center',size = 11,weight='bold',color='white')
ax.text(0,0.,"119 MTon", ha='center',va='center',size = 11,weight='bold',color='white')

ha = ["right", "left"]

xx = [5,-5]

index = 0
for bar,probability, ha in zip(ax.patches[3::4], probabilities, ha):
    ax.text(xx[index],bar.get_height()+bar.get_y()+1.,probability, size = 16, weight = "bold", ha= 'center')
    index += 1

ax.add_patch(plt.Arrow(0,4, 1, 0, width=0.2,color=color_dict['P10']))
ax.add_patch(plt.Arrow(0,4, -1, 0, width=0.2,color=color_dict['P90']))
ax.plot(0, 4.0001, 'o', markersize=6,color='white')

ax.text(xx[0],4.,p10_total_string, ha='center',size = 11)
ax.text(0,4.2,p50_total_string, ha='center',size = 11)
ax.text(xx[1],4.,p90_total_string, ha='center',size = 11)

ax.set_ylim((-1,5))
ax.set_yticks([])
ax.set_xticks([])
ax.set_xlim((-6,6))
# ax.set_axis_off()

##ax.set_xticks([-4000, -3000, -2000, -1000,0,1000,2000,3000,4000], ['', '', '', '','5996 kton','', '', '', ''])

plt.show()
