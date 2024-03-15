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
        sum_rainfall_for_duration = daily_dataframe['rain_sum'].sum()
        

        # Store the averages in the dictionary
        averages[start_date_year.year] = {
            'average_daily_relative_humidity': average_daily_relative_humidity,
            'average_daily_temperature': average_daily_temperature,
            'sum_rainfall_for_duration': sum_rainfall_for_duration
        }

    return averages

def _get_average_weather_data(averages):
    # Initialize variables to store the sum of each parameter
    sum_relative_humidity = 0
    sum_temperature = 0
    sum_rainfall = 0
        
    # Loop over the years in the averages dictionary
    for year in averages:
        # Get the average values for the current year
        year_data = averages[year]
        average_relative_humidity = year_data['average_daily_relative_humidity']
        average_temperature = year_data['average_daily_temperature']
        average_rainfall = year_data['sum_rainfall_for_duration']
            
        # Add the averages to the sum variables
        sum_relative_humidity += average_relative_humidity
        sum_temperature += average_temperature
        sum_rainfall += average_rainfall
        
    # Calculate the overall averages
    num_years = len(averages)
    overall_average_relative_humidity = sum_relative_humidity / num_years
    overall_average_temperature = sum_temperature / num_years
    overall_average_rainfall = sum_rainfall / num_years
        
    # Return the overall averages
    return overall_average_relative_humidity, overall_average_temperature, overall_average_rainfall

# Get three last years rainfall history
def get_rainfall_history(longitude, latitude, duration_in_years=3):
    cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
    retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
    openmeteo = openmeteo_requests.Client(session=retry_session)
    
    results = {}
    # End should be the previous year 31st December and start should be duration of years before that but 1st January
    one_year_ago = date.today() - timedelta(days=365)
    end_date = one_year_ago.replace(month=12, day=31)
    
    start_date = end_date - timedelta(days=365*duration_in_years)
    start_date = start_date.replace(month=1, day=1)
    
    
    url = "https://archive-api.open-meteo.com/v1/archive"
    
    params = {
	"latitude": latitude,
	"longitude": longitude,
	"start_date": start_date.strftime('%Y-%m-%d'),
	"end_date": end_date.strftime('%Y-%m-%d'),
	"daily": "rain_sum",
	"timezone": "Africa/Cairo"
    }
    
    responses = openmeteo.weather_api(url, params=params)
    
    response = responses[0]
    
    # Process daily data. The order of variables needs to be the same as requested.
    daily = response.Daily()
    daily_rain_sum = daily.Variables(0).ValuesAsNumpy()

    daily_data = {"date": pd.date_range(
        start = pd.to_datetime(daily.Time(), unit = "s", utc = True),
        end = pd.to_datetime(daily.TimeEnd(), unit = "s", utc = True),
        freq = pd.Timedelta(seconds = daily.Interval()),
        inclusive = "left"
    )}
    daily_data["rain_sum"] = daily_rain_sum

    daily_dataframe = pd.DataFrame(data = daily_data)
    return daily_dataframe
    
# Test the function with a duration of three years
get_rainfall_history(-0.7761, 34.9468, 3)