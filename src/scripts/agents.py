from bs4 import BeautifulSoup
from helper_functions import *
from utils import agents_dict
from dotenv import load_dotenv
from openai import OpenAI
from document_retrieval import get_company_profile
from database import get_ixbrl_data_from_dynamodb


# # initialize client
# load_dotenv('./.env.txt')

# # initialize client
# openai_key = os.environ.get('openai') # same as os.getenv('openai)
# client = OpenAI(api_key=openai_key)

# BELOW IS FOR STREAMLIT DEPLOYMENT
client = OpenAI(api_key=st.secrets.openai)


def get_cost_of_sales_single_run(client, file_id='file-xlNVkVH1evbzzAkj9yCHrrtV'):
    # Update Agent
    instructions = (
        'You are an expert agent that can retrieve financial information from text files. '
        'The text files contain tables and rows that are not easily readable by humans. '
        'The text files was extracted from a pdf. '
        'The pdf was first converted to image then to text using OCR. '
        'The text contains financial statements. '
        'Your first task is to Identify the Income statement (it could have a different title). '
        'Final task is to identify the value for Cost of sales (it could be cost of goods or COGS). '
        'You must output the value for cost of sales. '
        ' Use the following template for your answer: The Cost of Sales value is £{insert value here}. '
        "The notation £'000 in financial statements represents thousands of British pounds (£) as the unit of "
        "currency. This notation is commonly used in financial reporting to express amounts in thousands of pounds "
        "rather than in the actual pound sterling value."
        "For example, if a financial statement displays a figure as £'000, it means that the actual amount "
        "represented is in thousands of pounds. So, if the figure is reported as £'000 500, it signifies £500,000."
        "Instruction about how to read financial statements in the UK are ins files id: file-R4qOl7s5TxfqCidK3FdG6pW3 "
        "and file-xJQfGcn1R3oXvfOx95hLnQTT"

    )

    # update the description and load assistant object
    assistant = client.beta.assistants.update(
        assistant_id=agents_dict['Financial_Miner_COGS'],
        instructions=instructions
    )

    # print(agents_dict['Financial_Miner_Text_Extractor'])

    # Create a thread
    thread = client.beta.threads.create()

    # Create a message
    message_content = (
        f'Read the document with file id {file_id}. '
        # 'Identify the Income statement (it could have a different title). '
        'Can you extract the Cost of sales numerical value from the text? (it could be cost of goods or COGS). '
        'Please do not ask any questions back. '
        'If you need to do further processing go ahead, no need to ask. '
        'Please give me a final answer with just the final number of the cost of sales, No words. Nothing else. '
        'Example answer: The Cost of Sales value is £10,000'
    )

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=message_content,
        file_ids=[file_id],
    )

    # Create a run
    run = client.beta.threads.runs.create(
        assistant_id=assistant.id,
        thread_id=thread.id,
    )

    wait_on_run(client=client, run=run, thread=thread)

    # Retrieve messages from thread
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        # order='asc'
    )

    display_thread_messages(messages)

    # create a list of messages that can be used to write a log
    messages_list = create_thread_message_lists(messages)

    # Example usage:
    text = messages_list[0]
    numeric_value_int, numeric_value_str = extract_numeric_value(text)
    # print("Numeric value:", numeric_value)

    return numeric_value_int, numeric_value_str


