from datetime import datetime, timedelta
import os
import json

import http.client
from meteostat import Point, Daily, Hourly

date_obj_format = "%Y-%m-%d %H:%M:%S"

SQUAMISH_COORDS = Point(
    49.7016,
    123.1558,
)

SQUAMISH_METEOSTAT_ID = "71207"

WEATHER_STATISTICS = {"temp", "dwpt", "rhum", "prcp", "wspd", "pres", "coco"}


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
    with open("data.json") as json_file:
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


# Updates json with new image dict. If image already in data.json, it's not added again.
def update_json(new_image_dict, OVERWRITE_EXISTING=False):
    # Read JSON
    with open("data.json") as json_file:
        existing_image_dict = json.load(json_file)

    # Get image paths
    image_paths = existing_image_dict.keys()

    # Update the existing dictionary with new images
    for image_path, image_properties in new_image_dict.items():
        if image_path in image_paths and not OVERWRITE_EXISTING:
            continue

        # Go through each key/value for this image.
        for key, value in image_properties.items():
            existing_image_dict[image_path][key] = value

    # Save updated dictionary
    with open("data.json", "w") as f:
        json.dump(existing_image_dict, f)


if __name__ == "__main__":
    new_image_dict = get_weather_data_for_frames("frames/")

    update_json(new_image_dict, OVERWRITE_EXISTING=True)
