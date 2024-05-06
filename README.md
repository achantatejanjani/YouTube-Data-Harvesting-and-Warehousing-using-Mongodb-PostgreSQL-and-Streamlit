YouTube Data Harvesting and Warehousing

This project is a Streamlit application that allows users to harvest and analyze data from multiple YouTube channels. It also provides the capability to store the collected data in MongoDB or PostgreSQL databases. The README file aims to guide users through the setup, installation, usage, and contributors of the project.

Table of Contents
1. Overview
2. Setup and Installation
    Prerequisites
    Setting Up the Environment
    Installing Required Packages
3. Usage
4. Contributors

Overview
This project is a Streamlit application designed to facilitate the retrieval, storage, and analysis of data from YouTube channels. It integrates the Google API for data retrieval and supports storing the collected data in both MongoDB and PostgreSQL databases. The application provides an intuitive interface for users to interact with the data and perform various analyses.

Setup and Installation

Prerequisites:

Before setting up the project, ensure you have the following prerequisites installed:

Python (latest version)
VS Code (or any preferred code editor)
MongoDB (for data storage)
PostgreSQL (for data warehousing)

Setting Up the Environment:
1. Folder Setup: Create a new folder on your desktop and import it into VS Code.

2. Virtual Environment: Use VS Code's terminal to create a virtual environment:
                     Press Ctrl+Shift+P.
                     Select "Create Python Environment".
                     Choose Vnev to create a virtual environment in the workplace.
   
Installing Required Packages
1. Google API Python Client: Install using pip: pip install google-api-python-client
2. MongoDB: Install using pip: pip install pymongo
3. PostgreSQL: Install using pip: pip install psycopg2
4. Streamlit: Install using pip: pip install streamlit
5. Pandas: Install using pip: pip install pandas
   
Usage
1. Google Developer Console:
      Create a project and select the YouTube API.
      Generate an API key for authentication.
2. Running the Application:
      Execute the application using Streamlit: streamlit run youtube.py
3. Data Collection:
      Input YouTube channel IDs to retrieve relevant data.
      Store collected data in MongoDB or PostgreSQL databases.
4. Data Analysis:
      Analyze and visualize data using the Streamlit interface.
      Perform various queries and analyses on the stored data.

Contributors
Tejanjani Achanta
