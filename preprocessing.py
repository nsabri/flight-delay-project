import pandas as pd


def add_ac_type(df: pd.DataFrame): # Function to create a new column 'AC_TYPE' based on the 'AC' column    
    # Extract the 3-character code from 'AC' and assign it to 'AC_TYPE'
   df.insert( loc=df.columns.get_loc('AC') + 1,  # Insert the new column 'AC_TYPE' right after the 'AC' column
              column='AC_TYPE',
              value=df['AC'].astype(str).str.extract(r'\s(\w{3})')  # Extract the 3-char code
            )
   print("Added 'AC_TYPE' column based on 'AC' column.")
   return df  



def filter_flight_status(df: pd.DataFrame):
    # Filter the DataFrame to include only rows where 'FLIGHT_STATUS' is 'ATA'
    print("Filtering DataFrame for flights with status 'ATA'.")
    return df[df['STATUS'] == 'ATA'].reset_index(drop=True)  # Reset index after filtering



def convert_to_datetime(df : pd.DataFrame): #Converts 'STA' and 'STD' columns in the given DataFrame from string format
    for col in ['STA', 'STD']:
        # Replace first two '.' characters with ':' to match datetime format
        df[col] = df[col].str.replace('.', ':', n=2, regex=False)
        # Convert to datetime format
        df[col] = pd.to_datetime(df[col], format='%Y-%m-%d %H:%M:%S', errors='coerce')
    print("Converted 'STA' and 'STD' columns to datetime format.")
    return df



def add_flight_duration(df: pd.DataFrame):
    # Calculate flight duration in minutes and add it as a new column 'flight_duration'
    df['flight_duration'] = round((df.STA - df.STD) / pd.Timedelta(minutes=1))
    print("Calculated flight duration in minutes and added 'flight_duration' column.")
    return df



def add_month(df):
    # Create 'Month' column with abbreviated month names
    df['month'] = df['STA'].dt.strftime('%b')
    print("Added 'month' column with abbreviated month names.") 
    return df



def add_dayparts(df):
    """
    Adds a 'dayparts' column to the DataFrame based on the hour in the 'STD' datetime column.
    The dayparts are categorized as:
        - Early Morning: 05:00 - 08:59
        - Morning:       09:00 - 11:59
        - Afternoon:     12:00 - 16:59
        - Evening:       17:00 - 20:59
        - Night:         21:00 - 04:59
    """
    hours = df['STD'].dt.hour

    # Define function to map hour to daypart
    def get_daypart(hour):
        if 5 <= hour <= 8:
            return 'Early Morning'
        elif 9 <= hour <= 11:
            return 'Morning'
        elif 12 <= hour <= 16:
            return 'Afternoon'
        elif 17 <= hour <= 20:
            return 'Evening'
        else:
            return 'Night'

    # Apply mapping function to create 'dayparts' column
    df['dayparts'] = hours.apply(get_daypart)
    print("Added 'dayparts' column based on 'STD' hour.")   
    return df

def add_hour_bucket(df):
    """
    Adds a new column 'hour_bucket' to the DataFrame.
    Each hour of the day (0 to 23) is labeled as 'h00', 'h01', ..., 'h23'
    based on the hour extracted from the 'STD' datetime column.
  
    """
    
    # Extract hour and format as 'h00' to 'h23'
    df['hour_bucket'] = df['STD'].dt.hour.apply(lambda x: f'h{x:02}')
    return df

def add_expected_delay(df):
    def hour_to_x(hour_str):
        hour = int(hour_str[1:])  # 'h03' -> 3
        return hour - 3 if hour >= 3 else hour + 21

    df = df.copy() 
    df['x'] = df['hour_bucket'].apply(hour_to_x)
    df['expected_delay'] = 2.9 * df['x'] + 26
    df.drop(columns=['x'], inplace=True)
    return df

def clean_data(df: pd.DataFrame): # One function to clean the DataFrame
    """
    Cleans the DataFrame by applying all preprocessing steps:
    1. Adds 'AC_TYPE' column based on 'AC'.
    2. Filters for flights with status 'ATA'.
    3. Converts 'STA' and 'STD' to datetime.
    4. Adds 'flight_duration' column.
    5. Adds 'month' column.
    6. Adds 'dayparts' column.
    7. Add hour bucket column.
    8. Adds 'expected_delay' column. (Baseline model)
    """
    df = add_ac_type(df)
    df = filter_flight_status(df)
    df = convert_to_datetime(df)
    df = add_flight_duration(df)
    df = add_month(df)
    df = add_dayparts(df)
    df = add_hour_bucket(df)
    df = add_expected_delay(df)
    columns_to_drop = ['ID', 'DATOP', 'FLTID', 'AC', 'STA', 'STD', 'STATUS'] 
    df = df.drop(columns=columns_to_drop)
    print("Dropped unnecessary columns:", columns_to_drop)
    print("Data cleaning completed.")
    return df