import streamlit as st
import sqlite3
import re
from datetime import datetime
import os
import smtplib as s
import random
from num_dict import num, dep_code, doc_code
import time

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

# Create or connect to SQLite database
conn = sqlite3.connect("users.db")
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

# cursor.execute("""
#                CREATE TABLE IF NOT EXISTS spreadsheet (
#                    ID INTEGER PRIMARY KEY AUTOINCREMENT,
#                    Date TEXT NOT NULL,
#                    Email TEXT NOT NULL,
#                    Department TEXT NOT NULL,
#                    Doc_code TEXT NOT NULL,
#                    Number TEXT NOT NULL
#                )
#                """)

# Initialize session state variables
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "page" not in st.session_state:
    st.session_state.page = "login"  # Default page is login
    
if "title" not in st.session_state:
    st.session_state.title = ""
         
    

# function to show the login form
def show_login_page():
    col1,col2,col3,col4,col5 = st.columns(5)
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
                st.rerun()  # Immediately rerun the app to reflect changes
            else:
                st.warning("Incorrect email or password")
        else:
            st.warning("Please enter both email and password")

# Helper function to show the signup form
def validate_email(email):
    pattern = r'^[a-zA-Z0-9._%+-]+@(nuclearpowergh\.com|vra\.com)$'
    
    if re.match(pattern, email):
        return True
    return False

def validate_password(password):
    if len(password) >= 6:
        return True
    return False

def show_signup_page():
    st.subheader(":green[Signup]")
    st.session_state.email = st.text_input(label="Email", placeholder="Enter your email")
    password = st.text_input(label="Password", type="password", placeholder="Enter Password")
    password2 = st.text_input(label="Confirm Password", type="password", placeholder="Confirm password")
    
    if st.form_submit_button(label="Signup"):
        if st.session_state.email and password:
            if not cursor.execute("SELECT * FROM authorize WHERE Email=?", (st.session_state.email,)).fetchone():
                if validate_email(st.session_state.email):
                    if validate_password(password):
                        if password2 == password:
                            cursor.execute("INSERT INTO authorize (Email, Password) VALUES (?, ?)", (st.session_state.email, password))
                            conn.commit()
                            st.success("Signup successful! You can now login.")
                        else:
                            st.warning("Passwords do not match")
                    else:
                        st.warning("Password must be at least 6 characters long")
                else:
                    st.warning("Invalid email entry")
            else:
                st.warning("A user with the same email address already exists. Please Login or use the forgot password button")           
        else:
            st.warning("Please enter both email and password")


def clear_database():
    conn = sqlite3.connect("users.db")
    cursor = conn.cursor()
    cursor.execute("""
                   DELETE FROM spreadsheet
                   """)
    conn.commit()
    conn.close()
    
    st.session_state.success_message = True
    
    st.success("All records have been deleted")
    
# def view_database():
#     conn = sqlite3.connect("users.db")
#     cursor = conn.cursor()
#     query = cursor.execute("""
#                    SELECT * FROM spreadsheet
#                    """)
    
#     conn.commit()
#     df = pd.read_sql_query(query,conn)
#     conn.close()
    
#     return st.write(df)

