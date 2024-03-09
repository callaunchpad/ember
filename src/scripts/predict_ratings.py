# # %%

import sys

# append the path of the parent directory
sys.path.append("../dataset")
sys.path.append("../trainer")
sys.path.append("../scripts")
sys.path.append("../utils")
sys.path.append("../model")

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
    Softmax,
)


from torch.optim.lr_scheduler import ReduceLROnPlateau, CyclicLR
import torch.optim as optim

from torch.nn import MSELoss

from RatingsTrainer import RatingsTrainer
from RatingsModel import RatingsModel
from RatingsDataset import RatingsDataset

# Add utils directory to list of directories to search through
from utils import get_device, set_seed, make_dir, split_dataset


set_seed(2023)


# """

# SET CONFIG OBJECT.

# """
config = {
    "PROJECT": "ember_predict_ratings",
    # ------------------- #
    "INPUT_DIR": "../../squamish_data/data.json",
    "INPUT_FEATURES": [
        "temp",
        "humidity",
        "dew",
        "precip",
        "precipprob",
        "snow",
        "snowdepth",
        # "preciptype",
        # "windgust",
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
    "train_pct": 0.90,
    "val_pct": 0.05,
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

# Create the RatingsDataset
dataset = RatingsDataset(config)

# Create data loaders

train_loader, val_loader, test_loader = split_dataset(
    dataset, config["train_pct"], config["val_pct"], config["BATCH_SIZE"], shuffle=True
)


# Define layers for our model
layers = Sequential(
    # Linear(len(config["INPUT_FEATURES"]), 32),
    # ReLU(),
    # Linear(32, 64),
    # ReLU(),
    # Linear(64, 16),
    # ReLU(),
    # Linear(16, 5),
    Linear(len(config["INPUT_FEATURES"]), 5),
    # ReLU(),
    # Softmax(),
)

# Create Model
ratings_model = RatingsModel(layers, config)

# Compile model
ratings_model = ratings_model.to(dtype=config["base"], device=config["device"])

# Error function
criterion = MSELoss().to(dtype=config["base"], device=config["device"])

# Optimizer updates the weights
optimizer = optim.Adam(params=ratings_model.parameters(), lr=config["LEARNING_RATE"])

# Scheduler adjusts the learning rate based on the error
scheduler = ReduceLROnPlateau(
    optimizer,
    factor=config["LR_ADAPT_FACTOR"],
    patience=config["LR_PATIENCE"],
    verbose=True,
)

trainer = RatingsTrainer(
    ratings_model, criterion, optimizer, scheduler, config, train_loader, val_loader
)


print("Starting Training.")


# Start training
trainer.train()
