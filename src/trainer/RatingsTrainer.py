import torch
import math
import os
import wandb
import numpy as np


class Trainer:
    def __init__(
        self, model, criterion, optimizer, scheduler, config, train_loader, val_loader
    ):
        self.model = model
        self.criterion = criterion
        self.optimizer = optimizer
        self.scheduler = scheduler

        self.config = config

        self.train_loader = train_loader
        self.val_loader = val_loader

        self.train_loss_hist = []
        self.val_loss_hist = []

        self.curr_lr = config["LEARNING_RATE"]

        self.epoch = 0

    def init_wandb(self):
        # wandb.login(key=os.environ.)

        wandb.init(
            # set the wandb project where this run will be logged
            project=self.config["PROJECT"],
            # track hyperparameters and run metadata
            config=self.config,
        )

        # Save model architecture as a temporary file to upload to wandb
        file = open(os.path.join(wandb.run.dir, "model_arch.txt"), "w")
        file.write(str(self.model))
        file.close()

        wandb.save(os.path.join(wandb.run.dir, "model_arch.txt"))

        # If saving images for logging, update image subdirectory with name of this run
        if self.config["SAVE_IMAGES"]:
            self.config["IMAGES_SAVE_DIR"] = os.path.join(
                self.config["IMAGES_SAVE_DIR"], wandb.run.name
            )

            # Create the directory
            os.mkdir(self.config["IMAGES_SAVE_DIR"])

        # Store scheduler and optimizer type
        scheduler_string = str(self.scheduler)
        scheduler_params = self.scheduler.state_dict()
        scheduler_string_with_params = (
            f"{scheduler_string}\nParameters: {scheduler_params}"
        )

        self.config["scheduler"] = scheduler_string_with_params
        self.config["optimizer"] = str(self.optimizer)

    def train_epoch(self):
        running_loss = 0.0

        for x, y in self.train_loader:  # x is data, y is label
            # Zero the gradients
            self.optimizer.zero_grad()

            # Get outputs
            outputs = self.model(x)

            # Calculate loss
            curr_loss = self.criterion(outputs, y)

            # Calculate the gradients
            curr_loss.backward()

            # Do gradient descent to update weights.
            self.optimizer.step()

            # Update running loss variable
            running_loss += (
                curr_loss.item() * outputs.shape[0]
            )  # curr_loss.item = curr_loss / batch_size. multiply by batch_size to get actual curr_loss for this batch.

        return running_loss

    def train(self):
        # Initialize wandb
        self.init_wandb()

        EPOCHS = self.config["EPOCHS"]
        curr_epoch = 0

        while curr_epoch < EPOCHS:
            # Get loss for this epoch
            curr_loss = self.train_epoch()

            val_loss = self.validate()

            # Empty cache
            torch.cuda.empty_cache()

            # Step scheduler
            self.scheduler.step(val_loss)

            # Increment epoch
            curr_epoch += 1

        pass

    def validate(self):
        model = self.model
        val_loader = self.val_loader

        # Set model to validation mode to conserve memory - when in validation mode, gradient's arent calculated
        model.eval()

        # Ensure no gradients involved
        with torch.no_grad():
            running_val_loss = 0.0

            for x_val, y_val in val_loader:
                # Calculate validation prediction
                pred = model(x_val)

                # Calculate current validation loss
                curr_loss = self.criterion(pred, y_val)

                # Update running validation loss
                running_val_loss += curr_loss.item() * pred.shape[0]

        # Rever to training mode
        model.train()

        # Return our validation loss
        return running_val_loss
