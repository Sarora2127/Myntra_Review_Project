# pages > generate_analysis.py
import pandas as pd
import streamlit as st
from src.cloud_io import MongoIO
from src.constants import SESSION_PRODUCT_KEY
# from src.utils import fetch_product_names_from_cloud
from src.data_report.generate_data_report import DashboardGenerator

mongo_con = MongoIO()
def create_analysis_page(review_data: pd.DataFrame):
    if review_data is not None: # if there is data
        st.dataframe(review_data)
        if st.button("Generate Analysis"): # if generate analysis button is clicked
            dashboard = DashboardGenerator(review_data) # create dashboard object
            # Display General Information
            dashboard.display_general_info() 
            # Display product-specific sections
            dashboard.display_product_sections() # generate analysis section
            dashboard.display_sales_prediction() # ML model prediction

try:
    if 'data' in st.session_state:
        data = mongo_con.get_reviews(product_name = st.session_state[SESSION_PRODUCT_KEY]) # fetch session data from mongo db
        create_analysis_page(data) # create analysis
    else:
        with st.sidebar: # error in sidebar
            st.markdown("""No Data Available for Analysis. Please Go to Search Page for Analysis""")
except AttributeError:
    product_name = None
    st.markdown(""" # No Data Available for Analysis.""")