import torch
import math
import os
import wandb
import numpy as np


class RatingsTrainer:
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

        # Store how many ratings were predicted correctly
        num_correct_rating = 0

        for x, y in self.train_loader:  # x is data, y is label
            torch.cuda.empty_cache()

            # Zero the gradients
            self.optimizer.zero_grad()

            # Get outputs
            pred = self.model(x)

            # print("---> inputs: ", x)
            # print("---> outputs: ", outputs)

            # Calculate loss
            curr_loss = self.criterion(pred, y)

            # Calculate the gradients
            curr_loss.backward()

            # Do gradient descent to update weights.
            self.optimizer.step()

            # Update running loss variable
            running_loss += (
                curr_loss.item() * pred.shape[0]
            )  # curr_loss.item = curr_loss / batch_size. multiply by batch_size to get actual curr_loss for this batch.

            # Update how many ratings were correct only if you're doing one hot encoding
            if self.config["ONE_HOT_ENCODING"]:
                num_correct_rating += self.calc_num_correct_ratings(pred, y)

        # Calculate accuracy
        num_datapoints = len(self.train_loader.dataset)
        train_acc = num_correct_rating / num_datapoints

        return running_loss, train_acc

    def train(self):
        # Initialize wandb
        self.init_wandb()

        v_loss = self.validate()

        # Print train and val loss before any training.
        print(f"Before any training, Val Loss: {v_loss}")
        print()

        EPOCHS = self.config["EPOCHS"]
        curr_epoch = 0

        while curr_epoch < EPOCHS:
            # Get loss for this epoch
            curr_loss, train_acc = self.train_epoch()

            val_loss, val_acc = self.validate()

            print(f"Epoch: {curr_epoch} Train Loss: {curr_loss} Val Loss: {val_loss}")

            # Empty cache
            torch.cuda.empty_cache()

            # Step scheduler
            self.scheduler.step(val_loss)

            # Increment epoch
            curr_epoch += 1

            # Log metrics
            wandb.log(
                {
                    "epoch": curr_epoch,
                    "learning_rate": self.optimizer.param_groups[0]["lr"],
                    "train_loss": curr_loss,
                    "train_acc": train_acc,
                    "val_loss": val_loss,
                    "val_acc": val_acc,
                }
            )

        # Create heatmap for both training loader
        self.create_charts(self.train_loader, "train_heatmap", "train_roc")
        self.create_charts(self.val_loader, "val_heatmap", "val_roc")

        pass

    def validate(self):
        model = self.model
        val_loader = self.val_loader

        # Store how many ratings were predicted correctly
        num_correct_rating = 0

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

                # Update how many ratings were correct only if you're doing one hot encoding
                if self.config["ONE_HOT_ENCODING"]:
                    num_correct_rating += self.calc_num_correct_ratings(pred, y_val)

        # Revert to training mode
        model.train()

        # Calculate accuracy
        num_datapoints = len(self.val_loader.dataset)
        val_acc = num_correct_rating / num_datapoints

        # Return our validation loss
        return running_val_loss, val_acc

    def calc_num_correct_ratings(self, predicted_batch, actual_batch):
        num_correct = 0

        batch_list_pred = predicted_batch.tolist()
        batch_list_truth = actual_batch.tolist()

        for i in range(len(batch_list_pred)):
            # pred  and truth are both  lists of 5 values (neurons).
            pred, truth = batch_list_pred[i], batch_list_truth[i]
            pred_rating = pred.index(max(pred)) + 1
            truth_rating = truth.index(max(truth)) + 1

            if pred_rating == truth_rating:
                num_correct += 1

        return num_correct

    # Creates heatmaps and ROC curve
    def create_charts(self, loader, heatmap_name, roc_curve_name):
        model = self.model

        # Set model to validation mode to conserve memory - when in validation mode, gradient's arent calculated
        model.eval()

        # Store predictions and truths across all the batches
        total_pred = []
        total_truth = []

        # Stores all 5 output neurons
        full_prediction_probabilities = []

        # Ensure no gradients involved
        with torch.no_grad():
            running_val_loss = 0.0

            for x_val, y_val in loader:
                # Calculate validation prediction
                pred = model(x_val)

                batch_list_pred = pred.tolist()
                batch_list_truth = y_val.tolist()

                for i in range(len(batch_list_pred)):
                    list_pred, list_truth = batch_list_pred[i], batch_list_truth[i]
                    pred_rating = list_pred.index(
                        max(list_pred)
                    )  # for some reason i need to keep these starting at 0? instead of 1...
                    truth_rating = list_truth.index(max(list_truth))

                    total_pred.append(pred_rating)
                    total_truth.append(truth_rating)

                    full_prediction_probabilities.append(
                        list_pred
                    )  # Concatenate this set of outputs to the full prediction probabilities array

                    # print(f"----> Prediction: {pred} Ground Truth: {y_val}")
                    # print(f"----> Prediction: {pred_rating} Truth: {truth_rating}")

        # Rever to training mode
        model.train()

        class_names = [1, 2, 3, 4, 5]

        # Save heatmap
        wandb.log(
            {
                heatmap_name: wandb.plot.confusion_matrix(
                    preds=total_pred,
                    y_true=total_truth,
                    class_names=class_names,
                )
            }
        )

        # ROC curves need the data in the following format
        # Total truth is just an array of all the actual classes in integer form like [1, 2, 3, 4, 2, 1, ...]
        # Full prediction probabilities is the probability of each class for each data point like [[0.9, 0.1, 0.05, 0.05, 0.02], ...]
        # Question: do the probabilities need to sum to 1? If so I will have to add that
        wandb.log(
            {
                roc_curve_name: wandb.plot.roc_curve(
                    total_truth,
                    full_prediction_probabilities,
                    labels=class_names,
                )
            }
        )
