# take in some path to an input json
# specify the rating that you want to reduce the # of occurences
# specify how many images you want to randomly select from iamges with that rating
# save to some output json


import json
import os
import random
import numpy as np


def get_specific_rating(data, rating_to_reduce):
    ans = []
    for key, value in data.items():
        if value["rating"] == rating_to_reduce:
            ans.append(key)
    return ans


def select_some(data, remove_num):
    random.shuffle(data)
    return data[:remove_num]


def reduce_data(input_path, output_path, rating_to_reduce, output_num):

    with open(input_path, "r") as file:
        data = json.load(file)

    rating_data = get_specific_rating(data, rating_to_reduce)  # list of keys
    to_remove = select_some(
        rating_data, max(0, len(rating_data) - output_num)
    )  # list of keys

    for key in to_remove:
        del data[key]

    with open(output_path, "w") as file:
        json.dump(data, file, indent=4)

    print(f"Reduced data saved to {output_path}")


if __name__ == "__main__":
    # Example usage
    input_path = "json_data/datav2_augmented_noisy.json"
    output_path = "json_data/datav2_augmented_noisy_fewer_1s.json"
    rating_to_reduce = [1, 0, 0, 0, 0]  # Remove 1's
    output_num = 400

    reduce_data(input_path, output_path, rating_to_reduce, output_num)
