from datetime import datetime, timedelta
import os
import json

date_obj_format = "%Y-%m-%d %H:%M:%S"


# Gets weather data given a time object
def get_weather_data(time, location="Squamish"):
    return {"humidity": 10, "temperature": 5, "precipitation": 0}


def save_weather_data(time, json_path="data.json"):
    weather_data = get_weather_data(time)


def save_weather_data_for_frames(frame_dir):
    # iterate through frames in frame_dir
    files = os.listdir(frame_dir)

    frame_files = [
        file
        for file in files
        if file.endswith(".jpg") or file.endswith(".png") or file.endswith(".jpeg")
    ]

    with open("data.json") as json_file:
        existing_image_dict = json.load(json_file)

    for frame_file in frame_files:
        filename = frame_file.split(".")[0]
        time = filename.split("_")[1] + " " + filename.split("_")[2]

        time_obj = datetime.strptime(time, date_obj_format)

        print(time_obj)


if __name__ == "__main__":
    save_weather_data_for_frames("frames/")
