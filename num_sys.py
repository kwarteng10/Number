import streamlit as st
import sqlite3
import re
from datetime import datetime

# Set page title and config
st.set_page_config(
    page_title="Nuclear Power Ghana - Document Number Requisition System"
)

# CSS for custom styling
st.markdown(
    """
    <style>
    /* Change the background color of the app */
    body {
        background-color: #f5f5f5;
    }
    
    /* Style the selectbox and text input fields */
    .stTextInput, .stSelectbox {
        padding: 10px;
        margin-bottom: 20px;
        border: 1px solid #d4d4d4;
        border-radius: 5px;
    }
    
    /* Add padding and margin to buttons */
    .stButton > button {
        background-color: #4CAF50;
        color: white;
        padding: 10px 20px;
        border-radius: 5px;
    }

    /* Change subheader color */
    .stMarkdown h3 {
        color: #2A9D8F;
    }

    /* Style the title */
    h1 {
        color: #1D3557;
        font-family: 'Arial', sans-serif;
        font-size: 32px;
        padding-bottom: 10px;
    }
    </style>
    """,
    unsafe_allow_html=True)

# Create or connect to SQLite database using Streamlit connection
conn = st.connection("users_db", type="sql", ttl=0)  # Ensure you have the correct parameters for your use case
cursor = conn.cursor()

# Create table if it doesn't exist
cursor.execute(""" 
               CREATE TABLE IF NOT EXISTS authorize (
                   Email TEXT NOT NULL,
                   Password TEXT NOT NULL
               )
               """)

cursor.execute("""
               CREATE TABLE IF NOT EXISTS spreadsheet (
                   Date TEXT NOT NULL,
                   Requester TEXT NOT NULL,
                   Title TEXT NOT NULL,
                   Department TEXT NOT NULL,
                   Doc_Type TEXT NOT NULL,
                   Doc_Num TEXT NOT NULL
               )
               """)

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"  # Default page is login

# Function to show the login form
def show_login_page():
    col1, col2, col3, col4, col5 = st.columns(5)
    if "email" not in st.session_state:
        st.session_state.email = ""
    col1.subheader(":green[Login]")
    col5.image("npg.png")
    st.session_state.email = st.text_input(label="Email", placeholder="Please enter a valid email")
    password = st.text_input(label="Password", type="password")

    if st.form_submit_button(label="Login"):
        if st.session_state.email and password:
            user = cursor.execute("SELECT * FROM authorize WHERE Email=? AND Password=?", (st.session_state.email, password)).fetchone()
            if user:
                st.session_state.authenticated = True
                st.success("Login successful!")
                st.session_state.page = "request"
                st.rerun()
            else:
                st.warning("Incorrect email or password")
        else:
            st.warning("Please enter both email and password")

# Define other helper functions (show_signup_page, show_request_page, etc.) here...

# Page switching logic
if st.session_state.page == "login" and not st.session_state.authenticated:
    with st.form(key="Login", clear_on_submit=False):
        show_login_page()
    # Include buttons for signup and forgot password...

elif st.session_state.page == "signup":
    with st.form(key="Signup", clear_on_submit=False):
        show_signup_page()

elif st.session_state.page == "forgot_password":
    with st.form(key="Forgot Password", clear_on_submit=False):
        show_forgot_password_page()

elif st.session_state.page == "reset_password":
    with st.form(key="reset password", clear_on_submit=False):
        show_reset_password_page()

elif st.session_state.authenticated:
    show_request_page()

# Commit and close the database connection (this is managed automatically in st.connection)
# No need to close the connection explicitly
