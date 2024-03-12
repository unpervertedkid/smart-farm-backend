import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry
from datetime import timedelta
from datetime import date

def get_estimated_weather_conditions(longitude, latitude, duration_months=3, start_date=None):
    # Call the get_weather_data function with the given parameters
    averages = _get_weather_data(longitude, latitude, duration_months, start_date)
    
    # Call the get_average_weather_data function with the averages data
    overall_averages = _get_average_weather_data(averages)
    
    return {
        'relative_humidity': overall_averages[0],
        'temperature': overall_averages[1],
        'rainfall': overall_averages[2]
    }

def _get_weather_data(latitude, longitude, duration_months, start_date=None):
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)

    # If no start date is provided, use the current date
    if start_date is None:
        start_date = date.today()

    # Calculate the end date based on the duration
    end_date = start_date + timedelta(days=30*duration_months)
    
    # Initialize a dictionary to store the averages for each year
    averages = {}

    years_back = 3
    current_year = 1

    # Loop over the last 3 years
    while current_year <= years_back:
        # Calculate the start and end date for the current year
        start_date_year = start_date - timedelta(days=365*current_year)
        end_date_year = end_date - timedelta(days=365*current_year)

        current_year += 1
        
        # Define the parameters for the API request
        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": start_date_year.strftime('%Y-%m-%d'),
            "end_date": end_date_year.strftime('%Y-%m-%d'),
            "hourly": "relative_humidity_2m",
            "daily": ["temperature_2m_mean", "rain_sum"],
            "timezone": "Africa/Cairo"
        }
		
        # Make the API request
        url = "https://archive-api.open-meteo.com/v1/archive"
        responses = openmeteo.weather_api(url, params=params)

        # Process the first location
        response = responses[0]

        # Process hourly data
        hourly = response.Hourly()
        hourly_relative_humidity_2m = hourly.Variables(0).ValuesAsNumpy()

        hourly_data = {"date": pd.date_range(
            start=pd.to_datetime(hourly.Time(), unit="s", utc=True),
            end=pd.to_datetime(hourly.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=hourly.Interval()),
            inclusive="left"
        )}
        hourly_data["relative_humidity_2m"] = hourly_relative_humidity_2m

        hourly_dataframe = pd.DataFrame(data=hourly_data)

        # Process daily data
        daily = response.Daily()
        daily_temperature_2m_mean = daily.Variables(0).ValuesAsNumpy()
        daily_rainfall_sum = daily.Variables(1).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        daily_data["temperature_2m_mean"] = daily_temperature_2m_mean
        daily_data["rain_sum"] = daily_rainfall_sum

        daily_dataframe = pd.DataFrame(data=daily_data)

        # Resample hourly data to daily data and calculate the mean
        hourly_dataframe.set_index('date', inplace=True)
        hourly_dataframe_daily = hourly_dataframe.resample('D').mean()

        # Calculate the averages for the current year
        average_daily_relative_humidity = hourly_dataframe_daily['relative_humidity_2m'].mean()
        average_daily_temperature = daily_dataframe['temperature_2m_mean'].mean()
        average_daily_rainfall = daily_dataframe['rain_sum'].mean()

        # Store the averages in the dictionary
        averages[start_date_year.year] = {
            'average_daily_relative_humidity': average_daily_relative_humidity,
            'average_daily_temperature': average_daily_temperature,
            'average_daily_rainfall': average_daily_rainfall
        }

    return averages

def _get_average_weather_data(averages):
    # Initialize variables to store the sum of each parameter
    sum_relative_humidity = 0
    sum_temperature = 0
    sum_precipitation = 0
        
    # Loop over the years in the averages dictionary
    for year in averages:
        # Get the average values for the current year
        year_data = averages[year]
        average_relative_humidity = year_data['average_daily_relative_humidity']
        average_temperature = year_data['average_daily_temperature']
        average_precipitation = year_data['average_daily_rainfall']
            
        # Add the averages to the sum variables
        sum_relative_humidity += average_relative_humidity
        sum_temperature += average_temperature
        sum_precipitation += average_precipitation
        
    # Calculate the overall averages
    num_years = len(averages)
    overall_average_relative_humidity = sum_relative_humidity / num_years
    overall_average_temperature = sum_temperature / num_years
    overall_average_precipitation = sum_precipitation / num_years
        
    # Return the overall averages
    return overall_average_relative_humidity, overall_average_temperature, overall_average_precipitation





# Example usage
# Average weather for nairobi
longitude = 36.817223
latitude = 1.286389

# Get the estimated weather conditions for the next 3 months
estimated_weather = get_estimated_weather_conditions(longitude, latitude, 3)
print(estimated_weather)