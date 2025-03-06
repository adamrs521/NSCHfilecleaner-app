import streamlit as st
import pandas as pd

def generate_missing_rows(df):
    # Seasons in correct order for academic years
    season_order = ['Summer', 'Fall', 'Spring']

    # Initialize a list to hold new rows
    new_rows = []

    # Iterate over each unique student ID
    for student_id in df['Your_Unique_Identifier'].unique():
        student_data = df[df['Your_Unique_Identifier'] == student_id].copy()

        # Safely extract the Class_Of value
        if not student_data['Class_Of'].isna().all():
            class_of_year = int(student_data['Class_Of'].dropna().iloc[0])
        else:
            continue  # Skip students with no Class_Of year

        # Generate all combinations from Summer of Class_Of to Summer of Class_Of + 10
        for year_offset in range(0, 11):
            for season in season_order:
                # Calculate the corresponding School Year
                if season == 'Fall':
                    school_year = class_of_year + year_offset - 1
                else:
                    school_year = class_of_year + year_offset  # Spring/Summer are the next academic year

                # Check if a row for this season and school year already exists
                existing_row = student_data[
                    (student_data['Season'] == season) & (student_data['School_Year'] == str(school_year))
                ]

                if existing_row.empty:
                    # Create new row if it doesn't exist
                    new_row = {
                        'Your_Unique_Identifier': student_id,
                        'First_Name': student_data['First_Name'].iloc[0],
                        'Last_Name': student_data['Last_Name'].iloc[0],
                        'High_School_Grad_Date': student_data['High_School_Grad_Date'].iloc[0],
                        'College_Name': student_data['College_Name'].iloc[0],
                        'High_School_Code': student_data['High_School_Code'].iloc[0],
                        'Enrollment_Begin': None,
                        'Enrollment_Status': 'U',  # Default to 'U'
                        'Graduated': None,
                        'Graduation_Date': None,
                        'Season': season,
                        'Class_Of': str(class_of_year),
                        'School_Year': str(school_year)
                    }
                    new_rows.append(new_row)

    # Convert new_rows list into a DataFrame and concatenate with original df
    if new_rows:
        new_rows_df = pd.DataFrame(new_rows)
        df = pd.concat([df, new_rows_df], ignore_index=True)

    return df

def clean_data(df):
    df = df[['Your_Unique_Identifier', 'First_Name', 'Last_Name', 'High_School_Grad_Date', 'College_Name', 'High_School_Code', 
             'Enrollment_Begin', 'Enrollment_Status', 'Graduated', 'Graduation_Date']]

    # Fill Enrollment_Begin from Graduation_Date if missing
    df['Enrollment_Begin'] = df.apply(
        lambda row: row['Graduation_Date'] if pd.isnull(row['Enrollment_Begin']) and not pd.isnull(row['Graduation_Date']) else row['Enrollment_Begin'],
        axis=1
    )

    # Format dates as YYYYMMDD strings
    for date_column in ['Enrollment_Begin', 'Graduation_Date', 'High_School_Grad_Date']:
        df[date_column] = df[date_column].astype(str).str[:8]

    # Convert High_School_Grad_Date to datetime for Class_Of calculation
    df['High_School_Grad_Date'] = pd.to_datetime(df['High_School_Grad_Date'], format='%Y%m%d', errors='coerce')

    # Calculate Class_Of year
    def calculate_class_of(grad_date):
        if pd.isnull(grad_date):
            return None
        return grad_date.year + 1 if grad_date.month > 8 else grad_date.year

    df['Class_Of'] = df['High_School_Grad_Date'].apply(calculate_class_of)

    # Determine Season based on Enrollment_Begin date
    df['Season'] = pd.to_datetime(df['Enrollment_Begin'], format='%Y%m%d', errors='coerce').dt.month.map({
        9: 'Fall', 10: 'Fall', 11: 'Fall', 12: 'Fall',
        1: 'Spring', 2: 'Spring', 3: 'Spring', 4: 'Spring',
        5: 'Summer', 6: 'Summer', 7: 'Summer', 8: 'Fall'
    })

    # Add "School_Year" column
    df['School_Year'] = df.apply(
        lambda row: str(int(row['Enrollment_Begin'][:4]) - 1) if pd.notnull(row['Enrollment_Begin']) and row['Enrollment_Begin'] != 'nan' and row['Season'] in ['Spring', 'Summer'] else (
            row['Enrollment_Begin'][:4] if pd.notnull(row['Enrollment_Begin']) and row['Enrollment_Begin'] != 'nan' else (
                str(int(row['Graduation_Date'][:4]) - 1) if pd.notnull(row['Graduation_Date']) and row['Graduation_Date'] != 'nan' and row['Season'] in ['Spring', 'Summer'] else (
                    row['Graduation_Date'][:4] if pd.notnull(row['Graduation_Date']) and row['Graduation_Date'] != 'nan' else None
                )
            )
        ), axis=1
    )

    # Add "Sequence"
    df['Sequence'] = df.apply(
        lambda row: int(row['School_Year']) - int(row['Class_Of']) + 1 if pd.notnull(row['School_Year']) and pd.notnull(row['Class_Of']) else None,
        axis=1
    )

    return df

# Streamlit App
def run():
    st.title('Student Data Cleaning and Row Generation')

    uploaded_file = st.file_uploader("Upload your CSV file", type="csv")

    if uploaded_file:
        df = pd.read_csv(uploaded_file)

        st.write("### Original Data")
        st.dataframe(df.head())

        cleaned_df = clean_data(df)

        st.write("### Cleaned Data")
        st.dataframe(cleaned_df.head())

        # Generate missing rows
        completed_df = generate_missing_rows(cleaned_df)

        # Add "Sequence" after generating missing rows
        completed_df['Sequence'] = completed_df.apply(
            lambda row: int(row['School_Year']) - int(row['Class_Of']) + 1 if pd.notnull(row['School_Year']) and pd.notnull(row['Class_Of']) else None,
            axis=1
        )

        # Add "Sequence_Order"
        completed_df['Sequence_Order'] = completed_df.apply(
            lambda row: f"{row['Season']} {int(row['Sequence'])}" if pd.notnull(row['Season']) and pd.notnull(row['Sequence']) else None,
            axis=1
        )

        st.write("### Completed Data with Missing Rows, Sequence, and Sequence Order")
        st.dataframe(completed_df.head())

        csv = completed_df.to_csv(index=False).encode('utf-8')

        st.download_button(
            label="Download Completed Data",
            data=csv,
            file_name='completed_student_data.csv',
            mime='text/csv',
        )

# Prevent auto-execution when imported
if __name__ == "__main__":
    run()
