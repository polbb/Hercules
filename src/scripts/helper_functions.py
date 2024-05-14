import platform
import re
import sys
import time
import numpy as np
import pandas as pd
import pytesseract
from pdf2image import convert_from_path
import requests
import streamlit as st
from dotenv import load_dotenv
import os



def extract_numeric_value(text):
    # Define the regex pattern to match numeric values with commas and optional pound symbol
    pattern = r"£?([\d,]+)"

    # Search for the pattern in the text
    match = re.search(pattern, text)

    if match and match.group(1).replace(",", "").isdigit():  # Check if the matched value contains only digits
        # Extract the matched numeric value and remove commas if present
        numeric_value_str = match.group(1).replace(",", "")
        # print(f'string: {numeric_value_str}')

        # Convert the numeric value to an integer
        numeric_value_int = int(numeric_value_str)

        return numeric_value_int, numeric_value_str
    else:
        return None, None
    
def extract_numeric_value_int(text):
    # Define the regex pattern to match numeric values with commas and optional pound symbol
    pattern = r"£?([\d,]+)"

    # Search for the pattern in the text
    match = re.search(pattern, text)

    if match and match.group(1).replace(",", "").isdigit():  # Check if the matched value contains only digits
        # Extract the matched numeric value and remove commas if present
        numeric_value_str = match.group(1).replace(",", "")
        # print(f'string: {numeric_value_str}')

        # Convert the numeric value to an integer
        numeric_value_int = int(numeric_value_str)

        return numeric_value_int
    else:
        return None
    
def wait_on_run(client, run, thread):
    spinner = ['|', '/', '-', '\\']
    idx = 0
    while run.status == "queued" or run.status == "in_progress":
        run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)
        sys.stdout.write('\r' + spinner[idx % len(spinner)] + ' ' + run.status)
        sys.stdout.flush()
        # time.sleep(1)
        idx += 1
    sys.stdout.write('\rDone!          \n')
    return run
    


# def wait_on_run(client, run, thread):
#     while run.status == "queued" or run.status == "in_progress":
#         run = client.beta.threads.runs.retrieve(run_id=run.id, thread_id=thread.id)
#         time.sleep(2)
#         print(run.status)
#     return run


def display_thread_messages(messages):
    for thread_message in messages.data:
        print(thread_message.content[0].text.value)
        print("-" * 120)


def create_thread_message_lists(messages):
    messages_list = []
    for thread_message in messages.data:
        messages_list.append(thread_message.content[0].text.value)
    return messages_list


def upload_document(client, file_name):
    # directory path to file
    filename = file_name
    # Upload file to openai (create a file object)
    file = client.files.create(file=open(filename, "rb"), purpose="assistants")
    return file


def create_thread(client):
    thread = client.beta.threads.create()
    return thread


def load_document_from_openai(client, file_id):
    file = client.files.retrieve(file_id=file_id)
    return file


def extract_pdf_name(pdf_filename):
    # Check if the filename ends with '.pdf'
    if pdf_filename.endswith(".pdf"):
        # Remove the '.pdf' extension
        pdf_name = pdf_filename[:-4]
        return pdf_name
    else:
        return None  # Return None if the filename doesn't end with '.pdf'


def convert_pdf_to_text(file_name):
    pdf_path = file_name

    # Detect the operating system
    system = platform.system()

    if system == "Linux":
        poppler_path = "/usr/bin"
    elif system == "Windows":
        # Set the path to the Poppler bin directory on Windows
        poppler_path = r"C:\path\to\poppler\bin"
    elif system == "Darwin":  # macOS
        poppler_path = "/opt/homebrew/bin"
    else:
        # Unsupported operating system
        raise OSError(f"Unsupported operating system: {system}")

    images = convert_from_path(pdf_path, poppler_path=poppler_path)

    # Accumulate text from all pages
    all_text = ""

    for i, image in enumerate(images):
        # Use pytesseract to extract text from the image
        text = pytesseract.image_to_string(image)

        # Accumulate the extracted text
        all_text += f"Page {i + 1} Text:\n{text}\n\n"
    return all_text


def save_text_file(file_name, text):
    with open(file_name, "w", encoding="utf-8") as output_file:
        output_file.write(text)


def format_currency(amount):
    # Format the integer amount as a currency string with commas for thousands separators
    if amount is None:
        return "Amount is None"

    try:
        amount = int(amount)
    except ValueError as e:
        return f"Error: {e}"

    currency_string = f"£{amount:,}"
    return currency_string


def make_get_request(url, headers):
    # Companies House API key
    # api_key = st.secrets.ch
    load_dotenv('./.env.txt')
    api_key = os.getenv('ch')

    # Make a GET request to the Companies House API
    response = requests.get(
        url, auth=(api_key, ""), headers=headers
    )  # both lines of code work

    # Check if the request was successful (status code 200)
    if response.status_code == 200:
        # Print the JSON response if successful
        print("Response successful: status code 200")
        print(url)
    else:
        # Print an error message with the status code and response text if not successful
        print(f"Error: {response.status_code} - {response.text}")

    return response

def make_dataframe(results):
    df = pd.DataFrame(results)
    df.set_index('companyID', inplace=True)
    return df

# def display_metrics(name, ratio, stats={}):
#     col1, col2, col3, col4 = st.columns([3,1,1,1])
#     col1.metric(name, f"{round(ratio, 2)}", delta=f"{round(np.random.uniform(-10, 10), 1)}%")
    
#     try:
#         if ratio in stats:
#             col2.metric(label="Comp Median", value=round(stats['median'], 2), delta=f"{round(np.random.uniform(-10, 10), 1)}%")
#             col3.metric(label="Comp Min", value=round(stats['min'], 2), delta=f"{round(np.random.uniform(-10, 10), 1)}%")
#             col4.metric(label="Comp Max", value=round(stats['max'], 2), delta=f"{round(np.random.uniform(-10, 10), 1)}%")
#     except UnboundLocalError as e:
#         st.warning(f"Error: {e}")

def display_metrics(name, ratio, stats):
    col1, col2, col3, col4 = st.columns([3,1,1,1])
    col1.metric(name, f"{round(ratio, 2)}", delta=f"{round(np.random.uniform(-10, 10), 1)}%")
    col2.metric(label="Comp Median", value=round(stats['median'], 2), delta=f"{round(np.random.uniform(-10, 10), 1)}%")
    col3.metric(label="Comp Min", value=round(stats['min'], 2), delta=f"{round(np.random.uniform(-10, 10), 1)}%")
    col4.metric(label="Comp Max", value=round(stats['max'], 2), delta=f"{round(np.random.uniform(-10, 10), 1)}%")