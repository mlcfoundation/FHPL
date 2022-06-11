from unicodedata import category
from pyrsistent import m
import streamlit as st
import pandas as pd
import os

# Data Options
DATA_OPTIONS = {
    'State-wise Combined': 'fppe_data_combined.xlsx',
    'State-wise Rural': 'fppe_data_rural.xlsx',
    'State-wise Urban': 'fppe_data_urban.xlsx',
    'District-wise Combined': 'fppe_data_districts.xlsx'
}

# Location of data files
DATA_ROOT = os.path.join('.', 'data')
DATA_STATES_COMBINED_WS = os.path.join(DATA_ROOT, DATA_OPTIONS['State-wise Combined'])
DATA_STATES_RURAL_WS = os.path.join(DATA_ROOT, DATA_OPTIONS['State-wise Rural'])
DATA_STATES_URBAN_WS = os.path.join(DATA_ROOT, DATA_OPTIONS['State-wise Urban'])
DATA_DISTRICTS_WS = os.path.join(DATA_ROOT, DATA_OPTIONS['District-wise Combined'])

# Map state code with state names
STATE_CODE_TO_STR = {
    'AN': 'Andaman & Nicobar',
    'AP': 'Andhra Pradesh',
    'AR': 'Arunachal Pradesh',
    'AS': 'Assam',
    'BI': 'Bihar',
    'CD': 'Chandigarh',
    'CH': 'Chhattisgarh',
    'DE': 'Delhi',
    'DN': 'Dadra & Nagar Haveli and Daman & Diu',
    'GO': 'Goa',
    'GU': 'Gujarat',
    'HA': 'Harayana',
    'HP': 'Himachal Pradesh',
    'JA': 'Jammu & Kashmir',
    'JH': 'Jharkhand',
    'KA': 'Karnataka',
    'KE': 'Kerala',
    'LA': 'Ladakh',
    'LK': 'Lakshadweep',
    'MA': 'Madhya Pradesh',
    'MH': 'Maharashtra',
    'MN': 'Manipur',
    'MY': 'Meghalaya',
    'MZ': 'Mizoram',
    'NG': 'Nagaland',
    'OD': 'Odissa',
    'PU': 'Punjab',
    'RA': 'Rajasthan',
    'SI': 'Sikkim',
    'TA': 'Tamil Nadu',
    'TE': 'Telangana',
    'TR': 'Tripura',
    'UP': 'Uttar Pradesh',
    'UT': 'Uttarakhand',
    'WB': 'West Bengal'
}

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
def load_data():
    df1 = pd.read_excel(DATA_STATES_COMBINED_WS, header=[0,1,2], index_col=0)
    df2 = pd.read_excel(DATA_STATES_RURAL_WS, header=[0,1,2], index_col=0)
    df3 = pd.read_excel(DATA_STATES_URBAN_WS, header=[0,1,2], index_col=0)
    df4 = pd.read_excel(DATA_DISTRICTS_WS, header=[0,1,2], index_col=[0,1])
    return (df1,df2,df3,df4)
swcd_df, swrd_df, swud_df, dwcd_df = load_data()

@st.cache
def build_dimensions(df):
    dim = {}

    # Bucketize
    for col in df.columns:
        if col[0] not in dim.keys():
            dim[col[0]] = [col[1]]
        else:
            dim[col[0]].append(col[1])

    # Deduplicate because of 3rd column in index
    for key in dim.keys():
        dim[key] = list(set(dim[key]))

    return dim
dim = build_dimensions(swcd_df)

# Update index names (Pandas doesn't allow naming index during creation of multi-index DFs)
swcd_df.index.rename('State', inplace=True)
swrd_df.index.rename('State', inplace=True)
swud_df.index.rename('State', inplace=True)
dwcd_df.index.rename(['State', 'District'], inplace=True)

states     = list(swcd_df.index.array)
categories = swcd_df.columns.get_level_values(0).drop_duplicates() 
methods    = swcd_df.columns.get_level_values(1).drop_duplicates()
periods    = swcd_df.columns.get_level_values(2).drop_duplicates()

#with st.expander('Indicators', expanded=True):
# Populate dimensions
s_dims = st.multiselect('Dimensions', dim.keys(), help='Select dimensions')

# Select indicators for selected dimensions
filetered_ind = dict(filter(lambda e: e[0] in s_dims, dim.items()))

# Combine all indicators
ind = []
for k in filetered_ind.keys():
    ind.extend(filetered_ind[k])

# Populate indicators
s_inds = st.multiselect('Methods', ind, help='Select methods')

#with st.expander('Particulars', expanded=True):
# Populates list of states from any state level DF (easier)
s_states = st.multiselect('States', states, help='Select states')

# Run a query on the district level DF to select only rows matching the selected states
d = dwcd_df.query('State == @s_states')

# Populate list of districts based on result of query above
s_districts = st.multiselect('Districts', list(d.index.get_level_values(1).array), help='Select districts')

# Periods are fixed so can be populated from any state/district level DF
s_periods = st.multiselect('Period', list(periods.array), help='Select period')

# Query DF
if len(s_states):
    if len(s_districts):
        res = dwcd_df.query("State == @s_states")
    else:
        res = swcd_df.query("State == @s_states")

    if len(s_districts):
        res = res.query('District == @s_districts')

    if len(s_dims) and len(s_inds) and len(s_periods):
        print(s_states, s_dims, s_inds, s_periods)
        res = res.loc[:,(s_dims, s_inds, s_periods)]
        st.dataframe(res)