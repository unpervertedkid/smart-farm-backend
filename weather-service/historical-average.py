import openmeteo_requests
import requests_cache
import pandas as pd
from retry_requests import retry

# Setup the Open-Meteo API client with cache and retry on error
cache_session = requests_cache.CachedSession('.cache', expire_after=-1)
retry_session = retry(cache_session, retries=5, backoff_factor=0.2)
openmeteo = openmeteo_requests.Client(session=retry_session)

def get_historical_rain(longitude, latitude, duration_months):
    # Calculate the start and end dates for the historical data
    today = pd.Timestamp.today()
    start_date = today - pd.DateOffset(years=3)
    end_date = today + pd.DateOffset(months=duration_months)

    # Initialize an empty DataFrame to store all daily data
    all_daily_data = pd.DataFrame()

    for year in range(3):
        # Calculate the start and end dates for each year
        yearly_start_date = start_date + pd.DateOffset(years=year)
        yearly_end_date = yearly_start_date + pd.DateOffset(months=duration_months)

        params = {
            "latitude": latitude,
            "longitude": longitude,
            "start_date": yearly_start_date.strftime("%Y-%m-%d"),
            "end_date": yearly_end_date.strftime("%Y-%m-%d"),
            "daily": "precipitation_sum",
            "timezone": "Africa/Cairo"
        }
        url = "https://archive-api.open-meteo.com/v1/archive"
        responses = openmeteo.weather_api(url, params)

        # Process first location. Add a for-loop for multiple locations or weather models
        response = responses[0]

        # Process daily data. The order of variables needs to be the same as requested.
        daily = response.Daily()
        daily_precipitation_sum = daily.Variables(0).ValuesAsNumpy()

        daily_data = {"date": pd.date_range(
            start=pd.to_datetime(daily.Time(), unit="s", utc=True),
            end=pd.to_datetime(daily.TimeEnd(), unit="s", utc=True),
            freq=pd.Timedelta(seconds=daily.Interval()),
            inclusive="left"
        )}
        daily_data["precipitation_sum"] = daily_precipitation_sum

        daily_dataframe = pd.DataFrame(data=daily_data)
        all_daily_data = pd.concat([all_daily_data, daily_dataframe])

    average_rain = all_daily_data["precipitation_sum"].mean()
    return average_rain
# Example usage
longitude = 34.9468
latitude = -0.7761
duration_months = 3

average_rain = get_historical_rain(longitude, latitude, duration_months)
print(f"Average rainfall for the past 3 years for a {duration_months} month duration in Nairobi, Kenya: {average_rain} mm")