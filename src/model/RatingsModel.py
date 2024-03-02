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
)


class RatingsModel(Module):
    def __init__(self, linear_layers, conv_layers, config):
        super().__init__()

        self.linear_layers = linear_layers

    # Run x through each layer
    def forward(self, x):
        """

        TODO: Add the code to propagate the input through the linear layers!

        """
