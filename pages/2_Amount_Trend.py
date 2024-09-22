import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px
import datetime

# Load the datasets
df = pd.read_csv('Residential_records_CDFI_0916.csv')
fips = pd.read_csv('FIPS_code_0917.csv')

# Streamlit application
def app():
    # Set wide layout and page title
    st.set_page_config(page_title='CDFI Residential Loan Dashboard', layout='wide')

    # Title and Introduction Section
    st.title('CDFI Residential Loan Dashboard')
    st.markdown("""
    ### Overview
    This tab provides insights into the **amount of residential loans** approved by Community Development Financial Institutions (CDFIs) from **May 2021 to May 2024**. You can explore the trends over time and across states, and dive deeper into specific states and loan amounts.
    """)

    # Time-Series Visualization of Loan Amounts
    st.markdown("#### Time-series of Average Residential Loan Amounts (May 2021 - May 2024)")
    df['Mortgage1RecordingMonth'] = pd.to_datetime(df['Mortgage1RecordingDate'].str[:7] + '-01')
    df_avg_amount = df.groupby('Mortgage1RecordingMonth')['Mortgage1Amount'].mean().reset_index().rename(columns={
        'Mortgage1RecordingMonth': 'Time',
        'Mortgage1Amount': 'Average Loan Amount'
    })

    # Create Altair chart for time-series of loan amounts
    time_series_chart = alt.Chart(df_avg_amount).mark_line(point=True).encode(
        x=alt.X('Time:T', title='Time', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Average Loan Amount:Q', title='Average Loan Amount'),
        tooltip=[alt.Tooltip('yearmonth(Time):T', title='Month'), 
                 alt.Tooltip('Average Loan Amount:Q', title='Average Loan Amount')]
    ).properties(
        width=1000,
        height=400
    ).interactive()

    st.altair_chart(time_series_chart)

    # Filter by State
    st.markdown("#### Explore Loan Amounts by State")
    sorted_states = sorted(df['From Tax SitusStateCode'].unique())
    selected_state = st.selectbox('Select a state to check loan trends:', sorted_states)

    # Filter data by state
    df_state = df[df['From Tax SitusStateCode'] == selected_state]
    df_state_avg_amount = df_state.groupby('Mortgage1RecordingMonth')['Mortgage1Amount'].mean().reset_index().rename(columns={
        'Mortgage1RecordingMonth': 'Time',
        'Mortgage1Amount': 'Average Loan Amount'
    })

    # Time-series chart for state-specific loan amounts
    st.markdown(f"Average Loan Amounts in {selected_state} (May 2021 - May 2024)")
    state_time_series_chart = alt.Chart(df_state_avg_amount).mark_line(point=True).encode(
        x=alt.X('Time:T', title='Time', axis=alt.Axis(labelAngle=0)),
        y=alt.Y('Average Loan Amount:Q', title='Average Loan Amount'),
        tooltip=[alt.Tooltip('yearmonth(Time):T', title='Month'), 
                 alt.Tooltip('Average Loan Amount:Q', title='Average Loan Amount')]
    ).properties(
        width=1000,
        height=400
    ).interactive()

    st.altair_chart(state_time_series_chart)

    # Processing FIPS data for geographic visualization
    df['FIPS'] = df['From Tax SitusStateCountyFIPS'].astype(str).str[:-3]
    fips['FIPS'] = fips['FIPS'].astype(str)

    # Merge with FIPS data
    df1 = pd.merge(df, fips[['FIPS', 'State', 'State_abb', '2024_population']], on='FIPS', how='inner')
    df1['Mortgage1RecordingDate'] = pd.to_datetime(df1['Mortgage1RecordingDate'])

    # Date input for geographic visualization
    low_date = df1['Mortgage1RecordingDate'].min()
    high_date = df1['Mortgage1RecordingDate'].max()

    date_range = st.date_input(
        "Select the time period for geographic visualization",
        (low_date, high_date),
        min_value=low_date,
        max_value=high_date,
        format="MM.DD.YYYY"
    )

    # Error handling for date range selection
    if isinstance(date_range, tuple) and len(date_range) == 2:
        start_date, end_date = date_range
        df_filtered = df1[(df1['Mortgage1RecordingDate'] >= pd.to_datetime(start_date)) & (df1['Mortgage1RecordingDate'] <= pd.to_datetime(end_date))]
    else:
        st.error("Please select a valid date range.")
        return

    # Geographic Visualization of Average Loan Amount by State
    geo_data = df_filtered.groupby('State')['Mortgage1Amount'].mean().reset_index()
    geo_data = pd.merge(geo_data, fips[['State', 'State_abb', '2024_population']], on='State', how='inner')

    if start_date == end_date:
        st.markdown(f"### Geographic Visualization of Average Loan Amount on **{start_date.strftime('%B %d, %Y')}**")
    else:
        st.markdown(f"### Geographic Visualization of Average Loan Amount from **{start_date.strftime('%B %d, %Y')}** to **{end_date.strftime('%B %d, %Y')}**")

    # Choropleth map of loan amounts by state
    fig1 = px.choropleth(
        geo_data, 
        locations='State_abb',
        locationmode='USA-states',
        color='Mortgage1Amount',
        color_continuous_scale='Blues',
        scope="usa",
        labels={'Mortgage1Amount': 'Average Loan Amount'},
        hover_data=['State', 'Mortgage1Amount']
    )

    st.plotly_chart(fig1)

    # Density Plot for Loan Amounts (State-Level)
    dash_1 = st.container()
    with dash_1:
        col1, col2 = st.columns(2)
        with col1:
            d1 = st.date_input(
                "Select the time period for loan amount distribution:",
                (low_date, high_date),
                min_value=low_date,
                max_value=high_date,
                key="date_input_1"
            )
        with col2:
            selected_state1 = st.selectbox('Select a state to check distribution:', sorted_states)

    # Filter data for the density plot
    if isinstance(d1, tuple) and len(d1) == 2:
        start_d1, end_d1 = d1
        df_filtered_state = df1[(df1['Mortgage1RecordingDate'] >= pd.to_datetime(start_d1)) &
                                (df1['Mortgage1RecordingDate'] <= pd.to_datetime(end_d1)) &
                                (df1['From Tax SitusStateCode'] == selected_state1)]

        if df_filtered_state.empty:
            st.warning(f"No data available for {selected_state1} in the selected time period.")
        else:
            # Create an Altair violin/density plot for loan amounts
            violin_plot = alt.Chart(df_filtered_state).transform_density(
                'Mortgage1Amount',
                as_=['Amount', 'density'],
                extent=[df_filtered_state['Mortgage1Amount'].min(), df_filtered_state['Mortgage1Amount'].max()]
            ).mark_area(opacity=0.5).encode(
                x=alt.X('Amount:Q', title='Residential Loan Amount'),
                y=alt.Y('density:Q', title='Density')
            ).properties(
                width=1000,
                height=400,
                title=""
            )

            st.altair_chart(violin_plot)
    else:
        st.error("Please select a valid date range.")

if __name__ == "__main__":
    app()
