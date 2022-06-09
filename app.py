import streamlit as st
import pandas as pd

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
    return pd.read_excel('./fppe_data_combined.xlsx', header=[1,2,3], index_col=0)
df = load_combined_data()

methods = df.columns.get_level_values(0).drop_duplicates()
periods = df.columns.get_level_values(1).drop_duplicates()

s_states = st.multiselect('States', list(df.index.array), help='Select states')
s_methods = st.multiselect('Methods', list(methods.array), help='Select methods')
s_periods = st.multiselect('Period', list(periods.array), help='Select period')

if len(s_methods) and len(s_periods):
    ndf = df.loc[tuple(s_states), (tuple(s_methods), tuple(s_periods))]
    st.dataframe(ndf)