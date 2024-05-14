
import os
import streamlit as st
from helper_functions import make_get_request
from database import *

def request_filling_history(company_number):
    """
    Makes a GET request to the Companies House API to retrieve the filing history of a company.

    Parameters
    ----------
    company_number : str, optional
        The company number for which the filing history is requested.

    Returns
    -------
    dict
        A JSON object containing a list of filings for the specified company.
    """
    # Construct the API endpoint URL with the specified company number FILLING HISTORY
    url = f"https://api.company-information.service.gov.uk/company/{company_number}/filing-history"

    response = make_get_request(url, headers=None)

    return response.json()

def clean_name_for_dynamodb(name):
    cleaned_name = ''.join(e if e.isalnum() or e in ['_', '-', '.', ' '] else '' for e in name)
    return cleaned_name[:255]

def get_company_name(company_number):
    """
    Retrieves the company name from the provided company number and formats it with underscores.

    Parameters
    ----------
    company_number : str
        The company number to retrieve the company name.

    Returns
    -------
    str
        The company name with spaces replaced by underscores.
    """
    try:
        url = f"https://api.company-information.service.gov.uk/company/{company_number}"
        response = make_get_request(url, headers=None)
        company_info = response.json()
        company_name = company_info["company_name"]
        company_name = clean_name_for_dynamodb(company_name)
        return company_name

    except Exception as e:
        print(f"Error occurred while retrieving company name: {e}")
        return None


def get_company_profile(company_number):
    """
    Retrieves the company information from the provided company number.

    Parameters
    ----------
    company_number : str
        The company number to retrieve the company information.

    Returns
    -------
    dict
        A dictionary containing the company information.
        Returns None if an exception occurs.
    """
    try:
        url = f"https://api.company-information.service.gov.uk/company/{company_number}"
        response = make_get_request(url, headers=None)
        company_info = response.json()
        return company_info

    except Exception as e:
        print(f"Error occurred while retrieving company information: {e}")
        return None


def get_first_accounts_item(json_data):
    """
    Filters the first accounts item from the provided JSON data that matches the specified conditions.

    Parameters
    ----------
    json_data : dict
        The JSON data from which to filter the accounts item.

    Returns
    -------
    dict
        The first accounts item in the JSON data that matches the specified conditions.
        Returns None if no such item is found.
    """
    first_accounts_item = next(
        (
            item
            for item in json_data["items"]
            if item["type"] == "AA"
            # and item["description"].startswith("accounts-with-accounts")
        ),
        None,
    )
    return first_accounts_item


def retrieve_documents_url(first_accounts_item):
    """
    Retrieves the link to the document metadata from the first accounts item.

    Parameters
    ----------
    first_accounts_item : dict
        The first accounts item from which to retrieve the document metadata link.

    Returns
    -------
    str
        The link to the document metadata in the first accounts item.
        Returns None if the first accounts item is None.
    """
    if first_accounts_item:
        link_to_file = first_accounts_item["links"]["document_metadata"]
        return link_to_file
    else:
        return None


def retrieve_type_from_accounts_item(first_accounts_item):
    """
    Retrieves the type from the first accounts item.

    Parameters
    ----------
    first_accounts_item : dict
        The first accounts item from which to retrieve the type.

    Returns
    -------
    str
        The type in the first accounts item.
        Returns None if the first accounts item is None or if the type is not present.
    """
    if first_accounts_item and "type" in first_accounts_item:
        return first_accounts_item["type"]
    else:
        return None


def retrieve_date_from_accounts_item(first_accounts_item):
    """
    Retrieves the date from the first accounts item.

    Parameters
    ----------
    first_accounts_item : dict
        The first accounts item from which to retrieve the date.

    Returns
    -------
    str
        The date in the first accounts item.
        Returns None if the first accounts item is None or if the date is not present.
    """
    if first_accounts_item and "date" in first_accounts_item:
        return first_accounts_item["date"]
    else:
        return None


# HERE


def retrieve_xhtml_doc(url, company_number, company_name, date_str, type_str):
    """
    Retrieves the XHTML document from the provided URL and saves it to a directory.

    Parameters
    ----------
    url : str
        The URL from which to retrieve the XHTML document.
    company_number : str
        The company number to include in the saved file name.
    company_name : str
        The company name to include in the saved file name.
    date_str : str
        The date to include in the saved file name.
    type_str : str
        The type to include in the saved file name.

    Returns
    -------
    str
        The file path of the saved XHTML document.
    """
    try:
        # first retrieve the json object containing the documents (pdf + xhtml possibly)
        response = make_get_request(url, headers=None)
        url = response.json()["links"]["document"]

        # Then retrieve the desired document
        headers = {"Accept": "application/xhtml+xml"}
        response = make_get_request(url, headers)

        # the response should be a binary of the xhtml file
        xhtml_content = response.content.decode("utf-8")

        # Create the xhtml directory if it does not exist
        output_directory = "xhtml"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Save the xhtml file with company_number, date_str, type_str, and company_name in the file name
        file_name = f"{company_number}_{type_str}_{date_str}_{company_name}.xhtml"
        output_file_path = os.path.join(output_directory, file_name)

        with open(output_file_path, "w", encoding="utf-8") as file:
            file.write(xhtml_content)
        # insert_xhtml_to_dynamodb(company_number, type_str, xhtml_content)

        return file_name
    
    except Exception as e:
        print(f"Error occurred while retrieving and saving XHTML document: {e}")
        return None


