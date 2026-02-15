import streamlit as st
import pandas as pd
from database import create_connection, create_table, create_user_table

st.set_page_config(page_title="Employee Management System", layout="wide")

st.set_page_config(page_title="Login Page", layout="wide")
# ---------- CUSTOM COLOR STYLE ----------
st.markdown("""
<style>
section[data-testid="stSidebar"] {
    background-color: #1e293b;
}
section[data-testid="stSidebar"] * {
    color: white !important;
}
section[data-testid="stSidebar"] .stButton > button {
    background-color: #3b82f6;
    color: white;
    font-weight: bold;
    border-radius: 8px;
    height: 50px;
    margin-bottom: 10px;
}
section[data-testid="stSidebar"] .stButton > button:hover {
    background-color: #2563eb;
}
</style>
""", unsafe_allow_html=True)

create_table()
create_user_table()

conn = create_connection()
c = conn.cursor()
st.markdown(
    "<h1 style='text-align: center;'>Employee Management System</h1>",
    unsafe_allow_html=True
)

# ---------- SESSION STATE ----------
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

if "role" not in st.session_state:
    st.session_state.role = None

if "page" not in st.session_state:
    st.session_state.page = "Dashboard"

# ---------- LOGIN ----------
if not st.session_state.authenticated:

    # Add vertical spacing
    st.markdown("<br>", unsafe_allow_html=True)

    # Create center column
    col1, col2, col3 = st.columns([1,2,1])

    with col2:
        st.subheader(" Login")

        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login", use_container_width=True):

            c.execute(
                "SELECT role FROM users WHERE username=? AND password=?",
                (username, password)
            )

            user = c.fetchone()

            if user:
                st.session_state.authenticated = True
                st.session_state.role = user[0]
                st.rerun()
            else:
                st.error("Invalid Credentials")

    st.stop()
# ---------- SIDEBAR ----------
st.sidebar.write(f"Logged in as: {st.session_state.role}")

if st.sidebar.button("🚪 Logout", use_container_width=True):
    st.session_state.authenticated = False
    st.session_state.role = None
    st.rerun()

st.sidebar.title("Management Panel")

if st.sidebar.button("📊 Dashboard", use_container_width=True):
    st.session_state.page = "Dashboard"

if st.session_state.role in ["Admin", "HR"]:
    if st.sidebar.button("➕ Add Employee", use_container_width=True):
        st.session_state.page = "Add"

    if st.sidebar.button("🛠 Manage", use_container_width=True):
        st.session_state.page = "Manage"

if st.sidebar.button("💬 Feedback", use_container_width=True):
    st.session_state.page = "Feedback"

menu = st.session_state.page
st.divider()

# ---------- DASHBOARD ----------
if menu == "Dashboard":

    df = pd.read_sql_query("SELECT * FROM employees", conn)

    st.subheader("Company Overview")

    if not df.empty:

        col1, col2, col3 = st.columns(3)

        col1.metric("Total Employees", len(df))
        col2.metric("Average Salary", f"{df['salary'].mean():,.2f}")
        col3.metric("Highest Salary", f"{df['salary'].max():,.2f}")

        st.divider()

        dept_filter = st.selectbox(
            "Filter by Department",
            ["All"] + list(df["department"].unique())
        )

        if dept_filter != "All":
            df = df[df["department"] == dept_filter]

        st.bar_chart(df.groupby("department")["salary"].mean())

    else:
        st.info("No data available.")

# ---------- ADD EMPLOYEE ----------
elif menu == "Add":

    if st.session_state.role not in ["Admin", "HR"]:
        st.error("Access Denied")
        st.stop()

    st.subheader("Add New Employee")

    with st.form("employee_form", clear_on_submit=True):

        name = st.text_input("Full Name")
        email = st.text_input("Email")
        phone = st.text_input("Phone")

        department = st.selectbox(
            "Department",
            ["HR", "IT", "Finance", "Marketing", "Operations"]
        )

        designation = st.text_input("Designation")
        salary = st.number_input("Salary", min_value=0.0)
        joining_date = st.date_input("Joining Date")

        submit = st.form_submit_button("✅ Submit Employee")

        if submit:
            if name and email:
                c.execute("""
                    INSERT INTO employees
                    (name, email, phone, department, designation, salary, joining_date)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                """, (name, email, phone, department, designation, salary, str(joining_date)))

                conn.commit()
                st.success("Employee Added Successfully")
            else:
                st.error("Name and Email required.")

# ---------- MANAGE ----------
elif menu == "Manage":

    if st.session_state.role not in ["Admin", "HR"]:
        st.error("Access Denied")
        st.stop()

    st.subheader("Manage Employees")

    df = pd.read_sql_query("SELECT * FROM employees", conn)

    if not df.empty:

        search = st.text_input("Search by Name")

        if search:
            df = df[df["name"].str.contains(search, case=False)]

        st.dataframe(df, use_container_width=True)

        st.divider()

        emp_id = st.selectbox("Select Employee ID", df["id"])
        selected_emp = df[df["id"] == emp_id].iloc[0]

        new_salary = st.number_input(
            "Update Salary",
            value=float(selected_emp["salary"])
        )

        col1, col2 = st.columns(2)

        if col1.button("🔄 Update Salary", use_container_width=True):
            c.execute("UPDATE employees SET salary=? WHERE id=?",
                      (new_salary, emp_id))
            conn.commit()
            st.success("Updated Successfully")
            st.rerun()

        if col2.button("❌ Delete Employee", use_container_width=True):
            c.execute("DELETE FROM employees WHERE id=?", (emp_id,))
            conn.commit()
            st.warning("Deleted Successfully")
            st.rerun()

    else:
        st.info("No employees found.")

# ---------- FEEDBACK ----------
elif menu == "Feedback":

    st.subheader("Send Feedback")

    user_name = st.text_input("Your Name")
    message = st.text_area("Your Feedback")

    if st.button("📨 Submit Feedback", use_container_width=True):
        if user_name and message:
            st.success("Thank you for your feedback!")
        else:
            st.error("Please fill all fields.")
