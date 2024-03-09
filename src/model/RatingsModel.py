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
    def __init__(self, layers, config):
        super().__init__()

        self.layers = layers
        self.config = config

    # Run x through each layer
    def forward(self, x):
        """

        TODO: Add the code to propagate the input through the linear layers!

        """

        for layer in self.layers:
            x = layer(x)

        return x
