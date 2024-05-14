from database import get_ixbrl_data_from_dynamodb

import matplotlib.pyplot as plt

import streamlit as st

import plotly.graph_objects as go
import streamlit as st

def benford(company_number):
        
    # Benford's Law application with frequencies in percentage
    ixbrl_data = get_ixbrl_data_from_dynamodb(company_number)
    first_digit_frequencies = {str(digit): 0 for digit in range(1, 10)}  # Initialize frequency dict for digits 1-9
    total_values = 0  # Initialize total values count for percentage calculation
    for key, value_list in ixbrl_data.items():
        for value in value_list:
            try:
                number = float(value.replace(',', ''))
                if number == 0:  # Discard values that are only zero
                    continue
                first_digit = str(number)[0]  # Extract the first digit
                if first_digit in first_digit_frequencies:
                    first_digit_frequencies[first_digit] += 1  # Increment frequency of the first digit
                    total_values += 1  # Increment total values count
            except ValueError:
                continue
    
    # Convert frequencies to percentages
    for digit, frequency in first_digit_frequencies.items():
        if total_values > 0:  # Prevent division by zero
            first_digit_frequencies[digit] = (frequency / total_values) * 100

    # Plotting the frequencies against Benford's Law expected distribution using Plotly for Streamlit
    benford_distribution = [30.1, 17.6, 12.5, 9.7, 7.9, 6.7, 5.8, 5.1, 4.6]  # Expected percentages
    fig = go.Figure()
    fig.add_trace(go.Bar(x=list(first_digit_frequencies.keys()), y=list(first_digit_frequencies.values()), name='Observed Frequencies'))
    fig.add_trace(go.Scatter(x=list(first_digit_frequencies.keys()), y=benford_distribution, mode='lines+markers', name='BLD Expected'))
    fig.update_layout(title='BLD Method Review', xaxis_title='Modulus', yaxis_title='Frequency (%)', legend_title='Legend')
    fig.update_xaxes(type='category')  # Show all numbers on x-axis
    st.plotly_chart(fig)
    
    return first_digit_frequencies
