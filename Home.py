import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import altair as alt
import numpy as np

# Load data
cdfi = pd.read_csv("CDFI_Cert_List_06-17-2024_Final.csv")
number_cdfi = pd.read_csv("Total_CDFI_1004.csv")
table1 = pd.read_csv("Table1.csv")
table2 = pd.read_csv("Table2.csv")
table3 = pd.read_csv("Table3.csv")

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
    with st.expander("📋 View Full CDFI List (as of June 17, 2024)"):
        st.dataframe(cdfi)

    # Display number of loans by CDFI with better structure and clarity
    st.markdown("### 💼 **CDFI Data Extracted from HMDA 2022-2023 (Depository and Loan Fund)**")
    st.dataframe(table1)

    # Display number of loans by CDFI with better structure and clarity
    st.markdown("### 💼 **CDFI Loan Fund Data Extracted from ATTOM 2022-2023 (Loan Fund Only)**")
    st.markdown("##### 2022 ATTOM reporting Total: $8,311,175,400.00")
    st.markdown("##### 2023 ATTOM reporting Total: $4,466,844,730.00")
    st.dataframe(table2)

    st.markdown("### 💼 **CDFI Loan Fund Data Discrepancies Between HMDA and ATTOM Extracts 2022-2023**")
    st.dataframe(table3)

    # Add more interactivity (multi-select filter by state, sorted alphabetically)
    #st.markdown("#### 🌍 **Filter by State**")

    # Sort the unique states alphabetically
    #sorted_states = sorted(table1['State'].unique())

    # Create a multi-select dropdown to filter by state
    #selected_states = st.multiselect('Select one or more states to filter CDFI data:', sorted_states)

    # Filter data based on the selected states
    #if selected_states:
        #filtered_data = number_cdfi[number_cdfi['State'].isin(selected_states)]
        #st.dataframe(filtered_data)
    #else:
        #st.write("Please select at least one state to view data.")


if __name__ == "__main__":
    app()

