import os
import pickle
from bs4 import BeautifulSoup
from utils import ix_financial_values, ix_all_data_dictionary
import streamlit as st


@st.cache_data
def retreive_financial_values_xhtml(xhtml_file_path, date_str_ix, name_str_ix):
    """
    Retrieve financial values from the XHTML file.
    
    Args:
        xhtml_file_path (str): The file path of the XHTML file.
        date_str_ix (str): The date string.
        name_str_ix (str): The name string.
    
    Returns:
        dict: A dictionary containing the financial values.
    """
    # Open the file and parse the html
    with open(xhtml_file_path, 'r', encoding='utf-8') as file:
        html = file.read()
        soup = BeautifulSoup(html, 'html.parser')
    
    # dict_name = f"financial_values_{name_str_ix}_{date_str_ix}"
    dict_name = {}

    for label in ix_financial_values:

        if label:
            # Find the row containing "Cost of sales"
            element = soup.select(f'ix\\:nonfraction[name$={label}]')

            temp_list = []
            for item in element:
                    temp_list.append(item.text)

            dict_name[label] = temp_list
            # print(element.text)
            # Print or process the found CostSales
            print(label, dict_name[label])

    pkl_dir = 'pkl'
    if not os.path.exists(pkl_dir):
        os.makedirs(pkl_dir)

    with open(os.path.join(pkl_dir, f'{date_str_ix}_{name_str_ix}_ix_financial_values.pkl'), 'wb') as handle:
        pickle.dump(dict_name, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return dict_name

@st.cache_data
def retreive_all_ix_financial_data(xhtml_file_path, date_str_ix, name_str_ix):
    """
    Retrieve financial values from the XHTML file.
    
    Args:
        xhtml_file_path (str): The file path of the XHTML file.
        date_str_ix (str): The date string.
        name_str_ix (str): The name string.
    
    Returns:
        dict: A dictionary containing the financial values.
    """
    # Open the file and parse the html
    with open(xhtml_file_path, 'r', encoding='utf-8') as file:
        html = file.read()
        soup = BeautifulSoup(html, 'html.parser')
    
    # dict_name = f"financial_values_{name_str_ix}_{date_str_ix}"
    dict_name = {}

    for label in ix_all_data_dictionary:

        if label:
            # Find the row containing "Cost of sales"
            # element = soup.select(f'ix\\:nonfraction[name$={label}]')
            # element = soup.select(f'ix\\:[name$={label}]')
            element = soup.select(f'[name$={label}]')

            temp_list = []
            for item in element:
                    # temp_list.append(item.text)
                    temp_list.append(item.text)

            dict_name[label] = temp_list
            # print(element.text)
            # Print or process the found CostSales
            # print(label, dict_name[label])

    pkl_dir = 'pkl'
    if not os.path.exists(pkl_dir):
        os.makedirs(pkl_dir)

    with open(os.path.join(pkl_dir, f'{date_str_ix}_{name_str_ix}_ix_all_financial_data.pkl'), 'wb') as handle:
        pickle.dump(dict_name, handle, protocol=pickle.HIGHEST_PROTOCOL)

    return dict_name
