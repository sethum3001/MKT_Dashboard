import streamlit as st
import gspread
import pandas as pd
import matplotlib.pyplot as plt
from google.oauth2.service_account import Credentials

# Load Google Sheets Data
def get_google_sheet(sheet_url, sheet_name):
    creds = Credentials.from_service_account_file("mkt-dashboard-450501-39522c4d0871.json", scopes=["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"])
    client = gspread.authorize(creds)
    sheet = client.open_by_url(sheet_url).worksheet(sheet_name)
    
    # Fetch all data from the sheet
    data = sheet.get_all_values()
    
    # Manually set headers (third row in your sheet)
    headers = data[2]  # Third row contains headers
    rows = data[3:]    # Data starts from the fourth row
    
    # Create a DataFrame
    df = pd.DataFrame(rows, columns=headers)
    return df

# Set up Streamlit app
st.title("MKT Team Performance Dashboard")

# Google Sheet URL and Sheet Name
sheet_url = "https://docs.google.com/spreadsheets/d/18LjsmUIgR22yTdVF0Lt6RoXmTjcTiJF1DSw4EJv1iZI/edit?gid=2134091092#gid=2134091092"
sheet_name = "Performance"

# Load and display data
df = get_google_sheet(sheet_url, sheet_name)

# Check if the DataFrame is empty
if df.empty:
    st.error("The Performance sheet is empty or not formatted correctly.")
else:
    # Convert necessary columns
    df["Campaign progress"] = df["Campaign progress"].astype(str)
    df["Month"] = df["Month"].astype(str)

    # Get unique values for dropdowns
    done_by_list = df["Done by"].dropna().unique().tolist()
    month_list = df["Month"].dropna().unique().tolist()
    month_list = ["All"] + month_list  # Add "All" option to the month dropdown

    # Dropdowns for selection
    selected_person = st.selectbox("Select a person", done_by_list)
    selected_month = st.selectbox("Select a month", month_list)

    # Filter data for selected person and month
    if selected_month == "All":
        filtered_df = df[df["Done by"] == selected_person]
    else:
        filtered_df = df[(df["Done by"] == selected_person) & (df["Month"] == selected_month)]

    # Task Completion Rate (Pie Chart)
    if not filtered_df.empty:
        task_status = filtered_df["Campaign progress"].value_counts()
        fig1, ax1 = plt.subplots()
        wedges, texts, autotexts = ax1.pie(
            task_status, 
            labels=task_status.index, 
            autopct=lambda p: f"{p:.1f}%\n({int(p * sum(task_status) / 100)})", 
            startangle=90, 
            colors=["#4CAF50", "#FFC107"]
        )
        ax1.axis("equal")  # Equal aspect ratio ensures pie chart is circular
        st.write("### Task Completion Rate")
        st.pyplot(fig1)
    else:
        st.write("No data available for the selected person and month.")

    # Bar Chart for Completed Work by Everyone for Selected Month
    st.write("### Completed Work by Everyone for Selected Month")
    if not df.empty:
        completed_df = df[df["Campaign progress"] == "Completed"]
        if selected_month != "All":
            completed_df = completed_df[completed_df["Month"] == selected_month]
        
        bar_data = completed_df["Done by"].value_counts()
        
        fig2, ax2 = plt.subplots()
        bar_data.plot(kind="bar", ax=ax2, colormap="viridis")
        ax2.set_xlabel("Done by")
        ax2.set_ylabel("Number of Completed Tasks")
        plt.xticks(rotation=45)
        st.pyplot(fig2)
    else:
        st.write("No completed tasks found.")