import json
import datetime


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

        # if image path not there in existing_image_dict, add a dict for it
        if image_path not in existing_image_dict:
            existing_image_dict[image_path] = image_properties

        # Go through each key/value for this image.
        for key, value in image_properties.items():
            existing_image_dict[image_path][key] = value

    # Save updated dictionary
    with open("data.json", "w") as f:
        json.dump(existing_image_dict, f)


def round_datetime_to_minute(time):

    # Round to the nearest minute
    if time.second >= 30:
        time = time + datetime.timedelta(minutes=1)

    time = time.replace(second=0)

    return time
