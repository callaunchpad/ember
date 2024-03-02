# # %%

import sys
import torch

import pickle
import numpy as np
import platform

from torch.nn import (
    Module,
    Conv2d,
    Sequential,
    ConvTranspose2d,
    ReLU,
    MaxPool2d,
    Linear,
    Conv3d,
    Tanh,
    Dropout,
    DataParallel,
    BatchNorm2d,
)


from torch.optim.lr_scheduler import ReduceLROnPlateau, CyclicLR
import torch.optim as optim

from torch.nn import MSELoss

from trainer import RatingsTrainer
from model import RatingsModel
from dataset import RatingsDataset

# Add utils directory to list of directories to search through
from utils import get_device, set_seed, make_dir, save_img, split_dataset


set_seed(2023)


# """

# SET CONFIG OBJECT.

# """
config = {
    "PROJECT": "ember_predict_ratings",
    # ------------------- #
    "INPUT_DIR": "../../squamish-data/data.json",
    "INPUT_FEATURES": [
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
    ],
    # ------------------- #
    # "SHOW_IMAGES": True,
    "NORMALIZE": False,
    # ------------------- #
    "DEPTH": 18,  # 180 / compton_bin_size
    "train_pct": 0.95,
    "val_pct": 0.04,
    "BATCH_SIZE": 16,
    # ------------------- #
    "EPOCHS": 500,
    "PATIENCE": 40,
    "LEARNING_RATE": 0.01,
    # ------------------- #
    "LR_PATIENCE": 12,
    "LR_ADAPT_FACTOR": 0.5,
    # ------------------- #
    "base": torch.float32,
    "device": get_device(),
    "system": platform.system(),
    # # ------------------- #
    # "SAVE_IMAGES": True,
    # "IMAGES_SAVE_DIR": "../../logs/saved-images/",
    # "IMAGES_SAVE_INTERVAL": 10,
    # # ------------------- #
}

print("Starting Training.")
