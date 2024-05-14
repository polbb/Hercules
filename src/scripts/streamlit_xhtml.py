import plotly.express as px

from agents import *
from benford import *
from database import *
from document_retrieval import get_company_name
from helper_functions import make_dataframe
from sentiment import sentiment_analysis


def streamlit_xhtml(company_number):
    # DISPLAY COMPANY INFO
    name_str = get_company_name(company_number)  # Todo retrieve from DB instead

    with st.sidebar:
        st.title('Analysis by ArgoX.ai')
        st.divider()

    st.subheader(f"Target Company: {name_str}")
    st.divider()

    # GET FINANCIAL INDICATORS
    left = 25
    right = 25
    """with st.spinner("Calculating Cost of Sales Value..."):
        try:
            file_path = f"xhtml/{file_path}"
            cogs = get_cogs_xhtml(
                client, number_of_iterations=iterations, file_path=file_path
            )

            if not isinstance(cogs, int):
                st.warning(
                    "Error retrieving the value: Please start the process again. COGS"
                )
                st.stop()

            cogs_formatted = format_currency(cogs)
            st.text(f"{'Cost of Sales:':<{left}}          {cogs_formatted:>{right}}")
            # st.text(f"Cost of Sales:          {cogs_formatted}")
            

        except Exception as e:
            st.write(f"Error occurred during Cost of Sales calculation: {e}")
            st.warning(
                "Error retrieving the value: Please start the process again. COGS2"
            )
            st.stop()
"""
    """with st.spinner("Calculating Stocks Value..."):
        try:
            stocks = get_inventory_xhtml(
                client, number_of_iterations=iterations, file_path=file_path
            )
            if not isinstance(stocks, int):
                st.warning("Please start the process again. STOCKS")
                st.stop()
            if stocks == 0:
                st.warning("Stocks value was zero and the calculations cannot be done.")
                st.stop()

            stocks_formatted = format_currency(stocks)
            # st.text(f"Stocks:                 {stocks_formatted}")
            st.text(f"{'Stocks:':<{left}}          {stocks_formatted:>{right}}")

        except Exception as e:
            st.write(f"Error occurred during Stocks calculation: {e}")
            st.warning("Please start the process again. STOCKS2")
            st.stop()"""

    table = "company_ratios"

    with st.spinner('Retrieving Cost od Sales...'):
        cogs = get_attribute_value(company_number, table, "cost_of_sales")
        st.text(f"{'Cost of Sales:':<{left}} {format_currency(cogs):>{right}}")

    with st.spinner('Retrieving Stocks...'):
        stocks = get_attribute_value(company_number, table, "stocks")
        st.text(f"{'Stocks:':<{left}} {format_currency(stocks):>{right}}")

    with st.spinner('Retrieving Turnover...'):
        turnover = get_attribute_value(company_number, table, "turnover")
        st.text(f"{'Turnover:':<{left}} {format_currency(turnover):>{right}}")

    with st.spinner('Retrieving Current Assets...'):
        current_assets = get_attribute_value(company_number, table, "current_assets")
        st.text(f"{'Current Assets:':<{left}} {format_currency(current_assets):>{right}}")

    # fixed assets is a list where second to last might be the proper value
    with st.spinner('Retrieving Fixed Assets...'):
        fixed_assets = get_attribute_value(company_number, table, "fixed_assets")
        st.text(f"{'Fixed Assets:':<{left}} {format_currency(fixed_assets):>{right}}")

    with st.spinner('Retrieving Total Assets...'):
        total_assets = get_attribute_value(company_number, table, "total_assets")
        st.text(f"{'Total Assets:':<{left}} {format_currency(total_assets):>{right}}")

    with st.spinner('Retrieving Inventory Prepaid Expenses...'):
        inventory_prepaid_expenses = get_attribute_value(company_number, table, "inventory_prepaid_expenses")
        st.text(f"{'Stock Pre-paid Expenses:':<{left}} {format_currency(inventory_prepaid_expenses):>{right}}")

    with st.spinner('Retrieving Creditors...'):
        creditors = get_attribute_value(company_number, table, "creditors")
        st.text(f"{'Creditors:':<{left}} {format_currency(creditors):>{right}}")

    with st.spinner('Retrieving Cash and Cash Equivalents...'):
        cash_and_cash_equivalents = get_attribute_value(company_number, table, "cash_and_cash_equivalents")
        st.text(f"{'Cash & Equivalents:':<{left}} {format_currency(cash_and_cash_equivalents):>{right}}")

    st.divider()

    ########################################
    # GET SIC
    ########################################
    sic = get_sic_code(company_number)

    placeholder = st.empty()
    with placeholder.container():
        placeholder.text(f"SIC code is {sic}, comparative GICS is: TBC")

    ########################################
    # GET SME COMPARISON SET
    ########################################
    with st.spinner('Creating Comparison Research set....', ):

        # time.sleep(2)
        # get the set starting with total assests of company
        try:
            if total_assets is not None:
                result = get_sme_group(int(total_assets))
                # result = get_sme_group(total_assets)
                # st.write(f'total assets not none: {total_assets}')
            else:
                st.warning("Total assets value is None. Unable to retrieve SME group.")
                result = None
                return result
        except Exception as e:
            st.warning(f"An error occurred while retrieving SME group: {e}")
            result = None
            return result

        if result is not None:
            n = len(result)

            dataframe = make_dataframe(result)

            dataframe.drop(columns=['gics', 'gics_timestamp', 'non_micro'],
                           inplace=True)  # REMOVE THIS CODE AFTER CTEATING GIOCS TABLE!!!

            dataframe = calculate_financial_ratios(dataframe)  # add ratios columns

            statistics = calculate_statistics(dataframe)  # Returns a dictionary

            st.markdown(
                f"<span style='color: green; font-size: 30px;'>Comparison Research Set (Comps) = {n} SME Companies</span>",
                unsafe_allow_html=True)


    ########################################
    # New Container BOS
    ########################################
    st.divider()

    with st.container(border=True):
        # st.header('Business Operations Score')
        st.markdown(
                f"<span style='color: white; font-size: 60px;'>Business Operations Score</span>",
                unsafe_allow_html=True)
        

    ########################################
    # TABS
    ########################################

    st.divider()

    tab1, tab2, tab3, tab4 = st.tabs(["Analysis", "Data", "Plots", "Veracity"])

    with tab4:
        # Benford's Law application with frequencies in percentage
        first_digit_frequencies = benford(company_number)
        first_digit_df = pd.DataFrame(list(first_digit_frequencies.items()), columns=['Modulus', 'Frequency (%)'])

        # Display the frequencies in a dataframe with the index hidden
        st.dataframe(first_digit_df, hide_index=True)

    with tab1:

        if 'dataframe' in locals() or 'dataframe' in globals():
            with tab2:
                st.write(dataframe)
                st.write(result)

            with tab3:
                required_columns = ['wc_ratio', 'quick_ratio', 'itr_ratio', 'wr_score', 'cash_ratio']
                numeric_df = dataframe[required_columns].apply(pd.to_numeric, errors='coerce')

                for column in required_columns:
                    q1 = numeric_df[column].quantile(0.25)
                    q3 = numeric_df[column].quantile(0.75)
                    iqr = q3 - q1
                    lower_fence = q1 - 1.5 * iqr
                    upper_fence = q3 + 1.5 * iqr

                    filtered_df = numeric_df[column][
                        (numeric_df[column] >= lower_fence) & (numeric_df[column] <= upper_fence)]

                    fig = px.box(filtered_df, y=column, width=300)  # Adjusted width to make plots narrower
                    st.plotly_chart(fig)

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
                    wrscore = (current_assets / total_assets) / (creditors / total_assets)
                    wrscore = round(wrscore, 2)
                    # st.write(f'WR Score:              {round(wrscore, 2)}')
                except Exception as e:
                    st.write(f"Error occurred: {e}")

                # with st.spinner("Calculating Gap Index..."):
                pass
                # try:
                #     if wrscore == 0:
                #         raise ValueError("WRS cannot be zero for Gap Index calculation")
                #     gap_index = (
                #         itr_ratio / wrscore
                #     ) * 100  # Calculate gap index as a percentage
                #     gap_index = round(gap_index, 2)
                #     # st.write(f'Gap Index:             {round(gap_index, 2)}%')
                # except Exception as e:
                #     st.write(f"Error occurred: {e}")

        # Working capital ratio = current assets / current liabilities
        if total_assets and creditors:
            with st.spinner("Calculating Working Capital Ratio..."):
                try:
                    wc_ratio = total_assets / creditors
                    wc_ratio = round(wc_ratio, 2)

                except Exception as e:
                    st.write(f"Error occurred during division: {e}")

        # quick ratio = (current assets - inventory prepaid expenses) / current liabilities
        if total_assets and creditors and inventory_prepaid_expenses:
            with st.spinner("Calculating Quick Ratio..."):
                try:
                    quick_ratio = (total_assets - inventory_prepaid_expenses) / creditors
                    quick_ratio = round(quick_ratio, 2)

                except Exception as e:
                    st.write(f"Error occurred during division: {e}")

        # Cash Ratio = Cash and Cash Equivalents / Current Liabilities
        if cash_and_cash_equivalents and creditors:
            with st.spinner("Calculating Cash Ratio..."):
                try:
                    cash_ratio = cash_and_cash_equivalents / creditors
                    cash_ratio = round(cash_ratio, 2)

                except Exception as e:
                    st.write(f"Error occurred during division: {e}")

        ########################################
        # display ratios
        ########################################

        # ITR
        if 'itr_ratio' in locals() or 'itr_ratio' in globals():
            with st.container(border=True):
                st.header('Inventory Turns Ratio')
                display_metrics(name_str, itr_ratio, statistics['itr_ratio'])
        else:
            st.warning("Inventory Turns Ratio is not available or is null.")

        # WORKING CAPITAL
        if 'wc_ratio' in locals() or 'wc_ratio' in globals():
            with st.container(border=True):
                st.header('Working Capital Ratio')
                display_metrics(name_str, wc_ratio, statistics['wc_ratio'])
        else:
            st.warning("Working Capital Ratio is not available or is null.")

        # QUICK RATIO
        if 'quick_ratio' in locals() or 'quick_ratio' in globals():
            with st.container(border=True):
                st.header('Quick Ratio')
                display_metrics(name_str, quick_ratio, statistics['quick_ratio'])
        else:
            st.warning("Quick Ratio is not available or is null.")

        # Cash Ratio
        if 'cash_ratio' in locals() or 'cash_ratio' in globals():
            with st.container(border=True):
                st.header('Cash Ratio')
                display_metrics(name_str, cash_ratio, statistics['cash_ratio'])
        else:
            st.warning("Cash Ratio is not available or is null.")

        # WR SCORE
        if 'wrscore' in locals() or 'wrscore' in globals():
            with st.container(border=True):
                st.header('WR Score')
                display_metrics(name_str, wrscore, statistics['wr_score'])
        else:
            st.warning("WR Score is not available or is null.")

        # GAP INDEX
        # with st.container(border=True):
        # st.header('Gap Index')
        # if itr_ratio and wrscore and gap_index:
        #     display_metrics(name_str, gap_index, statistics['gap_index'])
        # else:
        #     st.warning("Error: Please start the process again")

        # st.text('Code Frozen 10:33 2024.02.13')

    with placeholder.container():
        with st.spinner('Coverting to GICS...'):
            gics = get_gics_code(company_number)

        placeholder.text(f"SIC code is {sic}, comparative GICS is: {gics}")

    with st.sidebar:
        st.title('Sentiment')
        # text = sentiment_analysis()
        # st.write(text)

        # generate()

        st.divider()

        st.title('Comparative Analysis')

        # analyse_metrics(
        #     companyID=company_number,
        #     metrics=dataframe.loc[company_number],
        #     n=n,
        #     stats=statistics
        #     # stats=statistics['itr_ratio']
        # )

        # save file to db

    # st.text('Code Frozen 09:50 2024.02.16')
