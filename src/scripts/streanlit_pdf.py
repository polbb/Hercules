
import streamlit as st
from agents import *
import os

def streamlit_pdf(client, iterations, file_path, date_str, name_str):

    ########################################
    # Read the saved pdf and convert to txt
    ########################################
    with st.spinner("Processing document, please wait..."):
        print(f"pdf/{file_path}")
        all_text = convert_pdf_to_text(f"pdf/{file_path}")
        pdf_name = extract_pdf_name(pdf_filename=file_path)
        file_name_text = f"txt/{pdf_name}.txt"

        # Save the text file
        output_directory = "txt"

        if not os.path.exists(output_directory):
            os.makedirs(output_directory)

        save_text_file(file_name_text, all_text)
        # st.write(f"Text saved to {file_name_text}")

    ########################################
    # Upload text document
    ########################################
    with st.spinner("Analysing the document, please wait..."):
        file = upload_document(
            client, file_name_text
        )  # this is an openai file object
        file_id = file.id
        st.success("Document loaded")

    ########################################
    # DISPLAY COMPANY INFO
    ########################################

        st.subheader(f"Company Name: {name_str}")
        st.write(f"Date of Submission: {date_str}")

        st.divider()

    ########################################
    # CALCULATE INFO INFO
    ########################################
    with st.spinner("Calculating Cost of Sales Value..."):
        try:
            cogs = get_cost_of_sales(
                client, number_of_iterations=iterations, file_id=file_id
            )
            cogs_formatted = format_currency(cogs)
            st.write(f"Cost of Sales:         {cogs_formatted}")
        except Exception as e:
            st.write(f"Error occurred during Cost of Sales calculation: {e}")
            st.warning("Please start the process again.")
            # Stop further calculations
            raise ValueError("Invalid input for Cost of Sales")

    with st.spinner("Calculating Stocks Value..."):
        try:
            stocks = get_inventory(
                client, number_of_iterations=iterations, file_id=file_id
            )
            if stocks == 0:
                st.warning(
                    "Stocks value was zero and the calculations cannot be done."
                )
                # Stop further calculations
                # raise ValueError("Stocks value is zero")
            stocks_formatted = format_currency(stocks)
            st.write(f"Stocks:                {stocks_formatted}")
        except Exception as e:
            st.write(f"Error occurred during Stocks calculation: {e}")
            st.warning("Please start the process again.")
            # Stop further calculations
            # raise ValueError("Invalid input for Stocks")
        
    st.divider()

    # Initialize variables (this avoid error when cogs or stocks is None -> NameError: name 'itr_ratio' is not defined)
    itr_ratio = None
    wrscore = None
    gap_index = None

    if stocks and cogs:
        with st.spinner("Calculating Inventory Turns Ratio..."):
            try:
                itr_ratio = cogs / stocks
                itr_ratio = round(itr_ratio, 2)
                # st.write(f'Inventory Turns Ratio: {round(itr_ratio, 2)}')
            except Exception as e:
                st.write(f"Error occurred during division: {e}")

        with st.spinner("Calculating WR Score..."):
            try:
                wrscore = itr_ratio * itr_ratio
                wrscore = round(wrscore, 2)
                # st.write(f'WR Score:              {round(wrscore, 2)}')
            except Exception as e:
                st.write(f"Error occurred: {e}")

        with st.spinner("Calculating Gap Index..."):
            try:
                if wrscore == 0:
                    raise ValueError("WRS cannot be zero for Gap Index calculation")
                gap_index = (
                    itr_ratio / wrscore
                ) * 100  # Calculate gap index as a percentage
                gap_index = round(gap_index, 2)
                # st.write(f'Gap Index:             {round(gap_index, 2)}%')
            except Exception as e:
                st.write(f"Error occurred: {e}")

    if itr_ratio and wrscore and gap_index:
        col1, col2, col3 = st.columns(3)
        col1.metric("ITR", f"{itr_ratio}")
        col2.metric("WRS", f"{wrscore}")
        col3.metric("GI", f"{gap_index}%")

    else:
        st.warning("Please try again")
