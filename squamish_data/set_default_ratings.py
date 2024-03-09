import os
import json

import sys

from squamish_utils import update_json


def set_default_ratings(path, attribute="default_rating"):
    # Read JSON
    with open(path) as json_file:
        image_dict = json.load(json_file)

    # Update the ratings
    for filename in image_dict:
        sunset_attributes = image_dict[filename]

        sunset_attributes[attribute] = 4

    update_json(image_dict, OVERWRITE_EXISTING=True)


if __name__ == "__main__":
    set_default_ratings("data.json")