def get_inventory_single_run(client, file_id='file-xlNVkVH1evbzzAkj9yCHrrtV'):
    # Update Agent
    instructions = (
        'You are an expert agent that can retrieve financial information from text files. '
        'The text files contain tables and rows that are not easily readable by humans. '
        'The text files was extracted from a pdf. '
        'The pdf was first converted to image then to text using OCR. '
        'The text contains financial statements. '
        'Your first task is to Identify the balance sheet (it could have a different title). '
        'Final task is to identify the value for Inventory (it could be Stocks). '
        'You must output the value for Inventory. '
        'Use the following template for your answer: The Inventory value is £{insert value here}. '
        "The notation £'000 in financial statements represents thousands of British pounds (£) as the unit of "
        "currency. This notation is commonly used in financial reporting to express amounts in thousands of pounds "
        "rather than in the actual pound sterling value."
        "For example, if a financial statement displays a figure as £'000, it means that the actual amount "
        "represented is in thousands of pounds. So, if the figure is reported as £'000 500, it signifies £500,000."
        "Instruction about how to read financial statements in the UK are ins files id: file-R4qOl7s5TxfqCidK3FdG6pW3 "
        "and file-xJQfGcn1R3oXvfOx95hLnQTT"

    )

    # update the description and load assistant object
    assistant = client.beta.assistants.update(
        assistant_id=agents_dict['Financial_Miner_Inventory'],
        instructions=instructions
    )

    # print(agents_dict['Financial_Miner_Text_Extractor'])

    # Create a thread
    thread = client.beta.threads.create()

    # Create a message
    message_content = (
        f'Read the document with file id {file_id}. '
        # 'Identify the Balance Sheet (it could have a different title). '
        'Can you extract the Inventory numerical value from that text? (it could be also called stocks). '
        'Please do not ask any questions back. '
        'If you need to do further processing go ahead, no need to ask. '
        'Please give me a final answer with just the final number of the cost of sales, No words. Nothing else. '
        'Example answer: The Inventory value is £10,000'
    )

    message = client.beta.threads.messages.create(
        thread_id=thread.id,
        role='user',
        content=message_content,
        file_ids=[file_id],
    )

    # Create a run
    run = client.beta.threads.runs.create(
        assistant_id=agents_dict['Financial_Miner_Inventory'],
        thread_id=thread.id,
    )

    wait_on_run(client=client, run=run, thread=thread)

    # Retrieve messages from thread
    messages = client.beta.threads.messages.list(
        thread_id=thread.id,
        # order='asc'
    )

    display_thread_messages(messages)

    # create a list of messages that can be used to write a log
    messages_list = create_thread_message_lists(messages)

    # Example usage:
    text = messages_list[0]
    numeric_value_int, numeric_value_str = extract_numeric_value(text)
    # print("Numeric value:", numeric_value)

    return numeric_value_int, numeric_value_str


def get_cost_of_sales(client, file_id='file-xlNVkVH1evbzzAkj9yCHrrtV', number_of_iterations=1):
    cogs = {}
    for iteration in range(number_of_iterations):

        print('%' * 20)
        print(f'Iteration: {iteration}')
        print('%' * 20)
        value = None

        try:
            value, string = get_cost_of_sales_single_run(client, file_id)
        except Exception as e:
            print(f"Error occurred: {e}")
            # Return an empty dictionary if an error occurs

        if isinstance(value, int):
            if value in cogs:
                cogs[value] += 1
            else:
                cogs[value] = 1

    most_common_value = max(cogs, key=cogs.get) if cogs else None

    print(cogs)
    return most_common_value


def get_inventory(client, file_id='file-xlNVkVH1evbzzAkj9yCHrrtV', number_of_iterations=1):
    cogs = {}
    for iteration in range(number_of_iterations):

        print('%' * 20)
        print(f'Iteration: {iteration}')
        print('%' * 20)
        value = None

        try:
            value, string = get_inventory_single_run(client, file_id)
        except Exception as e:
            print(f"Error occurred: {e}")
            # Return an empty dictionary if an error occurs

        if isinstance(value, int):
            if value in cogs:
                cogs[value] += 1
            else:
                cogs[value] = 1

    most_common_value = max(cogs, key=cogs.get) if cogs else None

    print(cogs)
    return most_common_value


def get_cogs_xhtml(client, file_path=None, number_of_iterations=1):

    cogs = {}
    for iteration in range(number_of_iterations):

        print('%' * 20)
        print(f'Iteration: {iteration}')
        print('%' * 20)
        value = None

        try:
            value, string = get_cogs_xhtml_single_run(client, file_path)
        except Exception as e:
            print(f"Error occurred: {e}")
            # Return an empty dictionary if an error occurs

        if isinstance(value, int):
            if value in cogs:
                cogs[value] += 1
            else:
                cogs[value] = 1

    most_common_value = max(cogs, key=cogs.get) if cogs else None

    print(cogs)
    return most_common_value   

def get_inventory_xhtml(client, file_path=None, number_of_iterations=1):

    stocks = {}
    for iteration in range(number_of_iterations):

        print('%' * 20)
        print(f'Iteration: {iteration}')
        print('%' * 20)
        value = None

        try:
            value, string = get_stocks_xhtml_single_run(client, file_path)
        except Exception as e:
            print(f"Error occurred: {e}")
            # Return an empty dictionary if an error occurs

        if isinstance(value, int):
            if value in stocks:
                stocks[value] += 1
            else:
                stocks[value] = 1

    most_common_value = max(stocks, key=stocks.get) if stocks else None

    print(stocks)
    return most_common_value   

