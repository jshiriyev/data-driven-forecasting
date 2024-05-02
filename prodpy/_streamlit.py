import os

import matplotlib.pyplot as plt

import pandas as pd

import streamlit as st

st.set_page_config(layout='wide',page_title='Decline Curve Analysis')

def file_selector(folder_path='.'):

    filenames = os.listdir(folder_path)

    selected_filename = st.selectbox('Select a file', filenames)

    return os.path.join(folder_path, selected_filename)

def get_welldata(well_name):

	return df[df['Well']==well_name]

with st.sidebar:

	filepath = file_selector(r'C:\Users\3876yl\OneDrive - BP\Documents')

	df = pd.read_excel(filepath)

	# st.write('You selected:')

	st.text_input('You selected:', value=f"{os.path.basename(filepath)}",disabled=True)

	# st.write(f"{os.path.basename(filepath)}")

	well_list = df['Well'].unique()

	# st.write('Active well stock:')

	well = st.selectbox("Active well stock:",well_list)

	wdf = get_welldata(well)

# st.header('Oil Rate')
# st.header('Liquid Rate')
# st.header('Gas Oil Ratio')
# st.header('Water Cut')
# st.header('Gas Rate')
# st.header('Water Rate')

orate = wdf['Actual Oil, Mstb/d']
grate = wdf['Actual Gas, MMscf/d']
wrate = wdf['Actual Water, Mstb/d']
lrate = orate+wrate
wcut  = wrate/(wrate+orate)*100
gor   = grate*1000/orate


fig, (ax1,ax2,ax3,ax4,ax5,ax6) = plt.subplots(nrows=6)

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

st.pyplot(fig)