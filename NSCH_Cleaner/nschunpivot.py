import streamlit as st
import pandas as pd

# Function to transform the dataset
def unpivot_student_data(df):
    # Keep necessary identifier columns
    id_columns = ["Your_Unique_Identifier", "First_Name", "Last_Name", "High_School_Grad_Date", "High_School_Code"]
    
    # Pivot data so that Sequence_Order values become columns with Enrollment_Status as values
    df_pivot = df.pivot_table(index=id_columns, columns="Sequence_Order", values="Enrollment_Status", aggfunc="first").reset_index()
    
    return df_pivot

# Streamlit app
def run():
    st.title("Student Data Transformation App")
    
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])
    if uploaded_file is not None:
        df = pd.read_csv(uploaded_file)
        st.write("### Original Data Preview")
        st.dataframe(df.head())
        
        df_transformed = unpivot_student_data(df)
        
        st.write("### Transformed Data Preview")
        st.dataframe(df_transformed.head())
        
        # Provide download link for transformed data
        csv = df_transformed.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Transformed Data",
            data=csv,
            file_name="transformed_student_data.csv",
            mime="text/csv"
        )

# Prevent automatic execution when imported
if __name__ == "__main__":
    run()
