# Hercules Project

## Overview
Hercules is a **Contextual Financial Reviewer** designed to extract, analyze, and manage financial data from various sources, such as PDFs, OCR-processed text, and online APIs. Leveraging advanced AI technologies like OpenAI's language models, AWS DynamoDB, and Streamlit, Hercules facilitates automated financial data retrieval, risk analysis, and interactive visualization.

## Features
- **Financial Data Extraction**: Retrieves key financial metrics and statements from complex documents using OCR and AI agents.
- **API Integration**: Connects to external APIs, such as Companies House, to fetch company profiles and filing histories.
- **DynamoDB Storage**: Manages extracted data in a cloud-based database for secure and efficient access.
- **Interactive UI**: Streamlit-powered interface for user interaction and data visualization.
- **AI Agents**: Intelligent agents for contextual financial data retrieval using OpenAI.

## Project Structure
- **`src/scripts`**: Core logic for financial data extraction, processing, and visualization.
  - **`main.py`**: 
    - Serves as the entry point for the application. 
    - Implements the Streamlit interface, allowing users to input a company number and view financial metrics.
    - Custom styling from `style.css` enhances the visual layout, ensuring a user-friendly experience.
    - Includes input fields, interactive buttons, and multi-column layouts for seamless user interactions.

  - **`document_retrieval.py`**: 
    - Handles API integration, specifically with Companies House, to fetch company profiles and filing histories.
    - Includes robust functions like `request_filling_history` for making HTTP requests and `get_company_name` for parsing and cleaning company-related data.
    - Ensures data compatibility with AWS DynamoDB by sanitizing inputs using `clean_name_for_dynamodb`.

  - **`utils_gpt.py`**: 
    - Provides threading and messaging utilities for managing AI-driven tasks.
    - Functions such as `wait_on_run` monitor and manage asynchronous tasks in the background.
    - Includes tools for creating threads (`create_a_thread`) and adding messages (`create_a_message`), enabling structured and interactive task management.

  - **`agents.py`**: 
    - Implements AI agents using OpenAI's API for targeted financial data retrieval.
    - Designed to process noisy OCR-derived text files and extract structured financial information, such as the cost of sales.
    - Contains clear and detailed prompts to guide the AI's behavior, ensuring high precision and relevance in responses.

  - **`database.py`**: 
    - Integrates AWS DynamoDB for secure storage and retrieval of financial data.
    - Includes functions like `get_company_profile` to fetch detailed company information and `get_ixbrl_data_from_dynamodb` for accessing structured financial documents.
    - Highlights cloud integration expertise by securely managing credentials and interacting with remote databases.

  - **`helper_functions.py`**: 
    - A collection of utility functions for various tasks, such as text processing, numeric value extraction, and API requests.
    - Functions like `extract_numeric_value` are tailored for parsing monetary values from noisy data sources.
    - Extensively uses libraries such as `pytesseract` and `pdf2image` for OCR and PDF processing.

  - **`benford.py`**:
    - Implements Benford's Law for statistical analysis of numeric data. 
    - Analyzes financial datasets to detect anomalies or irregularities, which may indicate potential fraud or data inconsistencies.
    - Provides visualizations to compare actual digit distributions against Benford's expected distribution, enabling quick anomaly detection.

## Key Components
### 1. **AI-Powered Data Extraction**
   - AI agents leverage OpenAI's models to extract contextual insights from financial documents.
   - Detailed instructions ensure that noisy and unstructured text is processed with high accuracy.

### 2. **Streamlit Interface**
   - The interface is intuitive and visually engaging, with clear input fields, multi-column layouts, and dynamic content.
   - Users can view tabular data, charts, and key financial metrics, all rendered in real-time.
   - Interactive plots are generated using the **Plotly** library, offering advanced features like zooming, filtering, and real-time updates. These plots include:
     - Filing history trends over time.
     - Distributions of financial metrics such as revenue, expenses, and profits.
     - Comparative visualizations of actual and expected data distributions based on Benford's Law.

### 3. **OCR and PDF Processing**
   - Converts scanned PDFs into machine-readable text using `pytesseract` and `pdf2image`.
   - Ensures accurate extraction of tabular and numeric data from visually complex documents.

### 4. **API and Database Integration**
   - Fetches real-time data from APIs like Companies House for up-to-date financial and regulatory information.
   - Stores and retrieves data efficiently using AWS DynamoDB, facilitating scalability and secure access.