def get_cogs_xhtml_single_run(client, file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Find the row containing "Cost of sales"
    CostSales = soup.select('ix\\:nonfraction[name$="CostSales"]')
    # Print or process the found TotalInventories
    # for element in CostSales:
    #     print(element)

    # Extract the text from the first element
    cogs_text = CostSales[0].text
    # Remove commas and parentheses
    cogs, cogs_str = extract_numeric_value(cogs_text)

    return cogs, cogs_str

def get_stocks_xhtml_single_run(client, file_path):

    with open(file_path, 'r', encoding='utf-8') as file:
        html = file.read()

    soup = BeautifulSoup(html, 'html.parser')

    # Find the row containing "Cost of sales"
    TotalInventories = soup.select('ix\\:nonfraction[name$="TotalInventories"]')
    # Print or process the found TotalInventories
    # for element in CostSales:
    #     print(element)

    # Extract the text from the first element
    stocks_text = TotalInventories[0].text
    # Remove commas and parentheses
    stocks, stocks_str = extract_numeric_value(stocks_text)

    return stocks, stocks_str

def analyse_metrics(companyID, metrics, n, stats):
    # get profile
    profile = get_company_profile(companyID)
    # ixbrl_data = get_ixbrl_data_from_dynamodb(companyID)
    
    # st.write(ixbrl_data)
    # st.write(f'ixbrl: {ixbrl_data['Item']['ixbrlData']}')

    # Update agent
    instructions = (
    f'You are an expert as both, underwriter and financial analyst. '
    f'You will analyse the data provided of financial ratios for a small company in the UK. '
    f'You will compare all ratios againt the min, max and median of ratios for a set of similar companies. '
    f'Your goal is to aid the underwriter to make a good decision in terms of W&I. '
    f'After comparing all the data print thoughts and recommendations of how this company ITR performs in terms of the set. '
    )
    # instructions = (
    # f'You are an expert as both, underwriter and financial analyst. '
    # f'You will analyse the data provided of financial ratios for a small company in the UK. '
    # f'You will compare Inventory Turn Ratio againt the min, max and median of ITR for a set of similar companies. '
    # f'Your goal is to aid the underwriter to make a good decision in terms of W&I. '
    # f'After comparing all the data print thoughts and recommendations of how this company ITR performs in terms of the set. '
    # )

    # update the description and load assistnt object
    assistant = client.beta.assistants.update(
        assistant_id='asst_bshJqwnnjeNfhH4JbSo2BkAi',
        instructions=instructions
    )
    #create a thread
    thread = client.beta.threads.create()

    # create a message
    message_content = (
        f'I will give you financial data for a company. '
        f'Information about the company can be found in the file {profile}. Use this for overall context. '
        # f'Ixbrl data of the company is provided in the file  {ixbrl_data}. Make sure to read all this data to find relevant information. '
        f'Comparison Research Set (Comps) = {n} SME. '
        f'All the financial metrics for the company are: {metrics}. '
        f'The statistinc for the {n} SME set for the ITR are: '
        f'stats: {stats}. This is  python dictionary containin min, max, and median for a series of metrics, including itr.'
        f'Do a comparative analysis. '
        f'Tell about how company compares to the stats in terms of metrics. '
        f'What are the implications from an underwriter perspective?'
        f'The most important question: After analysing all metrics in context of the statistics of the set of SME... What are the chances that the company {companyID} might decrease in value?. '
        f'Be brief. '
        f'Please do not ask any questions back. '
        f'If you need to do further processing go ahead, no need to ask. '
        f'Please give me a final answer. '
    )

    message = client.beta.threads.messages.create(
        thread_id= thread.id,
        role= 'user',
        content= message_content,
        file_ids=['file-cQFQQ0Cr1YWZb613vhShyEuO'], 
    )
    run = client.beta.threads.runs.create(
        assistant_id= assistant.id,
        thread_id= thread.id,
    )

    with st.spinner('Analysis by ArgoX.ai...'):
        wait_on_run(client=client, run=run, thread=thread)

    messages = client.beta.threads.messages.list(
        thread_id= thread.id,
        # order='asc'
    )

    
    with st.sidebar:

        # st.write(stats)
        try:
            st.write(messages.data[0].content[0].text.value)
        except Exception as e:
            st.error(f"Error occurred while displaying message: {e}")

def analyse_itr(companyID, itr, n, stats):
    # get profile
    profile = get_company_profile(companyID)
    # ixbrl_data = get_ixbrl_data_from_dynamodb(companyID)
    
    # st.write(ixbrl_data)
    # st.write(f'ixbrl: {ixbrl_data['Item']['ixbrlData']}')

    # Update agent
    instructions = (
    f'You are an expert as both, underwriter and financial analyst. '
    f'You will analyse the data provided of financial ratios for a small company in the UK. '
    f'You will compare Inventory Turn Ratio againt the min, max and median of ITR for a set of similar companies. '
    f'Your goal is to aid the underwriter to make a good decision in terms of W&I. '
    f'After comparing all the data print thoughts and recommendations of how this company ITR performs in terms of the set. '
    )

    # update the description and load assistnt object
    assistant = client.beta.assistants.update(
        assistant_id='asst_bshJqwnnjeNfhH4JbSo2BkAi',
        instructions=instructions
    )
    #create a thread
    thread = client.beta.threads.create()

    # create a message
    message_content = (
        f'I will give you financial data for a company. '
        f'Information about the company can be found in the file {profile}. Use this for overall context. '
        # f'Ixbrl data of the company is provided in the file  {ixbrl_data}. Make sure to read all this data to find relevant information. '
        f'Comparison Research Set (Comps) = {n} SME. '
        f'The Inventory Turns Ratio for the company is {itr}. '
        f'The statistinc for the {n} SME set for the ITR are: '
        f'stats: {stats}.'
        f'Do a comparative analysis. '
        f'Tell about how company compares to the stats in terms of ITR. '
        f'What are the implications from an underwriter perspective?'
        f'Be brief. '
        f'Please do not ask any questions back. '
        f'If you need to do further processing go ahead, no need to ask. '
        f'Please give me a final answer. '
    )

    message = client.beta.threads.messages.create(
        thread_id= thread.id,
        role= 'user',
        content= message_content,
        file_ids=['file-cQFQQ0Cr1YWZb613vhShyEuO'], 
    )
    run = client.beta.threads.runs.create(
        assistant_id= assistant.id,
        thread_id= thread.id,
    )

    with st.spinner('Analysis by ArgoX.ai...'):
        wait_on_run(client=client, run=run, thread=thread)

    messages = client.beta.threads.messages.list(
        thread_id= thread.id,
        # order='asc'
    )

    
    with st.sidebar:

        # st.write(stats)
        try:
            st.write(messages.data[0].content[0].text.value)
        except Exception as e:
            st.error(f"Error occurred while displaying message: {e}")

def analyse_data(companyID, n, dataframe):
    # get profile
    profile = get_company_profile(companyID)
    ixbrl_data = get_ixbrl_data_from_dynamodb(companyID)
    
    # st.write(ixbrl_data)
    # st.write(f'ixbrl: {ixbrl_data['Item']['ixbrlData']}')

    # Update agent
    instructions = (
        'You are an expert as both, underwriter and financial analyst. '
        'You will analyse the data provided of financial ratios for a small company in the UK. '
        'You will compare different finacial ratios against the min, max and median of the same ratios for a set of similar companies. '
        'Your goal is to aid the underwriter to make a good decision in terms of W&I. '
        'After comparing all the data print thoughts and recommendations of how this company performs in terms of the set. '
    )

    # update the description and load assistnt object
    assistant = client.beta.assistants.update(
        assistant_id='asst_OOq4DcZhMEOusD1HnlUfPIMD',
        instructions=instructions
    )
    #create a thread
    thread = client.beta.threads.create()

    # create a message
    message_content = (
        f'I will give you financial data for a company. '
        f'Information about the company can be found in the file {profile}. Use this for overall context. '
        f'Ixbrl data of the company is provided in the file  {ixbrl_data}. Make sure to read all this data to find relevant information. '
        f'Comparison Research Set (Comps) = {n} SME. '
        # f'The Inventory Turns Ratio for the company is {itr}. '
        f'All the finantial data to be analysed is contained in a dataframe: {dataframe}. '
        f'The dataframe contains rows with each company in the set. '
        f'The columns contain financial data, the ratios for each company. '
        f"The finantial ratios columns are: ['wc_ratio', 'quick_ratio', 'itr_ratio', 'wr_score', 'cash_ratio']. f`ind them in the dataframe. "
        f'For the ratios columns we must calculate the min, max and media of each set (do not consioder non numeric values). '
        f'Also, when finding min, max, median on each column, we must filter out outliers using quartiles. '
        f'Do a comparative analysis. '
        f'Tell about how company compares to the stats for all ratios. '
        f'What are the implications from an underwriter perspective?'
        f'Please do not ask any questions back. '
        f'If you need to do further processing go ahead, no need to ask. '
        f'Please give me a final answer. '
    )


    message = client.beta.threads.messages.create(
        thread_id= thread.id,
        role= 'user',
        content= message_content,
        # file_ids=['file-xlNVkVH1evbzzAkj9yCHrrtV'], 
    )
    run = client.beta.threads.runs.create(
        assistant_id= assistant.id,
        thread_id= thread.id,
    )

    with st.spinner('Assistant analysing...'):
        wait_on_run(client=client, run=run, thread=thread)

    messages = client.beta.threads.messages.list(
        thread_id= thread.id,
        # order='asc'
    )

    
    with st.sidebar:

        # st.write(stats)
        try:
            st.write(messages.data[0].content[0].text.value)
        except Exception as e:
            st.error(f"Error occurred while displaying message: {e}")
