import streamlit as st
import pandas as pd
from datetime import datetime
import plotly.express as px


# Load Excel data for customers and marketers
customers_file = 'customers.xlsx'
marketers_file = 'marketers.xlsx'

# Function to load data
@st.cache_data
def load_data(file):
    return pd.read_excel(file)

# Load the dataframes
customers_df = load_data(customers_file)
marketers_df = load_data(marketers_file)

# ------------------- Authentication Section -------------------
st.title("Team Management System")

# Simple login system
if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False

def login(username, password):
    marketer_info = marketers_df[marketers_df['Name'] == username]
    if not marketer_info.empty and marketer_info['Password'].values[0] == password:
        st.session_state['logged_in'] = True
        st.session_state['current_marketer'] = username
    else:
        st.error("Invalid login credentials!")

# Login Form
if not st.session_state['logged_in']:
    st.subheader("Login as Marketer")
    with st.form("login_form"):
        username = st.text_input("Marketer Username")
        password = st.text_input("Password", type="password")
        login_submit = st.form_submit_button("Login")
        if login_submit:
            login(username, password)
else:
    st.success(f"Logged in as {st.session_state['current_marketer']}")
    
    # ------------------- Marketers Section -------------------
    st.subheader("Marketers Data")

    # Display the Marketers Data
    st.write("Below is the list of marketers:")
    st.dataframe(marketers_df)

    # ------------------- Add a Button to Download Marketers Data -------------------
    st.subheader("Download Marketers Data")
    
    @st.cache_data
    def convert_marketers_df(df):
        return df.to_excel(index=False)

    marketers_excel_data = convert_marketers_df(marketers_df)
    st.download_button(
        label="Download Marketers Data as Excel",
        data=marketers_excel_data,
        file_name='marketers_data.xlsx',
        mime='application/vnd.ms-excel'
    )

    # ------------------- Customers Section -------------------
    st.subheader(f"Customers Managed by {st.session_state['current_marketer']}")

    # Filter customers by the logged-in marketer
    filtered_customers = customers_df[customers_df['Marketer'] == st.session_state['current_marketer']]

    # Display filtered customers
    st.write(f"Customers assigned to marketer: **{st.session_state['current_marketer']}**")
    st.dataframe(filtered_customers)

    # ------------------- Add New Customer with Sales Info -------------------
    st.subheader("Add a New Customer")
    with st.form("add_customer_form"):
        company_name = st.text_input("Company Name")
        next_meeting = st.date_input("Next Meeting Date")
        rating = st.slider("Meeting Rating", 1, 5, 3)
        product_sold = st.selectbox("Product Sold", ["Yes", "No"])
        product_name = st.text_input("Product Name (if sold)")
        product_quantity = st.number_input("Product Quantity Sold (if sold)", min_value=0, step=1)
        submit = st.form_submit_button("Add Customer")

        if submit:
            # Add the new customer to the dataframe
            new_customer = {
                'Company Name': company_name,
                'Next Meeting': next_meeting.strftime('%Y-%m-%d'),
                'Rating': rating,
                'Product Sold': product_sold,
                'Product Name': product_name if product_sold == "Yes" else "",
                'Product Quantity': product_quantity if product_sold == "Yes" else 0,
                'Marketer': st.session_state['current_marketer']
            }
            customers_df = customers_df.append(new_customer, ignore_index=True)

            # Save the updated dataframe to Excel
            customers_df.to_excel(customers_file, index=False)

            st.success(f"Customer {company_name} added successfully!")
            st.dataframe(filtered_customers)

    # ------------------- Download Customers Data -------------------
    st.subheader("Download Customer Data")
    
    @st.cache_data
    def convert_customers_df(df):
        return df.to_excel(index=False)

    customers_excel_data = convert_customers_df(customers_df)
    st.download_button(
        label="Download Customer Data as Excel",
        data=customers_excel_data,
        file_name='updated_customers.xlsx',
        mime='application/vnd.ms-excel'
    )

    # ------------------- Marketer Performance Dashboard -------------------
    st.subheader("Marketer Performance Dashboard")

    # Group data by marketer to calculate performance
    performance_data = customers_df.groupby('Marketer').agg(
        total_customers=('Company Name', 'count'),
        total_sales=('Product Quantity', 'sum'),
        average_rating=('Rating', 'mean')
    ).reset_index()

    # Display performance data
    st.write("Performance overview for all marketers:")
    st.dataframe(performance_data)

    # Visualize performance with charts
    st.write("Customer Count and Sales per Marketer")
    fig = px.bar(performance_data, x='Marketer', y=['total_customers', 'total_sales'],
                 barmode='group', labels={'value': 'Performance Metrics'})
    st.plotly_chart(fig)

    st.write("Average Customer Rating per Marketer")
    rating_fig = px.bar(performance_data, x='Marketer', y='average_rating',
                        labels={'average_rating': 'Average Rating'})
    st.plotly_chart(rating_fig)
