import plotly.express as pex
import streamlit as st
import pandas as pd
import os
import json

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

st.set_page_config(
    page_title="Family Planning Performance Explorer",
    layout="wide",
    initial_sidebar_state="expanded",
    menu_items={
        'Get Help': 'https://github.com/mlcfoundation/FPPE/issues',
        'Report a bug': "https://github.com/mlcfoundation/FPPE/issues",
        'About': "# Family Planning Performance Exporer App"
    }
 )

#with open( "style.css" ) as css:
#    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)

TEXT1 = "This app is developed by *[MLC Foundation](https://www.mlcfoundation.org.in/)*"
TEXT2 = "Please contact Aalok Ranjan *<aalok@mlcfoundation.org.in>* or "\
        "Akshay Ranjan *<akshay@mlcfoundation.org.in>* for any help, "\
        "suggestions, questions, etc."
TEXT3 = "This is an open source application and code can be found at "\
        "*[github.com](https://github.com/mlcfoundation/FPPE)*. Report bugs "\
        "*[here](https://github.com/mlcfoundation/FPPE/issues)*."

st.sidebar.write("## Family Planning Performance Explorer")
st.sidebar.write("***")
st.sidebar.write(TEXT1)
st.sidebar.write(TEXT2)
st.sidebar.write(TEXT3)
st.sidebar.write("***")
st.sidebar.write('Copyright (C) **MLC Foundation**. *All rights reserved.*')

@st.experimental_singleton
def load_data():
    df1 = pd.read_excel(DATA_STATES_COMBINED_WS, header=[1,2,3], index_col=0)
    df2 = pd.read_excel(DATA_STATES_RURAL_WS, header=[1,2,3], index_col=0)
    df3 = pd.read_excel(DATA_STATES_URBAN_WS, header=[1,2,3], index_col=0)
    df4 = pd.read_excel(DATA_DISTRICTS_WS, header=[1,2,3], index_col=[0,1])
    return (df1,df2,df3,df4)
swcd_df, swrd_df, swud_df, dwcd_df = load_data()

@st.experimental_singleton
# Open states geo
def load_states_geo():
    f_states = open(os.path.join(DATA_ROOT, 'STATE_BOUNDARY.json'))
    return json.load(f_states)
states_geo = load_states_geo()

@st.experimental_singleton
# Open districts geo
def load_districts_geo():
    f_districts = open(os.path.join(DATA_ROOT, 'DISTRICT_BOUNDARY.json'))
    geo = json.load(f_districts)
    features = geo['features']
    fda = {}
    fsa = {}

    for feature in features:
        d_name = feature['properties']['District']
        d_id = feature['properties']['DISTRICT_L']
        s_name = feature["properties"]['STATE']
        s_id = feature['properties']['State_LGD']

        if not d_name.startswith('DISPUTED'):
            # fda[d_name.replace('>','A').replace('|', 'I').replace('@','U')] = {
            #    "id": d_id,
            #    "state": s_name.replace('>','A').replace('|', 'I').replace('@','U'),
            #    "state_id": s_id
            # }
            fda[d_name] = {
                "id": d_id,
                "state": s_name,
                'state_id': s_id
            }
        if not s_name.startswith('DISPUTED'):
            #if s_name.replace('>','A').replace('|', 'I').replace('@','U') not in fsa.keys():
            #    fsa[s_name.replace('>','A').replace('|', 'I').replace('@','U')] = s_id
            if s_name not in fsa.keys():
                fsa[s_name] = s_id
    
    return geo, { 'States': fsa, 'Districts': fda }
districts_geo, names = load_districts_geo()
#print(names)

def download_as_csv(df):
    return df.to_csv().encode('utf-8')

@st.experimental_singleton
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

# Options
#opt_table = True
#opt_chart = False
#opt_map = False
with st.expander('Options', expanded=False):
    c1,c2,c3 = st.columns(3)
    with c1:
        opt_table = st.checkbox('Table', value=True, help='Show data in a table')
    with c2:
        opt_chart = st.checkbox('Chart', value=False, help='Show data in a bar chart')
    with c3:
        opt_map = st.checkbox('Map', value=False, help='Show data on a map')

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

# All states?
if st.checkbox('All states'):
    # All states are selected
    s_states = list(dwcd_df.index.get_level_values(0).array)
