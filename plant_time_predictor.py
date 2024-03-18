from datetime import datetime, timedelta
import pandas as pd
from weather_service import get_rainfall_history

def recommend_plant_time_recommendations(longitude, latitude, planting_duration):
    """
    Get plant time recommendations based on rainfall history.

    Args:
        longitude (float): The longitude of the location.
        latitude (float): The latitude of the location.
        planting_duration (int): The duration of the planting window.

    Returns:
        list: A list of recommended planting dates.

    """
    # Get the rainfall history
    rainfall_history = get_rainfall_history(longitude=longitude, latitude=latitude)

    # Calculate the average rainfall
    rainfall_prediction = calculate_average_rainfall(rainfall_history)

    # Find the best planting windows
    best_windows = find_best_planting_windows(rainfall_prediction, window_size=planting_duration)

    # Get the recommendation dates
    recommended_dates = get_recommendation_dates(best_windows)

    return recommended_dates

def calculate_average_rainfall(df):
    # Convert the date to datetime and set it as the index
    df['date'] = pd.to_datetime(df['date'])
    df.set_index('date', inplace=True)

    # Group by day of year and calculate the mean
    avg_df = df.groupby(df.index.dayofyear).mean()

    # Reset the index
    avg_df.reset_index(inplace=True)

    # Explicitly set the column names
    avg_df.columns = ['day_of_year', 'average_rainfall']

    return avg_df

def find_best_planting_windows(df, window_size, num_windows=3, min_days_between=30):
    # Calculate the rolling sum of rainfall
    df['rolling_rainfall'] = df['average_rainfall'].rolling(window_size, min_periods=1).sum()

    # Initialize a list to store the best windows
    best_windows = []

    # While we need more windows
    while len(best_windows) < num_windows:
        # Find the maximum rolling sum
        max_rainfall = df['rolling_rainfall'].max()

        # Find the day of the year with this maximum rolling sum
        best_day = df[df['rolling_rainfall'] == max_rainfall]['day_of_year'].values[0]

        # Convert best_day to a Python int before appending
        best_windows.append(int(best_day))

        # Remove the window and the days around it from consideration
        start_day = max(0, best_day - window_size - min_days_between)
        end_day = min(365, best_day + window_size + min_days_between)
        df = df[(df['day_of_year'] < start_day) | (df['day_of_year'] > end_day)]

    return best_windows

def get_recommendation_dates(best_windows):
    # Get today's date
    today = datetime.today()

    # Initialize a list to store the recommendations
    recommendations = []

    # For each window
    for window in best_windows:
        # Calculate the start date of the window
        start_date = datetime(today.year, 1, 1) + timedelta(days=window - 1)

        # If the start date is before today, add one year
        if start_date < today:
            start_date = start_date.replace(year=start_date.year + 1)

        # Calculate the end date of the window (two weeks after the start date)
        end_date = start_date + timedelta(weeks=2)

        # Add the recommendation to the list
        recommendations.append({
            'start_date': start_date,
            'end_date': end_date
        })

    return recommendations