# Helper function to show the document request page
def show_request_page():
    st.write("# :blue[Document Number Requisition System]")
    st.write("## Welcome! You can now request a document number.")
    
    if st.session_state.email == "n.angu@vra.com":
        st.sidebar.button("clear database", on_click=clear_database)
    # else:
    #     st.sidebar.button("view database", on_click=view_database)
        
    
    if "sub_list" not in st.session_state:
        st.session_state.sub_list = []
    
    if "title" not in st.session_state:
        st.session_state.title = ""
        
    
    # Document number request form
    department = st.selectbox("Select Department", ["Executive Office", "Project Management", "Engineering Development", 
                                                    "Public Affairs"])
    st.session_state.title = st.text_area("Document Tile", value= st.session_state.title, height=4).title()
    document_code = st.selectbox("Select Document Type", ["Report", "Manual", "Letter", "Procedure", "Process", "Presentation"])
    infra_issue = [key for key in num.keys()]
    infrastructure_issue = st.selectbox("Select Infrastructure Issue", infra_issue)
    subject_index = st.selectbox("Select Subject Index", [indexes for indexes in num[infrastructure_issue]])
    # sub_division = st.selectbox("Select Sub-division", st.session_state.sub_list, placeholder="Choose an option")
    seq_num = "001"
    sub_area = str(num[infrastructure_issue][subject_index])
    code = doc_code[document_code]
    
    if infrastructure_issue == "Stakeholder Involvement" and subject_index == "International":
        st.session_state.sub_list = [indexes for indexes in num[infrastructure_issue][subject_index]]
        sub_division = st.selectbox("Select Sub-division", st.session_state.sub_list, placeholder="Choose an option")
        sub_area = str(num[infrastructure_issue][subject_index][sub_division])

        # if sub_division:  # Only access sub_area if sub_division has a valid selection
        #     sub_area = str(num[infrastructure_issue][subject_index][sub_division])
        # else:
        #     st.warning("Please select a valid sub-division.")
            
    elif infrastructure_issue == "Stakeholder Involvement" and subject_index == "Local":
        st.session_state.sub_list = [indexes for indexes in num[infrastructure_issue][subject_index]]
        sub_division = st.selectbox("Select Sub-division", st.session_state.sub_list, placeholder="Choose an option")
        sub_area = str(num[infrastructure_issue][subject_index][sub_division])
        # if sub_division:  # Only access sub_area if sub_division has a valid selection
        #     sub_area = str(num[infrastructure_issue][subject_index][sub_division])
        # else:
        #     st.warning("Please select a valid sub-division.")
        
    else:
        st.session_state.sub_list = []
        sub_area = str(num[infrastructure_issue][subject_index])
      
       
    col1, col2, col3,col4,col5 = st.columns(5)
    
    Request = col1.button("Request Number")
    # clear = col2.button("Clear")
    logout = col5.button("Logout")
    if Request:
        title_check = cursor.execute("SELECT * FROM spreadsheet WHERE Title LIKE ?", (st.session_state.title.title(),)).fetchone()
        dept_check = cursor.execute("SELECT * FROM spreadsheet WHERE Department=?", (department,)).fetchone()
        pattern = dep_code[department] + "-" + sub_area + "-" + code
        if not st.session_state.title:
            st.warning("Please type the document title in the field provided")
        elif title_check and dept_check:
            st.warning("The Document Already Exists in the Database")
        else:
            seq_count = cursor.execute("SELECT COUNT(*) FROM spreadsheet WHERE Doc_Num LIKE ?", (pattern + '%',)).fetchone()[0]
            if seq_count > 0:
                seq_count = str(seq_count + 1)
                seq_num = "00" + seq_count
            date = datetime.now()
            document_num = dep_code[department] + "-" + sub_area + "-" + code + "-" + seq_num
            cursor.execute("INSERT INTO spreadsheet (Date, Requester,Title,Department, Doc_Type, Doc_Num) VALUES (?,?,?,?,?,?)", (date,st.session_state.email, st.session_state.title.title(),department,document_code,document_num))
            conn.commit()
            st.success(f"Document number generated is:  {document_num}", icon="✅")
    elif logout:
        st.session_state.page = "login"
        st.session_state.authenticated = False
        st.rerun()
    

# Helper function to show the forgot password page
def show_forgot_password_page():
    st.subheader(":green[Forgot Password]")
    email = st.text_input("Enter the email you registered with")
    
    if st.form_submit_button(label="Submit"):
        if validate_email(email):
            user = cursor.execute("SELECT * FROM authorize WHERE Email=?", (email,)).fetchone()
            if user:
                # Simulate sending a reset link (you'd replace this with actual email logic)
                #st.success(f"Password reset link has been sent to {email}.")
                st.session_state.page = "reset_password"
                st.session_state.reset_email = email
                #st.session_state.authenticated = False
                st.rerun()
            else:
                st.warning("Email not found in the system.")
        else:
            st.warning("Please enter a valid email.")

# Helper function to show the reset password page
def show_reset_password_page():
    st.subheader(":green[Reset Password]")
    new_password = st.text_input(label="New Password", type="password", placeholder="Enter new password")
    new_password2 = st.text_input(label="Confirm Password", type="password", placeholder="Confirm new password")
    
    if st.form_submit_button(label="Reset Password"):
        if validate_password(new_password):
            if new_password and new_password2:
                if new_password == new_password2:
                    # Update the password in the database
                    cursor.execute("UPDATE authorize SET Password=? WHERE Email=?", (new_password, st.session_state.reset_email))
                    conn.commit()
                    st.success("Password reset successful! You can now login.")
                    st.session_state.page = "login"
                    st.rerun()
                else:
                    st.warning("Passwords do not match.")
            else:
                st.warning("Please fill both password fields.")
        else:
            st.warning("Password is too short")

        
        

# Page switching logic
if st.session_state.page == "login" and not st.session_state.authenticated:
    with st.form(key="Login", clear_on_submit=False):
        show_login_page()

    if st.button(label="New User? Signup"):
        st.session_state.page = "signup"
        st.rerun()  # Trigger a rerun after changing the page
    
    if st.button(label="Forgot Password?", key="forgot_password"):
        st.session_state.page = "forgot_password"
        st.rerun()

elif st.session_state.page == "signup":
    with st.form(key="Signup", clear_on_submit=False):
        show_signup_page()

    if st.button(label="Already have an account? Login"):
        st.session_state.page = "login"
        st.rerun()  # Trigger a rerun after changing the page
    
    elif st.button(label="forgot password"):
        st.session_state.page = "forgot_password"
        st.rerun()

elif st.session_state.page == "forgot_password":
    with st.form(key="Forgot Password", clear_on_submit=False):
        show_forgot_password_page()
        
elif st.session_state.page == "reset_password":
    with st.form(key="reset password", clear_on_submit=False):
        show_reset_password_page()
    

elif st.session_state.authenticated:
    show_request_page()

# Commit and close the database connection
conn.commit()
conn.close()