def retrieve_pdf_doc(url, company_number, company_name, date_str, type_str):
    """
    Retrieves the PDF document from the provided URL and saves it to a directory.

    Parameters
    ----------
    url : str
        The URL from which to retrieve the PDF document.
    company_number : str
        The company number to include in the saved file name.
    company_name : str
        The company name to include in the saved file name.
    date_str : str
        The date to include in the saved file name.
    type_str : str
        The type to include in the saved file name.

    Returns
    -------
    str
        The file path of the saved PDF document.
    """
    try:
        # first retrieve the json object containing the documents (pdf + xhtml possibly)
        response = make_get_request(url, headers=None)
        url = response.json()["links"]["document"]

        # Then retrieve the desired document
        headers = {"Accept": "application/pdf"}
        response = make_get_request(url, headers)

        # the response should be a binary of the pdf file
        pdf_content = response.content

        # Create the pdf directory if it does not exist
        output_directory = "pdf"
        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        # Save the pdf file with company_number, date_str, type_str, and company_name in the file name
        file_name = f"{company_number}_{type_str}_{date_str}_{company_name}.pdf"
        output_file_path = os.path.join(output_directory, file_name)

        with open(output_file_path, "wb") as file:
            file.write(pdf_content)

        return file_name

    except Exception as e:
        print(f"Error occurred while retrieving and saving PDF document: {e}")
        return None

@st.cache_data
def download_pdf(company_number):
    # This function downloads a PDF document for a given company number
    try:
        # Request the filling history of the company
        json = request_filling_history(company_number=company_number)
        # Get the first accounts item from the filling history
        item = get_first_accounts_item(json)

        # Retrieve the company name, date, and type from the accounts item
        company_name = get_company_name(company_number)
        date_str = retrieve_date_from_accounts_item(item)
        type_str = retrieve_type_from_accounts_item(item)

        # Retrieve the URL of the documents
        url = retrieve_documents_url(item)
        # Retrieve and save the PDF document
        doc = retrieve_pdf_doc(
            url, company_number, company_name, date_str=date_str, type_str=type_str
        )

        # Return the path of the saved PDF document along with date and name strings
        return doc, date_str, company_name

    except Exception as e:
        # Print the error message if an exception occurs
        print(f"Error occurred while downloading PDF: {e}")
        # Return None if an exception occurs
        return None, None, None

@st.cache_data
def download_xhtml(company_number):
    # This function downloads an XHTML document for a given company number
    try:
        # Request the filling history of the company
        json = request_filling_history(company_number=company_number)
        # Get the first accounts item from the filling history
        item = get_first_accounts_item(json)

        # Retrieve the company name, date, and type from the accounts item
        company_name = get_company_name(company_number)
        date_str = retrieve_date_from_accounts_item(item)
        type_str = retrieve_type_from_accounts_item(item)

        # Retrieve the URL of the documents
        url = retrieve_documents_url(item)
        # Retrieve and save the XHTML document
        doc = retrieve_xhtml_doc(
            url, company_number, company_name, date_str=date_str, type_str=type_str
        )

        # Return the path of the saved XHTML document along with date and name strings
        return doc, date_str, company_name

    except Exception as e:
        # Print the error message if an exception occurs
        print(f"Error occurred while downloading XHTML: {e}")
        # Return None if an exception occurs
        return None, None, None

@st.cache_data
def check_for_xhtml(item):
    """
    Check if the given item contains an XHTML document.

    Parameters:
    item (dict): The item to check for XHTML document.

    Returns:
    bool: True if the item contains an XHTML document, False otherwise.
    """
    link_to_file = item["links"]["document_metadata"]
    response = make_get_request(link_to_file, headers=None)
    # print(response.json()['resources'])
    if "application/xhtml+xml" in response.json()["resources"]:
        return True
    else:
        return False

@st.cache_data
def check_for_xhtml_and_pdf(company_number):
    """
    Download XHTML and PDF documents for a given company number.

    Parameters:
    company_number (str): The company number for which the documents are to be downloaded.

    Returns:
    bool: True if the documents are downloaded successfully, False otherwise.
    """
    # Request the filling history of the company
    json = request_filling_history(company_number=company_number)
    # Get the first accounts item from the filling history
    item = get_first_accounts_item(json)

    check = check_for_xhtml(item)
    if check:
        # download_xhtml(company_number)
        # download_pdf(company_number)
        return True
    else:
        # download_pdf(company_number)
        return False