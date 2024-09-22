import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt
import numpy as np

# Load data
cdfi = pd.read_csv("CDFI_Cert_List_06-17-2024_Final.csv")
number_cdfi = pd.read_csv("Total_CDFI_0921.csv")

# Streamlit application
def app():
    # Set wide layout and page title
    st.set_page_config(page_title='CDFI Residential Loan Dashboard', layout='wide')

    # Title section
    st.title('CDFI Residential Loan Dashboard')
    st.markdown("#### Analyzing residential loan trends from May 2021 to May 2024")

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
    st.markdown("### 🔍 **Research Questions**")
    st.markdown("""
    1. **What is the overall volume of residential loans over time?**
    2. **Which states have the highest demand for CDFI-approved loans?**
    3. **How does the average loan amount vary across states and CDFIs?**
    """)

    # Add horizontal space between sections
    st.markdown("---")

    # Display CDFI list with an expander for cleaner look
    with st.expander("📋 View Full CDFI List (as of June 17, 2024)"):
        st.dataframe(cdfi)

    # Display number of loans by CDFI with better structure and clarity
    st.markdown("### 💼 **Number of Loans by CDFI**")
    number_cdfi1 = number_cdfi[['Organization Name', 'Number', 'City', 'State', 'Zipcode', 'Address','Organization Website']]
    st.dataframe(number_cdfi1)

    # Add more interactivity (multi-select filter by state, sorted alphabetically)
    st.markdown("#### 🌍 **Filter by State**")

    # Sort the unique states alphabetically
    sorted_states = sorted(number_cdfi1['State'].unique())

    # Create a multi-select dropdown to filter by state
    selected_states = st.multiselect('Select one or more states to filter CDFI data:', sorted_states)

    # Filter data based on the selected states
    if selected_states:
        filtered_data = number_cdfi1[number_cdfi1['State'].isin(selected_states)]
        st.dataframe(filtered_data)
    else:
        st.write("Please select at least one state to view data.")


if __name__ == "__main__":
    app()

