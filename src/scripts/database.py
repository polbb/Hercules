from decimal import Decimal
import boto3
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os
import numpy as np
import streamlit as st
from boto3.dynamodb.conditions import Attr
from helper_functions import load_document_from_openai, make_get_request
from utils import RATIOS
import requests

aws_access_key_id = st.secrets.AWS_ACCESS_KEY_ID
aws_secret_access_key = st.secrets.AWS_SECRET_ACCESS_KEY
aws_default_region = st.secrets.AWS_DEFAULT_REGION

# load_dotenv('./.env.txt')
# aws_access_key_id = os.getenv('AWS_ACCESS_KEY_ID')
# aws_secret_access_key = os.getenv('AWS_SECRET_ACCESS_KEY')
# aws_default_region = os.getenv('AWS_DEFAULT_REGION')

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

def get_sic_code(company_number):
    try:
        table_name = 'company_profile'
        table = dynamodb.Table(table_name)

        # Get a single item
        response = table.get_item(
            Key={
                'companyID': company_number
            },
            ProjectionExpression='profile.sic_codes'
        )
        print('Success: Value retrieved successfully')
        return response['Item']['profile']['sic_codes']
    except Exception as e:
        print(f"Error: {e}")
        return None

def get_gics_code(company_number):
    url = "https://3il04h84ea.execute-api.eu-west-2.amazonaws.com/classify-upload/"

    table = dynamodb.Table('company_xhtml')

    try:
        # Get the file from DynamoDB using the file ID
        response = table.get_item(
            Key={
                'companyID': company_number
            }
        )
        file_content = response['Item']['xhtml']  # Assuming the file content is stored under the 'xhtml' key
        print("File content retrieved successfully.")
    except Exception as e:
        print(f"Error retrieving file content: {e}")
        return None

    # Parse the HTML content
    soup = BeautifulSoup(file_content, 'html.parser')

    # Extract all text from the HTML
    all_text = soup.get_text()
    # st.write(f'before sic: {all_text}')

    # # Get SIC code and append to the text file:
    # sic_code = get_sic_code(company_number)

    # # Get company profile info
    # profile_json = get_company_profile(company_number)


    # # Extract all text from the HTML and prepend the SIC code
    # all_text = f"SIC Code: {profile_json}\n {all_text}" 
    # st.write(f'after sic: {all_text}')

    files = {
        'file': (f'{company_number}.txt', all_text, 'text/plain')
    }
    headers = {
        'accept': 'application/json',
    }
    response = requests.post(url, files=files, headers=headers)

    if response.status_code == 200:
        response_json = response.json()
        # Return 'sub_industry' if it exists, otherwise return the whole json response
        return response_json.get('sub_industry', response_json)
    else:
        print(f"Error: Received status code {response.status_code}")
        return None



       
def put_item_to_dynamodb(table, item):
    table = dynamodb.Table(table)
    response = table.put_item(
        Item=item
    )
    return response

def get_ixbrl_data_from_dynamodb(company_number):
    table_name = 'company_ixbrl_data'
    table = dynamodb.Table(table_name)

    try:
        response = table.get_item(
            Key={
                'companyID': company_number
            },
            ProjectionExpression='ixbrlData'
        )
        print('Success: Value retrieved successfully')
        
        # Filter out items with empty lists
        filtered_response = {k: v for k, v in response['Item']['ixbrlData'].items() if v and isinstance(v, list) and any(v)}
        
        return filtered_response
    except Exception as e:
        print(f"Error: {e}")
        return None
    
# def get_ixbrl_data_from_dynamodb(company_number):
#     table_name = 'company_ixbrl_data'
#     table = dynamodb.Table(table_name)

#     try:
#         response = table.get_item(
#             Key={
#                 'companyID': company_number
#             },
#             ProjectionExpression='ixbrlData'
#         )
#         print('Success: Value retrieved successfully')
#         return response
#     except Exception as e:
#         print(f"Error: {e}")
#         return None

def get_item_from_dynamodb(table, item):
    table = dynamodb.Table(table)
    item = table.get_item(
        Key=item
    )
    return item

def get_item_from_dynamodb_primery_key_only(company_number, table):
    table = dynamodb.Table(table)
    item = table.get_item(
        Key={
            'companyID': {'S': company_number}
        }
    )
    return item


def connect_to_dynamodb():
    try:
        dynamodb = boto3.resource(
            'dynamodb',
            region_name=aws_default_region,
            aws_access_key_id=aws_access_key_id,
            aws_secret_access_key=aws_secret_access_key
        )
        print("Successfully connected to DynamoDB")

    except Exception as e:

        print(f"Error occurred while connecting to DynamoDB: {e}")

    return dynamodb

def get_attribute_value(companyID, table_name, attribute_name):
    table = dynamodb.Table(table_name)
    response = table.get_item(
        Key={
            'companyID': companyID
        },
        ProjectionExpression=attribute_name
    )

    item = response.get('Item', {})
    attribute_value = item.get(attribute_name)

    if attribute_value is not None:
        # print(f'The value of {attribute_name} is: {attribute_value}')
        return attribute_value
    else:
        # print(f'{attribute_name} does not exist or is null {companyID}')
        return None
    
