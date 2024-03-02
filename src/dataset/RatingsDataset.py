import os
import pickle
from torch.utils.data import Dataset
import torch
import numpy as np
import sys
import json

sys.path.append("../utils")
from utils import normalize


class RatingsDataset(Dataset):
    """Dataset for the full simulations of healpix data."""

    def __init__(self, config, transform=None):
        self.input_features = config["INPUT_FEATURES"]

        input_dir = config["INPUT_DIR"]

        with open(input_dir) as f:
            image_dict = json.load(f)

        # Convert image dict to only store necessary features. Also convert weather statistics to be stored in a list instead of a map.
        new_image_dict = self.convert_image_dict_weather_data_to_lists(image_dict)
        self.image_dict = new_image_dict

        # Stores image filepaths (the keys in data.json)
        self.data_paths = list(self.image_dict.keys())

        self.input_dir = input_dir
        self.transform = transform
        self.config = config
        self.normalize = config["NORMALIZE"]

    def convert_image_dict_weather_data_to_lists(self, image_dict):
        new_image_dict = {}

        # Go through each image path in the image_dict
        for image_path, weather_data_map in image_dict.items():
            weather_data_list = []

            for feature in self.input_features:
                statistic = image_dict[image_path][feature]
                weather_data_list.append(statistic)

            new_image_dict[image_path] = weather_data_list

        return new_image_dict

    def __len__(self):
        return len(self.data_paths)

    def __getitem__(self, index):
        # Open the file at the given index
        f = open(self.data_paths[index], "rb")
        data = pickle.load(f)
        f.close()

        # Normalize y if needed
        if self.normalize:
            for i in range(len(data["y"])):
                cross_sec = data["y"][i]

                normalized_cross_sec = normalize(cross_sec)

                # Update data
                data["y"][i] = normalized_cross_sec

        # Transform if needed
        if self.transform:
            data = self.transform(data)

        x = data["x"]
        y = data["y"]

        # Convert to tensors
        x = torch.tensor(x).to(dtype=self.config["base"], device=self.config["device"])
        y = torch.tensor(y).to(dtype=self.config["base"], device=self.config["device"])

        return x, y