else:
    # Populates list of states from any state level DF (easier)
    s_states = st.multiselect('States', states, help='Select states')

# Run a query on the district level DF to select only rows matching the selected states
d = dwcd_df.query('State == @s_states')

# All districts?
if st.checkbox('All districts'):
    # All districts of selected states
    s_districts = list(d.index.get_level_values(1).array)
else:
    # Populate list of districts based on result of query above
    s_districts = st.multiselect('Districts', list(d.index.get_level_values(1).array), help='Select districts')

# Periods are fixed so can be populated from any state/district level DF
s_periods = st.multiselect('Period', list(periods.array), help='Select period')

# Query DF (we need state to be selected)
if len(s_states):
    if len(s_districts):
        res = dwcd_df.query("State == @s_states")
    else:
        res = swcd_df.query("State == @s_states")

    # Filter districts (if selected)
    if len(s_districts):
        res = res.query('District == @s_districts')

    # Make sure we have all the parameters
    if len(s_dims) and len(s_inds) and len(s_periods):
        res = res.loc[:,(s_dims, s_inds, s_periods)]

        # Flatten columns
        res.columns = [ ', '.join(c).rstrip('_') for c in res.columns.values ]

        with st.expander(label='Table', expanded=True):
            if opt_table:
                # Deep copy DF if map is also enabled
                tres = res.copy(deep=True) if opt_map else res
                
                # Check if districts are selected
                if len(s_districts):
                    # Flatten index
                    tres.index = [ ', '.join(i).rstrip('_') for i in tres.index.values ]

                st.table(tres)
                st.download_button('Download as CSV', download_as_csv(tres), 'FPPE.csv', 'text/csv', key='download-csv')

        with st.expander(label='Chart', expanded=True):
            if opt_chart:
                # Deep copy DF if map is also enabled
                cres = res.copy(deep=True) if opt_map else res
                
                # Check if districts are selected
                if len(s_districts):
                    # Flatten index
                    cres.index = [ ', '.join(i).rstrip('_') for i in cres.index.values ]

                chart = pex.bar(cres, text_auto=True, orientation='v', barmode='group')
                chart.update_layout(font_family='helvetica')
                st.plotly_chart(chart, use_container_width=True)

        with st.expander(label='Map', expanded=True):
            if opt_map:
                if len(s_districts):
                    if len(res.columns) == 1:
                        nres = res.reset_index()

                        data_color = nres[nres.columns[2]]
                        r_max = nres[nres.columns[2]].max()
                        r_min = nres[nres.columns[2]].min()

                        # Add district indice
                        nres['District_ID'] = nres.apply(lambda row: names['Districts'][row.District.upper()]['id'], axis=1)

                        print(nres)

                        # Use mapbox
                        pex.set_mapbox_access_token(st.secrets['mapbox']['key'])
                        chart = pex.choropleth_mapbox(nres, 
                                                      geojson=districts_geo,
                                                      locations='District_ID',
                                                      color=data_color,
                                                      range_color=(r_max, r_min),
                                                      color_continuous_scale='spectral_r',
                                                      featureidkey='properties.DISTRICT_L',
                                                      mapbox_style='light',
                                                      center={"lat": 22, "lon": 82},
                                                      zoom=3.85,
                                                      width=900,
                                                      height=950)
                        st.plotly_chart(chart, use_container_width=True)
                else:
                    if len(res.columns) == 1:
                        nres = res.reset_index()

                        data_color = nres[nres.columns[1]]
                        r_max = nres[nres.columns[1]].max()
                        r_min = nres[nres.columns[1]].min()

                        # Add state indice
                        nres['State_ID'] = nres.apply(lambda row: names['States'][row.State.upper()], axis=1)

                        # Dump DF
                        # print(nres)

                        # Use mapbox
                        pex.set_mapbox_access_token(st.secrets['mapbox']['key'])
                        chart = pex.choropleth_mapbox(nres, 
                                                      geojson=states_geo,
                                                      locations='State_ID',
                                                      color=data_color,
                                                      range_color=(r_max, r_min),
                                                      color_continuous_scale='spectral_r',
                                                      featureidkey='properties.STATE',
                                                      mapbox_style='light',
                                                      center={"lat": 22, "lon": 82},
                                                      zoom=3.85,
                                                      width=900,
                                                      height=950)
                        st.plotly_chart(chart, use_container_width=True)
                





