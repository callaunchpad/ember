from datetime import datetime, timedelta, time, date
import os
import json

import http.client
from meteostat import Point, Daily, Hourly
from utils import update_json, round_datetime_to_minute

from suntime import Sun, SunTimeException

import requests
from geopy.geocoders import Nominatim

date_obj_format = "%Y-%m-%d %H:%M:%S"

SQUAMISH_COORDS = (
    49.7016,
    -123.1558,  # DONT FORGET NEGATIVE
)
sun = Sun(SQUAMISH_COORDS[0], SQUAMISH_COORDS[1])

SQUAMISH_METEOSTAT_ID = "71211"  # "71207"

WEATHER_STATISTICS = {
    "temp",
    "dwpt",
    "rhum",
    "prcp",
    "wspd",
    "pres",
    "coco",
}


def get_weather_df(start_time, end_time):
    # Make start_time slightly smaller in case
    start_time -= timedelta(days=1)

    # Make end_time slightly bigger in case
    end_time += timedelta(days=1)

    # Get daily data for 2018
    data = Hourly(SQUAMISH_METEOSTAT_ID, start_time, end_time)
    data = data.fetch()

    print(data)

    # Currently, time is the index of the df. reset index to make it a column.
    data = data.reset_index()

    return data


# Gets weather data given a time object
def get_weather_data(time, weather_df, location="Squamish"):
    # Find closest time in the weather_df
    print(weather_df.columns)

    closest_row = weather_df.iloc[(weather_df["time"] - time).abs().argsort()[:1]]

    print(closest_row)

    weather_data = {}

    for statistic in WEATHER_STATISTICS:
        weather_data[statistic] = closest_row[statistic].iloc[0]

    # Plot line chart including average, minimum and maximum temperature
    # data.plot(y=["tavg", "tmin", "tmax"])
    # plt.show()

    return weather_data


def parse_time_from_image_path(image_path):
    filename = image_path.split(".")[0]
    time = filename.split("_")[1] + " " + filename.split("_")[2]
    time_obj = datetime.strptime(time, date_obj_format)
    return time_obj


def get_weather_data_for_frames(frame_dir):
    with open("json_data/data.json") as json_file:
        image_dict = json.load(json_file)

    # Get image paths
    image_paths = image_dict.keys()

    times = list(map(parse_time_from_image_path, image_paths))

    earliest_time = min(times)
    latest_time = max(times)

    # Create weather_df
    weather_df = get_weather_df(earliest_time, latest_time)

    print(weather_df)

    for image_path in image_paths:
        time = parse_time_from_image_path(image_path)

        # get weather data for this time obj
        weather_data = get_weather_data(time, weather_df)

        # store weather data for this image
        for weather_statistic, weather_value in weather_data.items():
            image_dict[image_path][weather_statistic] = weather_value

    print(image_dict)

    return image_dict


# day_obj specifies the year-month-day
def get_sunset_time(day_obj):
    r = requests.get(
        "https://api.sunrisesunset.io/json",
        params={
            "lat": SQUAMISH_COORDS[0],
            "lng": SQUAMISH_COORDS[1],
            "date": day_obj,
            "timezone": "PST",
        },
    ).json()
    sunset = r["results"]["sunset"]

    # Convert date format to our format
    time_obj = datetime.strptime(sunset, "%I:%M:%S %p").time()
    date_obj = date(day_obj.year, day_obj.month, day_obj.day)

    datetime_obj = datetime.combine(date_obj, time_obj)
    # formatted_datetime = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
    return datetime_obj


if __name__ == "__main__":
    new_image_dict = get_weather_data_for_frames("frames/")

    update_json(new_image_dict, OVERWRITE_EXISTING=True)

    # print(get_sunset_time(datetime.strptime("2020-05-08 00:00:00", date_obj_format)))
