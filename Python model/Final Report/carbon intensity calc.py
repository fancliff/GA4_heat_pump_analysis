import pandas as pd

def calculate_daily_avg_carbon_intensity(input_file, output_file):
    # Load the CSV file
    data = pd.read_csv(input_file)

    # Convert the DATETIME column to pandas datetime format
    data['DATETIME'] = pd.to_datetime(data['DATETIME'])

    # Extract the date from the datetime
    data['DATE'] = data['DATETIME'].dt.date

    # Calculate the daily average carbon intensity
    # daily_avg = data.groupby('DATE')['CARBON_INTENSITY'].mean().reset_index() # for csv
    daily_avg = data.groupby('DATE')['CARBON_INTENSITY'].mean() # for txt

    # Save the result to a CSV file
    #daily_avg.to_csv(output_file, index=False)
    
    # Save the result to a text file 
    with open(output_file, 'w') as f:
        for intensity in daily_avg:
            f.write(f"{intensity}\n")
    
    print(f'Daily average carbon intensities saved to {output_file}')

input_file = 'C:\\Users\Freddie\OneDrive - University of Cambridge\Engineering\GA4\Python model\Final Report\\df_fuel_ckan.csv'
# output_file = 'C:\\Users\Freddie\OneDrive - University of Cambridge\Engineering\GA4\Python model\Final Report\\uk_daily_avg_carbon_intensity_2023.csv'
output_file = 'C:\\Users\Freddie\OneDrive - University of Cambridge\Engineering\GA4\Python model\Final Report\\uk_daily_avg_carbon_intensity_2023.txt'
calculate_daily_avg_carbon_intensity(input_file, output_file)
