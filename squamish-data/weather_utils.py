from datetime import datetime, timedelta
import os
import json

date_obj_format = "%Y-%m-%d %H:%M:%S"


# Gets weather data given a time object
def get_weather_data(time, location="Squamish"):
    return {"humidity": 10, "temperature": 5, "precipitation": 0}


def get_weather_data_for_frames(frame_dir):
    with open("data.json") as json_file:
        image_dict = json.load(json_file)

    # Get image paths
    image_paths = image_dict.keys()

    for image_path in image_paths:
        filename = image_path.split(".")[0]
        time = filename.split("_")[1] + " " + filename.split("_")[2]

        time_obj = datetime.strptime(time, date_obj_format)

        # get weather data for this time obj
        weather_data = get_weather_data(time)

        # store weather data for this image
        for weather_statistic, weather_value in weather_data.items():
            image_dict[image_path][weather_statistic] = weather_value

        print(time_obj)

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
    for image_path in new_image_dict:
        if image_path in image_paths and not OVERWRITE_EXISTING:
            continue

        existing_image_dict[image_path] = new_image_dict[image_path]

    # Save updated dictionary
    with open("data.json", "w") as f:
        json.dump(existing_image_dict, f)


if __name__ == "__main__":
    new_image_dict = get_weather_data_for_frames("frames/")

    update_json(new_image_dict, OVERWRITE_EXISTING=True)
