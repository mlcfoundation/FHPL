import streamlit as st
import pandas as pd
import os

st.set_page_config(
     page_title="Family Planning Performance Explorer",
     layout="wide",
     initial_sidebar_state="expanded",
     menu_items={
         'Get Help': 'https://github.com/mlcfoundation/NFHS/issues',
         'Report a bug': "https://github.com/mlcfoundation/NFHS/issues",
         'About': "# NFHS-5 District Indicators Comparison App"
     }
 )

# Location of data files
DATA_ROOT = os.path.join('.', 'data')
DATA_STATES_COMBINED_WS = os.path.join(DATA_ROOT, 'fppe_data_combined.xslx')
DATA_STATES_RURAL_WS = os.path.join(DATA_ROOT, 'fppe_data_rural.xslx')
DATA_STATES_URBAN_WS = os.path.join.(DATA_ROOT, 'fppe_data_urban.xslx')
DATA_DISTRICTS_WS = os.path.join(DATA_ROOT, 'fppe_data_districts.xslx')

st.sidebar.write("## Family Planning Performance Explorer")
st.sidebar.write("***")
st.sidebar.write('## District & State Comparison')
#st.sidebar.write(TEXT1)
#st.sidebar.write(TEXT2)
#st.sidebar.write(TEXT3)
st.sidebar.write("***")
st.sidebar.write('Copyright (C) **MLC Foundation**. *All rights reserved.*')

@st.cache
def load_combined_data():
    return pd.read_excel(DATA_STATES_COMBINED_WS, header=[1,2,3], index_col=0)
df = load_combined_data()

methods = df.columns.get_level_values(0).drop_duplicates()
periods = df.columns.get_level_values(1).drop_duplicates()

s_states = st.multiselect('States', list(df.index.array), help='Select states')
s_methods = st.multiselect('Methods', list(methods.array), help='Select methods')
s_periods = st.multiselect('Period', list(periods.array), help='Select period')

if len(s_methods) and len(s_periods):
    ndf = df.loc[tuple(s_states), (tuple(s_methods), tuple(s_periods))]
    st.dataframe(ndf)