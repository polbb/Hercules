# APP VERSION v0.1-D
import streamlit as st

# from openai import OpenAI
from document_retrieval import download_pdf, check_for_xhtml_and_pdf, get_company_name
from streanlit_pdf import streamlit_pdf
from streamlit_xhtml import streamlit_xhtml
from retrieve_values import *
# from dotenv import load_dotenv
import os
from database import *

# # initialize client
# load_dotenv('./.env.txt')

# # initialize client
# openai_key = os.environ.get('openai') # same as os.getenv('openai)
# client = OpenAI(api_key=openai_key)

# # BELOW IS FOR STREAMLIT DEPLOYMENT
# client = OpenAI(api_key=st.secrets.openai)
with open( "src/scripts/style.css" ) as css:
    st.markdown( f'<style>{css.read()}</style>' , unsafe_allow_html= True)
    

# st. set_page_config(layout="wide")
# title
st.title("ArgoXai")
st.subheader("HERCULES - Contextual Financial Reviewer (Release G2)")


col1, col2, col3, c4, c5, c6, c7 ,c8 = st.columns([3,3,1,1,1,1,1,1])
company_number = col1.text_input("Enter the company number")
iterations = col2.number_input("How many review vectors?", value=1)



calculate_ratio = st.button("Start Analysis")


if calculate_ratio:  # calc ratio button pressed

    company_exists = check_company_profile_exists(company_number) #checking DB

    if company_exists:    
        # CHECK IF LATEST ACC HAS IXBRL
        has_xhtml = check_for_xhtml_and_pdf(company_number) # todo change to check DB

        # IF IX SAVE BOTH, IF NOT SAVE PDF
        if has_xhtml:  
            
            streamlit_xhtml(company_number)

            
        else:
            # # Below is the porcess of gathering pdf data and using GPT agents
            # pdf_file_path, date_str, name_str = download_pdf(company_number)
            # streamlit_pdf(client, iterations, pdf_file_path, date_str, name_str)
            name_str = get_company_name(company_number)
            st.warning(f'No ixbrl data available for company: {name_str}')
    else:
        st.warning(f"Data for company number {company_number} is not available yet")