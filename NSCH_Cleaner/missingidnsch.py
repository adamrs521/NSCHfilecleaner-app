import streamlit as st
import pandas as pd

def process_unique_identifiers(df):
    # Standardize the format of existing IDs
    def standardize_existing_id(row):
        if pd.isna(row['Your_Unique_Identifier']) or not str(row['Your_Unique_Identifier']).isdigit():
            return None  # Mark non-numeric or missing IDs as invalid
        return row['Your_Unique_Identifier']

    df['Your_Unique_Identifier'] = df.apply(standardize_existing_id, axis=1)

    # Identify missing or invalid IDs
    missing_ids = df['Your_Unique_Identifier'].isna()

    # Extract numeric part of existing IDs and determine starting ID
    existing_ids = df.loc[~missing_ids, 'Your_Unique_Identifier'].astype(float)
    starting_id = int(existing_ids.max() + 1) if not existing_ids.empty else 10000

    # Create a mapping of new unique IDs for students with missing IDs
    id_mapping = {}
    for _, group in df[missing_ids].groupby(['First_Name', 'Last_Name']):
        key = (group['First_Name'].iloc[0], group['Last_Name'].iloc[0])
        if key not in id_mapping:
            id_mapping[key] = str(starting_id)
            starting_id += 1

    # Assign unique IDs
    def assign_final_identifier(row):
        if pd.isna(row['Your_Unique_Identifier']):
            return id_mapping.get((row['First_Name'], row['Last_Name']))
        return row['Your_Unique_Identifier']

    df['Your_Unique_Identifier'] = df.apply(assign_final_identifier, axis=1)

    return df

# Streamlit App
def run():
    st.title("Unique Identifier Generator for Students")

    # File uploader
    uploaded_file = st.file_uploader("Upload your CSV file", type=["csv"])

    if uploaded_file:
        # Read the uploaded file
        df = pd.read_csv(uploaded_file)

        st.write("### Original Data")
        st.dataframe(df.head())

        # Process the data
        updated_df = process_unique_identifiers(df)

        st.write("### Updated Data with Unique Identifiers")
        st.dataframe(updated_df.head())

        # Allow the user to download the processed file
        csv = updated_df.to_csv(index=False).encode('utf-8')
        st.download_button(
            label="Download Updated CSV",
            data=csv,
            file_name="updated_student_data.csv",
            mime="text/csv",
        )

# Prevent auto-execution when imported
if __name__ == "__main__":
    run()
