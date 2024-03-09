import os
import pickle
from torch.utils.data import Dataset
import torch
import numpy as np
import sys
import json
import numpy as np

sys.path.append("../utils")
from utils import normalize


class RatingsDataset(Dataset):
    """Dataset class for sunset data."""

    def __init__(self, config):
        self.input_features = config["INPUT_FEATURES"]

        input_dir = config["INPUT_DIR"]

        with open(input_dir) as f:
            image_dict = json.load(f)

        self.config = config

        # Stores image filepaths (the keys in data.json)
        self.data_paths = list(image_dict.keys())

        # Convert image dict to only store necessary features. Also convert weather statistics to be stored in a list instead of a map.
        self.data = self.convert_image_dict_weather_data_to_lists(image_dict)

        self.input_dir = input_dir

        self.normalize = config["NORMALIZE"]

        # print(self.data)

    def convert_image_dict_weather_data_to_lists(self, image_dict):
        inputs = []
        outputs = []

        # The data
        data = {}

        # Go through each image path in the image_dict
        for image_path, weather_data_map in image_dict.items():
            weather_data_list = []

            has_nan = False

            for feature in self.input_features:
                statistic = image_dict[image_path][feature]

                # If the statistic is nan, skip this datapoint
                if statistic == None:
                    has_nan = True
                    break

                weather_data_list.append(statistic)

            if has_nan:
                continue

            # Store the inputs
            inputs.append(weather_data_list)

            # Store the outputs
            outputs.append(weather_data_map["default_rating"])

        # Convert to np arrays
        # inputs = np.array(inputs)
        # outputs = np.array(outputs)

        # print(inputs)
        print(type(inputs))

        # Convert to tensors
        inputs = torch.tensor(inputs).to(
            dtype=self.config["base"], device=self.config["device"]
        )
        outputs = torch.tensor(outputs).to(
            dtype=self.config["base"], device=self.config["device"]
        )

        # Create data dictionary
        data["x"] = inputs
        data["y"] = outputs

        return data

    def __len__(self):
        return len(self.data["x"])

    def __getitem__(self, index):
        x = self.data["x"][index]
        y = self.data["y"][index]
        return x, y
