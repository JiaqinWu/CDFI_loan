import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import datetime

# Load the datasets
df = pd.read_csv('Residential_records_CDFI_1004.csv')
fips = pd.read_csv('FIPS_code_0917.csv')

# Streamlit application
def app():
    # Set wide layout and page title
    st.set_page_config(page_title='CDFI Research Coalition: Analysis of CDFI Lending in the Single-Family Mortgage Market', layout='wide')

    # Title and Introduction Section
    st.title('CDFI Residential Loan Dashboard')
    st.markdown("""
    ### Overview
    This tab provides insights into the **number of residential loan**s approved by Community Development Financial Institutions (CDFIs) from **May 2021 to May 2024**. You can explore the loan trends over time and across states.
    """)

    # Processing data for time-series visualization
    df['Mortgage1RecordingMonth'] = [i[:-2] + '01' for i in df['Mortgage1RecordingDate']]
    df['Mortgage1RecordingMonth'] = pd.to_datetime(df['Mortgage1RecordingMonth'])
    df_count = df.groupby('Mortgage1RecordingMonth')['match_CDFI_final'].count().reset_index().rename(columns={
        'Mortgage1RecordingMonth': 'Time',
        'match_CDFI_final': 'Number of Loans'
    })

    # Time-series chart for all states
    st.markdown("#### Time-series of Residential Loans (May 2021 - May 2024)")
    line_chart = alt.Chart(df_count).mark_line(point=True).encode(
        x=alt.X('Time:T', title='Time', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Number of Loans:Q', title='Number of Loans'),
        tooltip=[alt.Tooltip('yearmonth(Time):T', title='Month'), 
                 alt.Tooltip('Number of Loans:Q', title='Number of Loans')]
    ).properties(
        width=1000,
        height=400
    ).interactive()

    st.altair_chart(line_chart)

    # State-based filtering
    st.markdown("#### Time-series of Residential Loans by State")
    sorted_states = sorted(df['From Tax SitusStateCode'].unique())
    selected_state = st.selectbox('Select a state:', sorted_states)

    df_state = df[df['From Tax SitusStateCode'] == selected_state]
    df_state_count = df_state.groupby('Mortgage1RecordingMonth')['match_CDFI_final'].count().reset_index().rename(columns={
        'Mortgage1RecordingMonth': 'Time',
        'match_CDFI_final': 'Number of Loans'
    })

    # State-level time-series chart
    st.markdown(f"Number of Loans in {selected_state} (May 2021 - May 2024)")
    line_chart_state = alt.Chart(df_state_count).mark_line(point=True).encode(
        x=alt.X('Time:T', title='Time', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Number of Loans:Q', title='Number of Loans'),
        tooltip=[alt.Tooltip('yearmonth(Time):T', title='Month'), 
                 alt.Tooltip('Number of Loans:Q', title='Number of Loans')]
    ).properties(
        width=1000,
        height=400
    ).interactive()

    st.altair_chart(line_chart_state)

    # Processing FIPS data for geographic visualization
    df['FIPS'] = df['From Tax SitusStateCountyFIPS'].astype(str).str[:-3]  # Correct FIPS handling
    fips['FIPS'] = fips['FIPS'].astype(str)

    # Merging the data with population data
    df1 = pd.merge(df, fips[['FIPS', 'State', 'State_abb', '2024_population']], on='FIPS', how='inner')
    df1['Mortgage1RecordingDate'] = pd.to_datetime(df1['Mortgage1RecordingDate'])

    # Date input for time selection
    low_date = df1['Mortgage1RecordingDate'].min()
    high_date = df1['Mortgage1RecordingDate'].max()

    date_range = st.date_input(
        "Select the time period for geographic visualization",
        (low_date, high_date),
        min_value=low_date,
        max_value=high_date,
        format="MM.DD.YYYY"
    )

    # Check for valid date range selection
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df1[(df1['Mortgage1RecordingDate'] >= pd.to_datetime(start_date)) & (df1['Mortgage1RecordingDate'] <= pd.to_datetime(end_date))]
    else:
        st.error("Please select a valid date range.")
        return

    # Prepare data for geographic visualization
    geo_data = df_filtered.groupby('State').Mortgage1RecordingDate.count().reset_index().rename(columns={'Mortgage1RecordingDate': 'Value'})
    geo_data = pd.merge(geo_data, fips[['State', 'State_abb', '2024_population']], on='State', how='inner')
    geo_data['Value_M'] = geo_data['Value'] / geo_data['2024_population'] * 1000000  # Normalize by population

    # Update title based on date range
    if start_date == end_date:
        st.markdown(f"### Geographic Visualization of Residential Loans on **{start_date.strftime('%B %d, %Y')}**")
    else:
        st.markdown(f"### Geographic Visualization of Residential Loans from **{start_date.strftime('%B %d, %Y')}** to **{end_date.strftime('%B %d, %Y')}**")

    # Choropleth map for number of loans
    st.markdown("""
    ##### Geographic Visualization of the Number of Residential Loans
    """)
    fig1 = px.choropleth(
        geo_data,
        locations='State_abb',
        locationmode='USA-states',
        color='Value',
        color_continuous_scale='Blues',
        scope="usa",
        labels={'Value': 'Loans'},
        hover_data=['State', 'Value']
    )

    st.plotly_chart(fig1)

    # Choropleth map for number of loans
    st.markdown("""
    ##### Geographic Visualization of the Number of Residential Loans Per Million People 
    """)
    fig = px.choropleth(
        geo_data,
        locations='State_abb',
        locationmode='USA-states',
        color='Value_M',
        color_continuous_scale='Blues',
        scope="usa",
        labels={'Value_M': 'Loans per Million People'},
        hover_data=['State', 'Value_M']
    )

    st.plotly_chart(fig)

    # Population data source
    st.markdown("""
    ##### *Population data sourced from [World Population Review](https://worldpopulationreview.com/states).*
    """)

if __name__ == "__main__":
    app()
