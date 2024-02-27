import requests
from datetime import datetime
import json
from utils import update_json
from dotenv import load_dotenv
import os

load_dotenv()  # take environment variables from .env.

# These are the coords in the info tab in visual crossing when you search squamish
SQUAMISH_COORDS = (
    49.6867,
    -123.1350,
    # 49.6985,
    # -123.155,  # DONT FORGET NEGATIVE
)

KEY = os.environ.get("VISUAL_CROSSING_KEY")
date_obj_format = "%Y-%m-%d %H:%M:%S"
location = "Squamish,BC,Canada"

statistics = [
    "temp",
    "humidity",
    "dew",
    "precip",
    "precipprob",
    "snow",
    "snowdepth",
    "preciptype",
    "windgust",
    "windspeed",
    "pressure",
    "cloudcover",
    "solarradiation",
    "solarenergy",
    "conditions",
]


def reformat_date_for_api(date):
    return date.strftime("%Y-%m-%dT%H:%M:%S")


def get_weather_data(date):
    print(f"---- Retrieving weather data for {date} ----")

    formatted_date = reformat_date_for_api(date)

    url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/{SQUAMISH_COORDS[0]},{SQUAMISH_COORDS[1]}/{formatted_date}"

    r = requests.get(
        url,
        params={
            "key": KEY,
            "include": "current",
        },
    ).json()

    result = {}

    for statistic in statistics:
        result[statistic] = r["currentConditions"][statistic]

    # Manually add day's visibility, although I don't think this is tied to a specific hour
    result["overall_day_visibility"] = r["days"][0]["visibility"]
    result["overall_day_preciptype"] = r["days"][0]["preciptype"]

    return result


def parse_time_from_image_path(image_path):
    filename = image_path.split(".")[0]
    time = filename.split("_")[1] + " " + filename.split("_")[2]
    time_obj = datetime.strptime(time, date_obj_format)
    return time_obj


def get_weather_data_for_frames(frame_dir, OVERWRITE=False):
    with open("data.json") as json_file:
        image_dict = json.load(json_file)

    # Get image paths
    image_paths = image_dict.keys()

    times = list(map(parse_time_from_image_path, image_paths))

    for image_path in image_paths:
        time = parse_time_from_image_path(image_path)

        # Check if the statistics all already there for this image. If it's already there, no need to make a new API call unless OVERWRITE is specified.
        existing_weather_data = image_dict[image_path]
        has_all_statistics = True
        for statistic in statistics:
            if statistic not in existing_weather_data:
                has_all_statistics = False
                break

        # If already has all the statistics (and OVERWRITE=False), no need to call API
        if has_all_statistics and not OVERWRITE:
            print(
                f"---- Skipping adding weather data for {time} as all statistics exist already. ----"
            )
            continue

        # get weather data for this time obj
        weather_data = get_weather_data(time)

        # store weather data for this image
        for weather_statistic, weather_value in weather_data.items():
            image_dict[image_path][weather_statistic] = weather_value

    return image_dict


if __name__ == "__main__":
    image_dict = get_weather_data_for_frames("frames/", OVERWRITE=False)
    update_json(image_dict, OVERWRITE_EXISTING=True)