def get_all_attributes_for_company(company_id):
    """
    Retrieves all attributes for a company from the DynamoDB table.

    Args:
        company_id (str): The ID of the company to retrieve attributes for.

    Returns:
        dict: A dictionary containing all attributes of the company.

    Raises:
        Exception: If an error occurs during the retrieval process.
    """
    try:
        table_name = 'company_ratios'
        table = dynamodb.Table(table_name)

        # Get a single item with all attributes
        response = table.get_item(
            Key={
                'companyID': company_id
            }
        )
        print('Success: Value retrieved successfully')
        return response['Item']
    except Exception as e:
        print(f"Error: {e}")
        return {}
    
def get_sme_group(total_assets):
    import numpy as np

    lower = int(total_assets*0.7)
    upper = int(total_assets*1.3)

    try:
        table_name = 'company_ratios'
        table = dynamodb.Table(table_name)

        # Scan the table for items with total assets 30% above and below the reference value
        response = table.scan(
            FilterExpression=Attr('total_assets').between(lower, upper)
        )

        # st.write(response['Items'])

        if 'Items' in response:
            total_assets_values = [float(item['total_assets']) for item in response['Items']]
            # st.write(total_assets_values)

            q1, q3 = np.percentile(total_assets_values, [25, 75])
            # st.write(f'q1 q3: {q1, q3}')

            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr


            # Filter items that fall between the lower and upper fence
            filtered_items = []
            for item in response['Items']:
                total_assets_value = float(item['total_assets'])
                # st.write(f'total ass value before check: {total_assets_value}')
                # st.write(f'lower fence: {lower_fence}')
                # st.write(f'upper fence: {upper_fence}')
                if total_assets_value > lower_fence and total_assets_value < upper_fence:
                    filtered_items.append(item)

            # st.write(f'filtered items: {filtered_items}')

            if filtered_items:
                # st.write('returned fneced items')
                return filtered_items


            else:
                st.warning('No items found within the specified quartile range')
                return {}
        else:
            st.warning('No items found within the specified range')
            return {}
    except Exception as e:
        st.warning(f"Error: {e}")
        return {}

def calculate_financial_ratios(df):
    # Calculate financial ratios
    df['wc_ratio'] = df.apply(lambda x: float(x['current_assets']) / float(x['creditors']) if x['current_assets'] is not None and x['creditors'] is not None and x['creditors'] != 0 else None, axis=1)
    df['quick_ratio'] = df.apply(lambda x: (float(x['current_assets']) - float(x['inventory_prepaid_expenses'])) / float(x['creditors']) if x['current_assets'] is not None and x['inventory_prepaid_expenses'] is not None and x['creditors'] is not None and x['creditors'] != 0 else None, axis=1)
    df['itr_ratio'] = df.apply(lambda x: float(x['cost_of_sales']) / float(x['stocks']) if x['cost_of_sales'] is not None and x['stocks'] is not None and x['stocks'] != 0 else None, axis=1)
    df['wr_score'] = df.apply(lambda x: (float(x['current_assets']) / float(x['total_assets'])) / (float(x['creditors']) / float(x['total_assets'])) if x['current_assets'] is not None and x['total_assets'] is not None and x['creditors'] is not None and x['creditors'] != 0 else None, axis=1)
    df['gap_index'] = df.apply(lambda x: ((float(x['itr_ratio']) / float(x['wr_score'])) * 100) if x['itr_ratio'] is not None and x['wr_score'] is not None else None, axis=1)
    df['cash_ratio'] = df.apply(lambda x: float(x['cash_and_cash_equivalents']) / float(x['creditors']) if x['cash_and_cash_equivalents'] is not None and x['creditors'] is not None and x['creditors'] != 0 else None, axis=1)
    return df

def calculate_statistics(df):
    """
    Calculate basic statistics for each numeric column in a DataFrame, excluding 'companyID'.
    
    This function computes the minimum, maximum, and median values for each column after filtering out outliers
    based on the interquartile range (IQR). Outliers are defined as values below Q1 - 1.5*IQR or above Q3 + 1.5*IQR.
    
    Parameters:
    - df (pd.DataFrame): The DataFrame containing the data to analyze.
    
    Returns:
    - dict: A dictionary where each key is a column name and each value is another dictionary with 'min', 'max', and 'median' statistics.
    """
    # Generate statistics for each column in the DataFrame
    ratios = RATIOS
    statistics = {}
    for column in df.columns:
        if column != 'companyID':
            # Convert column values to float if they are of type Decimal (needed to avoid error)
            df[column] = df[column].apply(lambda x: float(x) if isinstance(x, Decimal) else x)
            
            # Calculate quartiles and interquartile range for each column. Leave out outliers
            q1 = df[column].quantile(0.25)
            q3 = df[column].quantile(0.75)
            iqr = q3 - q1
            lower_fence = q1 - 1.5 * iqr
            upper_fence = q3 + 1.5 * iqr
            
            # Filter values within the interquartile range
            filtered_df = df[column][(df[column] >= lower_fence) & (df[column] <= upper_fence)]
            
            # Calculate and store statistics for the column in a dict
            statistics[column] = {
                'min': round(float(filtered_df.min()), 2),
                'max': round(float(filtered_df.max()), 2),
                'median': round(float(filtered_df.median()), 2)
            }
    return statistics



def check_company_profile_exists(company_id):
    table_name = 'company_profile'
    table = dynamodb.Table(table_name)
    try:
        response = table.get_item(
            Key={
                'companyID': company_id
            }
        )
        if 'Item' in response:
            return True
        else:
            return False
    except Exception as e:
        print(f"Error checking company profile exists: {e}")
        return False



 # connect to DynamoDB table
dynamodb = connect_to_dynamodb()   
