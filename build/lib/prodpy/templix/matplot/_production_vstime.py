import datetime

import pandas

import matplotlib.pyplot as plt

def matplot_template(frame:pandas.DataFrame,fit:pandas.DataFrame=None,forecast:pandas.DataFrame=None):

	today = datetime.date.today()

	fig, axes = plt.subplots(nrows=4,figsize=(10,16))

	data, = axes[0].plot(frame[datehead],frame[oprohead],
		color="#6B5B95",lw=1,linestyle='',marker='o',markersize=1)

	if fit is not None:
		line1, = axes[0].plot(fit['x'],fit['y'],color='red',linewidth=1)

	if forecast is not None:
		line2, = axes[0].plot(forecast['x'],forecast['y'],color='blue',linewidth=1)

	axes[1].plot(frame[datehead],frame[wprohead],linestyle='',marker='o',markersize=1)
	axes[1].set_ylabel('Gundelik_su, m3/gun',color='blue')

	axis_12 = axes[1].twinx()
	axis_12.plot(frame[datehead],frame[gprohead],linestyle='',marker='o',markersize=3,color='red')
	axis_12.set_ylabel('Gundelik_qaz, Km3/gun',color='red')

	axes[2].plot(frame[datehead],frame[chckhead],linestyle='',marker='o',markersize=1)
	axes[2].set_ylabel('Chocke2',color='blue')

	axis_22 = axes[2].twinx()
	axis_22.plot(frame[datehead],frame[pdayhead],linestyle='',marker='o',markersize=3,color='red')
	axis_22.set_ylabel('Production_Days',color='red')

	axes[3].plot(frame[datehead],frame[liftname])
	axes[3].set_ylabel('Hasilat_usulu')

	for axis in axes:

	    axis.set_xlim(xmax=datetime.date(today.year+1,1,1))

	    axis.axvline(x=today,color='k',linestyle='--',linewidth=0.5)

	line.set_path_effects([patheffects.withStroke(linewidth=3, foreground='black')])

	axes[0].set_facecolor("#f4f4f4")
	axes[0].spines['left'].set_color('#6B5B95')
	axes[0].spines['bottom'].set_color('#6B5B95')
	axes[0].grid(True, linestyle='--',color='gray',alpha=0.5)
	axes[0].tick_params(colors='#6B5B95')
	axes[0].set_ylabel("Gündəlik Neft, ton/gün", fontsize=12, color="#88B04B", weight='bold')