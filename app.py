import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime

# ==========================================
# PAGE CONFIGURATION
# ==========================================
st.set_page_config(
    page_title="Ranzo NHS Canteen Management System",
    page_icon="🏫",
    layout="wide",
    initial_sidebar_state="expanded"
)

# ==========================================
# LOCAL STORAGE / BACKUP MANAGEMENT
# ==========================================
DATA_FILE = "canteen_data.json"

def get_default_data():
    return {
        "members": [
            {"id": 1, "name": "ELUSFA, PHEBE", "group": 1, "contribution": 1000},
            {"id": 2, "name": "FELECIO, RIZZA", "group": 1, "contribution": 1000}
        ],
        "daily_sales": [
            {"date": "2026-09-01", "gross_sales": 2500, "salary": 300, "water": 50, "purchased": 1200, "others": 100, "net_sales": 850}
        ],
        "faculty_accounts": [
            {"name": "ACUESA, IVY JOY", "sep": 0, "oct": 0, "nov": 0, "dec": 0, "jan": 0, "feb": 0, "mar": 0, "apr": 0},
            {"name": "AGADIA, ROSANNA", "sep": 0, "oct": 0, "nov": 0, "dec": 0, "jan": 0, "feb": 0, "mar": 0, "apr": 0}
        ]
    }

