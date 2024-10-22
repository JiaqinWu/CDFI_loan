import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
import altair as alt
from PIL import Image
import numpy as np
import os

# Load data
cdfi = pd.read_csv("CDFI_Cert_List_06-17-2024_Final.csv")
#number_cdfi = pd.read_csv("Total_CDFI_1004.csv")
table1 = pd.read_csv("Table1.csv")
table2 = pd.read_csv("Table2.csv")
table3 = pd.read_csv("Table3.csv")
attom = pd.read_csv("Table4.csv")
fips = pd.read_csv('FIPS_code_0917.csv')

# Streamlit application
def app():
    # Set wide layout and page title
    st.set_page_config(page_title='CDFI Research Coalition: Analysis of CDFI Lending in the Single-Family Mortgage Market', layout='wide')

    # Title section
    st.title('CDFI Research Coalition: Analysis of CDFI Lending in the Single-Family Mortgage Market')
    st.markdown("#### Analyzing CDFI participation in the Single-Family Mortgage Market from 2021-2024.")

    # Introduction section with accent color
    st.markdown("""
    ### 🏡 **Introduction**
    This dashboard uses loan data from **Attom** (May 15, 2021 – May 8, 2024) to analyze residential loans, with a focus on those approved by **Community Development Financial Institutions (CDFIs)**. We also incorporate the latest CDFI list from the [CDFI Fund website](https://www.cdfifund.gov/) as of **June 17, 2024**. Through this analysis, we explore:

    - When and where residential loans are being sought
    - Which CDFIs are most frequently approached
    - Loan amounts by CDFIs
    - Regional loan-seeking patterns
    """, unsafe_allow_html=True)

    # Create space and add research questions in a structured layout
    st.markdown("### 📊 **Data Sources**")
    st.markdown("""
    1. **Home Mortgage Disclosure Act (HMDA) for 2022 and 2023**
    2. **ATTOM Data Extract (proprietary extract based on public records such as property records)**
    3. **CDFI Fund**
    """)

    # Add horizontal space between sections
    st.markdown("---")

    # Display CDFI list with an expander for cleaner look
    with st.expander("### 📋 View Full CDFI List (as of June 17, 2024)"):
        st.dataframe(cdfi)

    # Display number of loans by CDFI with better structure and clarity
    st.markdown("### 💼 **CDFI Data Extracted from HMDA 2022-2023 (Depository and Loan Fund)**")
    table1[' Average Loan Size '] = table1[' Average Loan Size '].replace('[\$,]', '', regex=True).astype(float)
    table1[' Totals '] = table1[' Totals '].replace('[\$,]', '', regex=True).astype(float)
    st.dataframe(table1)

    # Display number of loans by CDFI with better structure and clarity
    st.markdown("### 💼 **CDFI Loan Fund Data Extracted from ATTOM 2022-2023 (Loan Fund Only)**")
    st.markdown("##### 2022 ATTOM reporting Total: $8,311,175,400.00")
    st.markdown("##### 2023 ATTOM reporting Total: $4,466,844,730.00")
    table2[' Average Loan Size (Perameters: $3MM-$70,000 '] = table2[' Average Loan Size (Perameters: $3MM-$70,000 '].replace('[\$,]', '', regex=True).astype(float)
    table2[' Total '] = table2[' Total '].replace('[\$,]', '', regex=True).astype(float)
    st.dataframe(table2)

    ## 3rd table
    st.markdown("### 💼 **CDFI Loan Fund Data Discrepancies Between HMDA and ATTOM Extracts 2022-2023**")
    table3[' HMDA: Average Loan Size (No Perameters) '] = table3[' HMDA: Average Loan Size (No Perameters) '].replace('[\$,]', '', regex=True).astype(float)
    table3[' ATTOM: Average Loan Size (Perameters: $3MM-$70,000) '] = table3[' ATTOM: Average Loan Size (Perameters: $3MM-$70,000) '].replace('[\$,]', '', regex=True).astype(float)
    table3[' HMDA: Total '] = table3[' HMDA: Total '].replace('[\$,]', '', regex=True).astype(float)
    table3[' ATTOM: Total '] = table3[' ATTOM: Total '].replace('[\$,]', '', regex=True).astype(float)

    st.dataframe(table3)

    ## 4th table
    st.markdown("### 💼 **CDFI Loan Fund Data Feed from Private sector Resources: Unbound Raw Data**")
    # Create a 2x2 layout
    col1, col2 = st.columns(2)

    # State Selection in the first column
    with col1:
        sorted_states = sorted(attom['From Tax SitusStateCode'].unique())
        sorted_states.insert(0, "All States")
        selected_state = st.selectbox('Select a state:', sorted_states)

    # CDFI Loan Fund Selection Box in the second column
    with col2:
        cdfi_funds = sorted(attom['Name of CDFI Loan Fund'].unique())
        selected_cdfi_fund = st.selectbox('Select a CDFI Loan Fund:', cdfi_funds)

    # Mortgage Amount Range Slider in the first column of the second row
    with col1:
        min_mortgage = int(attom['Mortgage1Amount'].min())
        max_mortgage = int(attom['Mortgage1Amount'].max())
        selected_mortgage_range = st.slider(
            'Select Mortgage Amount Range:',
            min_value=min_mortgage,
            max_value=max_mortgage,
            value=(min_mortgage, max_mortgage),
            key='m1'  # Default selection: full range
        )

    # Date Range Slider in the second column of the second row
    with col2:
        attom['Mortgage1RecordingDate'] = pd.to_datetime(attom['Mortgage1RecordingDate'])
        min_date = attom['Mortgage1RecordingDate'].min().date()
        max_date = attom['Mortgage1RecordingDate'].max().date()
        selected_date_range = st.slider(
            'Select Recording Date Range:',
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date)  # Default selection: full date range
        )

    # Filter data based on user selections
    filtered_data = attom[
        ((attom['From Tax SitusStateCode'] == selected_state)|(selected_state == "All States")) &
        (attom['Name of CDFI Loan Fund'] == selected_cdfi_fund) &
        (attom['Mortgage1Amount'] >= selected_mortgage_range[0]) &
        (attom['Mortgage1Amount'] <= selected_mortgage_range[1]) &
        (attom['Mortgage1RecordingDate'].dt.date >= selected_date_range[0]) &
        (attom['Mortgage1RecordingDate'].dt.date <= selected_date_range[1])
    ].sort_values(by='Mortgage1RecordingDate').reset_index(drop=True)

    # Display the filtered results
    st.markdown(f"##### {filtered_data.shape[0]} records are found.")
    st.dataframe(filtered_data)

    # Fifth graph
    # Processing FIPS data for geographic visualization
    attom['FIPS'] = attom['From Tax SitusStateCountyFIPS'].astype(str).str[:-3]
    fips['FIPS'] = fips['FIPS'].astype(str)

    # Merge with FIPS data
    df1 = pd.merge(attom, fips[['FIPS', 'State', 'State_abb', '2024_population']], on='FIPS', how='inner')
    df1['Mortgage1RecordingDate'] = pd.to_datetime(df1['Mortgage1RecordingDate'])

    # Six Plot
    st.markdown('### 🌍 Geographic Visualization of CDFI Loan Fund Single-Family Mortgage Lending Distributed Relative to State Population: New Mexico, Colorado, Florida and Georgia Have Strong Showings.')
    st.markdown('#### Source: CDFI Loan Fund Data Extracted from ATTOM 2022-2023')

    # Filter data based on user selections
    df_filtered1 = df1[
        (df1['Year'].isin([2022,2023]))
    ].sort_values(by='Mortgage1RecordingDate').reset_index(drop=True)

    # Geographic Visualization of Average Loan Amount by State
    geo_data1 = df_filtered1.groupby('State')['Mortgage1Amount'].sum().reset_index()
    geo_data1 = pd.merge(geo_data1, fips[['State', 'State_abb', '2024_population']], on='State', how='inner')
    geo_data1['amount_m'] = round(geo_data1['Mortgage1Amount']/geo_data1['2024_population'],2)
    geo_data1['State'] = geo_data1['State'].str.title()

    # Choropleth map of loan amounts by state
    fig2 = px.choropleth(
        geo_data1, 
        locations='State_abb',
        locationmode='USA-states',
        color='amount_m',
        color_continuous_scale=[
            [0, "green"],  # Lowest value
            [1, "orange"]  # Highest value
        ],
        scope="usa",
        labels={'amount_m': 'Lending Distributed Relative to State Population'},
        hover_data=['State', 'amount_m']
    )

    st.plotly_chart(fig2)


    # Date input for geographic visualization
    st.markdown('##### Customize your selection!')
    selected_date_range1 = st.slider(
            'Select Recording Date Range:',
            min_value=min_date,
            max_value=max_date,
            value=(min_date, max_date),
            key='m2'  # Default selection: full date range
        )
    
    # Filter data based on user selections
    df_filtered = df1[
        (df1['Mortgage1RecordingDate'].dt.date >= selected_date_range1[0]) &
        (df1['Mortgage1RecordingDate'].dt.date <= selected_date_range1[1])
    ].sort_values(by='Mortgage1RecordingDate').reset_index(drop=True)

    # Geographic Visualization of Average Loan Amount by State
    geo_data = df_filtered.groupby('State')['Mortgage1Amount'].sum().reset_index()
    geo_data = pd.merge(geo_data, fips[['State', 'State_abb', '2024_population']], on='State', how='inner')
    geo_data['amount_m'] = round(geo_data['Mortgage1Amount']/geo_data['2024_population'],2)
    geo_data['State'] = geo_data['State'].str.title()
    state_lists = geo_data.sort_values(by='amount_m',ascending=False)['State'].head(4).tolist()

    # Format the list into a readable string: "xx, xx, xx, and xx"
    if len(state_lists) == 4:
        formatted_states = f"{state_lists[0]}, {state_lists[1]}, {state_lists[2]}, and {state_lists[3]}"
    else:
        formatted_states = ", ".join(state_lists)

    # Use in the markdown output
    st.markdown(f"### 🌍 Geographic Visualization of CDFI Loan Fund Single-Family Mortgage Lending Distributed Relative to State Population: {formatted_states} Have Strong Showings.")
    st.markdown(f'#### Source: CDFI Loan Fund Data Extracted from ATTOM **{selected_date_range1[0]}** to **{selected_date_range1[1]}**')

    # Choropleth map of loan amounts by state
    fig1 = px.choropleth(
        geo_data, 
        locations='State_abb',
        locationmode='USA-states',
        color='amount_m',
        color_continuous_scale=[
            [0, "green"],  # Lowest value
            [1, "orange"]  # Highest value
        ],
        scope="usa",
        labels={'amount_m': 'Lending Distributed Relative to State Population'},
        hover_data=['State', 'amount_m']
    )

    st.plotly_chart(fig1)

    st.markdown("### 📖 OFN CDFI Research Coalition Presentation: October 21, 2024")
    
    # Folder where your slides are saved
    slide_folder = 'Slides'



    # Collect slide paths
    slides = sorted([os.path.join(slide_folder, f) for f in os.listdir(slide_folder) if f.endswith('.png')])

    # Initialize session state to track the current slide index
    if 'slide_index' not in st.session_state:
        st.session_state.slide_index = 0

    # Function to update the slide index
    def next_slide():
        if st.session_state.slide_index < len(slides) - 1:
            st.session_state.slide_index += 1

    def previous_slide():
        if st.session_state.slide_index > 0:
            st.session_state.slide_index -= 1

    # Add navigation buttons
    col1, col2, col3 = st.columns([1, 12, 1])
    with col1:
        if st.button("Previous"):
            previous_slide()

    with col2:
        st.markdown(f"<h3 style='text-align: center;'>Slide {st.session_state.slide_index + 1} of {len(slides)}</h3>", unsafe_allow_html=True)

    with col3:
        if st.button("Next"):
            next_slide()

    # Display the current slide
    slide = Image.open(slides[st.session_state.slide_index])
    st.image(slide, use_column_width=True)





if __name__ == "__main__":
    app()

