import streamlit as st

# This must be the first Streamlit command
st.set_page_config(page_title="NSCH Data Tools", layout="wide")

# Now import the other scripts
import missingidnsch
import nsch_cleaner
import step2nsch
import nschunpivot

# Sidebar Navigation
st.sidebar.title("NSCH Data Processing Tools")
option = st.sidebar.radio(
    "Select a tool:", 
    ["Missing ID NSCH", "NSCH Cleaner", "Step 2 NSCH", "NSCH Unpivot"]
)

# Display the selected app
if option == "Missing ID NSCH":
    missingidnsch.run()
elif option == "NSCH Cleaner":
    nsch_cleaner.run()
elif option == "Step 2 NSCH":
    step2nsch.run()
elif option == "NSCH Unpivot":
    nschunpivot.run()
