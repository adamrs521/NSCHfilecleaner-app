import streamlit as st
import pandas as pd

# Function to clean the dataset
def clean_student_data(df):
    # Ensure Enrollment_Begin is treated as a string and extract the first 4 digits as the year
    df["Enrollment_Begin"] = df["Enrollment_Begin"].astype(str).str[:4]
    df["Enrollment_Begin"] = pd.to_numeric(df["Enrollment_Begin"], errors="coerce")
    
    # Update School_Year based on Season rules
    df.loc[df["Season"] == "Fall", "School_Year"] = df["Enrollment_Begin"]
    df.loc[df["Season"].isin(["Spring", "Summer"]), "School_Year"] = df["Enrollment_Begin"] - 1
    
    # Ensure Sequence_Order follows "Season Sequence" format
    df["Sequence"] = df["Sequence"].fillna(0).astype(int)
    df["Sequence_Order"] = df["Season"] + " " + df["Sequence"].astype(str)
    
    # Identify students who have "Graduated" as "Y"
    graduated_students = df[df["Graduated"] == "Y"]["Your_Unique_Identifier"].unique()
    
    # Update Enrollment_Status to "G" only for sequences after the first "Y" in Graduated
    for student_id in graduated_students:
        student_rows = df[df["Your_Unique_Identifier"] == student_id].copy()
        grad_sequence = student_rows[student_rows["Graduated"] == "Y"]["Sequence"].min()
        df.loc[
            (df["Your_Unique_Identifier"] == student_id) & (df["Sequence"] > grad_sequence),
            "Enrollment_Status"
        ] = "G"
    
    # Ensure all subsequent rows after a "G" remain "G"
    for student_id in df["Your_Unique_Identifier"].unique():
        student_mask = df["Your_Unique_Identifier"] == student_id
        student_records = df[student_mask].copy()
        first_g_index = student_records[student_records["Enrollment_Status"] == "G"].index.min()
        if not pd.isna(first_g_index):
            df.loc[(student_mask) & (df.index >= first_g_index), "Enrollment_Status"] = "G"
    
    # Fill blank Enrollment_Status with "U"
    df["Enrollment_Status"].fillna("U", inplace=True)
    
    # Update Enrollment_Status values based on the given mapping
    status_mapping = {
        "G": "Graduated",
        "W": "Withdrawn",
        "Q": "Persisted",
        "H": "Persisted",
        "F": "Persisted",
        "L": "Persisted",
        "U": "Unknown"
    }
    df["Enrollment_Status"] = df["Enrollment_Status"].map(status_mapping).fillna(df["Enrollment_Status"])
    
    return df

# Streamlit app
def run():
    st.title("Student Data Cleaning App")
    
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Original Data Preview")
        st.dataframe(df.head())
        
        df_cleaned = clean_student_data(df)
        
        st.write("### Cleaned Data Preview")
        st.dataframe(df_cleaned.head())
        
        # Provide download link for cleaned data
        csv = df_cleaned.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Cleaned Data",
            data=csv,
            file_name="cleaned_student_data.csv",
            mime="text/csv"
        )

# This ensures it doesn't run automatically when imported
if __name__ == "__main__":
    run()