def load_data():
    if not os.path.exists(DATA_FILE):
        with open(DATA_FILE, "w") as f:
            json.dump(get_default_data(), f, indent=4)
    with open(DATA_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(DATA_FILE, "w") as f:
        json.dump(data, f, indent=4)

if "db" not in st.session_state:
    st.session_state.db = load_data()

# ==========================================
# AUTHENTICATION & ACCESS CONTROL
# ==========================================
st.sidebar.title("🔐 Access Control")
user_role = st.sidebar.radio("Select Role:", ["Viewer (Read-Only)", "Admin / Manager"])

is_admin = False
if user_role == "Admin / Manager":
    admin_password = st.sidebar.text_input("Enter Admin PIN:", type="password")
    if admin_password == "1234": # Set your custom password here
        is_admin = True
        st.sidebar.success("Admin Authenticated!")
    else:
        st.sidebar.warning("Incorrect PIN. Running in Viewer Mode.")

# ==========================================
# NAVIGATION & HEADER
# ==========================================
st.title("🏫 Ranzo NHS Canteen Management & Accounting System")
st.caption("Real-time collaborative ledger, startup funds, daily sales, and dividends portal.")

menu = st.sidebar.selectbox(
    "Navigation Menu",
    [
        "📊 Dashboard Summary",
        "💵 Start-up Funds & Members",
        "📝 Daily Sales & Expenses",
        "👥 Faculty & Staff Accounts",
        "📈 Dividend Calculator",
        "💾 Data Backup & Restore"
    ]
)

# ==========================================
# 1. DASHBOARD SUMMARY
# ==========================================
if menu == "📊 Dashboard Summary":
    st.header("Executive Financial Summary")
    
    sales_df = pd.DataFrame(st.session_state.db["daily_sales"])
    members_df = pd.DataFrame(st.session_state.db["members"])
    faculty_df = pd.DataFrame(st.session_state.db["faculty_accounts"])
    
    total_gross = sales_df["gross_sales"].sum() if not sales_df.empty else 0
    total_net = sales_df["net_sales"].sum() if not sales_df.empty else 0
    total_funds = members_df["contribution"].sum() if not members_df.empty else 0
    
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Total Capital Funds", f"₱{total_funds:,.2f}")
    col2.metric("Total Gross Sales", f"₱{total_gross:,.2f}")
    col3.metric("Total Net Profit", f"₱{total_net:,.2f}")
    col4.metric("Active Members", len(members_df))
    
    st.subheader("Daily Sales Performance")
    if not sales_df.empty:
        st.line_chart(sales_df.set_index("date")[["gross_sales", "net_sales"]])

# ==========================================
# 2. START-UP FUNDS & MEMBERS
# ==========================================
elif menu == "💵 Start-up Funds & Members":
    st.header("Canteen Start-Up Funds & Member Register")
    
    df_members = pd.DataFrame(st.session_state.db["members"])
    st.dataframe(df_members, use_container_width=True)
    
    if is_admin:
        st.subheader("➕ Add New Member Entry")
        with st.form("add_member_form"):
            m_id = len(df_members) + 1
            name = st.text_input("Member Full Name")
            group = st.number_input("Group Assignment", min_value=1, max_value=10, value=1)
            contrib = st.number_input("Contribution Amount (₱)", min_value=0.0, step=100.0)
            
            submitted = st.form_submit_button("Save Member")
            if submitted and name:
                st.session_state.db["members"].append({
                    "id": m_id, "name": name, "group": group, "contribution": contrib
                })
                save_data(st.session_state.db)
                st.success(f"Member '{name}' added successfully!")
                st.rerun()

# ==========================================
# 3. DAILY SALES & EXPENSES
# ==========================================
elif menu == "📝 Daily Sales & Expenses":
    st.header("Daily Sales Report & Expenses Ledger")
    
    df_sales = pd.DataFrame(st.session_state.db["daily_sales"])
    st.dataframe(df_sales, use_container_width=True)
    
    if is_admin:
        st.subheader("➕ Add Daily Record")
        with st.form("add_sales_form"):
            col1, col2 = st.columns(2)
            d_date = col1.date_input("Transaction Date", datetime.now()).strftime("%Y-%m-%d")
            gross = col1.number_input("Gross Sales (₱)", min_value=0.0, step=10.0)
            salary = col1.number_input("Salary Expense (₱)", min_value=0.0, step=10.0)
            
            water = col2.number_input("Water Subsidy (₱)", min_value=0.0, step=10.0)
            purchased = col2.number_input("Purchased Goods (₱)", min_value=0.0, step=10.0)
            others = col2.number_input("Other Expenses (₱)", min_value=0.0, step=10.0)
            
            submit_sales = st.form_submit_button("Record Sales Data")
            if submit_sales:
                total_exp = salary + water + purchased + others
                net = gross - total_exp
                st.session_state.db["daily_sales"].append({
                    "date": d_date, "gross_sales": gross, "salary": salary,
                    "water": water, "purchased": purchased, "others": others, "net_sales": net
                })
                save_data(st.session_state.db)
                st.success("Daily Record Added!")
                st.rerun()

# ==========================================
# 4. FACULTY & STAFF ACCOUNTS
# ==========================================
elif menu == "👥 Faculty & Staff Accounts":
    st.header("Ranzo NHS Faculty and Staff Credit Accounts")
    
    df_faculty = pd.DataFrame(st.session_state.db["faculty_accounts"])
    months = ["sep", "oct", "nov", "dec", "jan", "feb", "mar", "apr"]
    df_faculty["TOTAL BALANCE"] = df_faculty[months].sum(axis=1) if not df_faculty.empty else 0
    st.dataframe(df_faculty, use_container_width=True)

# ==========================================
# 5. DIVIDEND CALCULATOR
# ==========================================
elif menu == "📈 Dividend Calculator":
    st.header("Dividend Computation Portal")
    
    sales_df = pd.DataFrame(st.session_state.db["daily_sales"])
    members_df = pd.DataFrame(st.session_state.db["members"])
    
    total_net_profit = sales_df["net_sales"].sum() if not sales_df.empty else 0.0
    num_members = len(members_df) if len(members_df) > 0 else 1
    dividend_per_member = total_net_profit / num_members
    
    col1, col2 = st.columns(2)
    col1.metric("Total Annual Net Profit Available", f"₱{total_net_profit:,.2f}")
    col2.metric("Calculated Dividend per Official Member", f"₱{dividend_per_member:,.2f}")

# ==========================================
# 6. DATA BACKUP & RESTORE
# ==========================================
elif menu == "💾 Data Backup & Restore":
    st.header("Database Backup & System Recovery")
    
    st.subheader("📥 Export Local Database")
    json_string = json.dumps(st.session_state.db, indent=4)
    st.download_button(
        label="Download Full JSON Backup",
        file_name=f"canteen_backup_{datetime.now().strftime('%Y%m%d')}.json",
        mime="application/json",
        data=json_string
    )
    
    if is_admin:
        st.subheader("📤 Restore Database")
        uploaded_file = st.file_uploader("Upload JSON Backup File", type=["json"])
        if uploaded_file is not None:
            data = json.load(uploaded_file)
            st.session_state.db = data
            save_data(data)
            st.success("Database restored successfully!")
            st.rerun()
