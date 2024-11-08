import matplotlib.pyplot as plt

import numpy

import pandas as pd

color = {"P10": "#00A86B", "P90": "#FF2800", }

data = {
    "activities" : [
        "Baza Hasilatı",
        "Geoloji tədbirlər",
        "Qazma+Yan lülə",
        "Texniki tədbirlər"
        ],
    "P90" : [   3.7 ,   0.6, 1.5,  1.6],
    "P50" : [3256.  , 194. , 8. , 30. ],
    "P10" : [   3.8 ,   2.7, 1.0,  2.1],
    "P50s": [
        "3256 MTon",
        " 194 MTon",
        "   8 MTon",
        "  30 MTon",
        ]
}

p10_total_string = '3497 MTon'
p50_total_string = '3487 MTon'
p90_total_string = '3480 MTon'

xy_ticklabel_color ='#101628'

df = pd.DataFrame(data)

df.sort_values(by='P50',ascending=True,inplace=True)
df.reset_index(inplace=True,drop=True)

max_wing_value = df[['P90','P10']].max().max()
max_wing_power = (-int(numpy.floor(numpy.log10(abs(max_wing_value)))))
max_wing_value = (numpy.ceil(max_wing_value*10**max_wing_power)/10**max_wing_power).tolist()

fig, ax = plt.subplots(figsize=(10,6))

for index,row in df.iterrows():

    ax.barh(row["activities"],-row['P90'],align='center',height=0.5,facecolor=color['P90'])
    ax.barh(row["activities"], row['P10'],align='center',height=0.5,facecolor=color['P10'])

    ax.text(-row['P90']-0.4,index,row['P90'],ha='left' ,va="center",color=xy_ticklabel_color,size=11)
    ax.text( row['P10']+0.4,index,row['P10'],ha='right',va="center",color=xy_ticklabel_color,size=11)

    ax.text(0.,index+0.35,s=row['activities'],ha='center',size=11,color=xy_ticklabel_color)

    ax.text(0.2,index,row["P50s"],ha='center',va='center',size=11,weight='bold',color='white')

N = len(df)

ax.text( max_wing_value,N,"P10",size=16,weight="bold",ha='center')
ax.text(-max_wing_value,N,"P90",size=16,weight="bold",ha='center')

ax.add_patch(plt.Arrow(0,N,-1,0,width=0.2,color=color['P90']))
ax.plot(0,N+0.0001,'o',markersize=6,color='white')
ax.add_patch(plt.Arrow(0,N, 1,0,width=0.2,color=color['P10']))

ax.text( max_wing_value,N-0.3,p10_total_string,ha='center',size=11)
ax.text(              0,N+0.2,p50_total_string,ha='center',size=11)
ax.text(-max_wing_value,N-0.3,p90_total_string,ha='center',size=11)

ax.set_ylim((-1,N+1))
ax.set_yticks([])
ax.set_xticks([])
ax.set_xlim((-max_wing_value-1,max_wing_value+1))
# # ax.set_axis_off()

plt.show()
