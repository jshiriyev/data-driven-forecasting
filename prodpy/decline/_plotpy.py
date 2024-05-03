from matplotlib import pyplot

fig,(ax1,ax2,ax3,ax4,ax5,ax6) = plt.subplots(nrows=6)

fig.set_figheight(15)

ax1.scatter(wdf['Date'],orate,s=1)

ax1.set_ylabel('Oil Rate, MSTB/d')

ax2.scatter(wdf['Date'],lrate,s=1)

ax2.set_ylabel('Liquid Rate, MSTB/d')

ax3.scatter(wdf['Date'],gor,s=1)

ax3.set_ylabel('GOR, SCF/STB')

ax4.scatter(wdf['Date'],wcut,s=1)

ax4.set_ylabel('Water Cut, %')

ax5.scatter(wdf['Date'],grate,s=1)

ax5.set_ylabel('Gas Rate, MMSCF/d')

ax6.scatter(wdf['Date'],wrate,s=1)

ax6.set_ylabel('Water Rate, MSTB/d')