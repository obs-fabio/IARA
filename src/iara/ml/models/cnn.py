import typing
import torch

import iara.ml.models.base_model as iara_model
import iara.ml.models.mlp as iara_mlp

class CNN(iara_model.BaseModel):

    def __init__(self,
                 input_shape: typing.Iterable[int],
                 conv_n_neurons: typing.List[int],
                 classification_n_neurons: int,
                 conv_activation: torch.nn.Module = torch.nn.LeakyReLU(),
                 conv_pooling: torch.nn.Module = torch.nn.MaxPool2d(2, 2),
                 back_norm: bool = True,
                 kernel_size: int = 5,
                 padding: int = 2,
                 n_targets: int = 1,
                 classification_hidden_activation: torch.nn.Module = None,
                 classification_output_activation: torch.nn.Module = torch.nn.Sigmoid()):
        super().__init__()

        classification_hidden_activation = conv_activation if classification_hidden_activation is None else classification_hidden_activation

        if len(input_shape) != 3:
            raise UnboundLocalError("CNN expects as input an image in the format: \
                                    channel x width x height")

        self.input_shape = input_shape

        conv_layers = []
        conv = [self.input_shape[0]]
        conv.extend(conv_n_neurons)

        for i in range(1, len(conv)):
            conv_layers.append(torch.nn.Conv2d(conv[i - 1], conv[i],
                                               kernel_size=kernel_size, padding=padding))
            if back_norm:
                conv_layers.append(torch.nn.BatchNorm2d(conv[i]))
            conv_layers.append(conv_activation)
            conv_layers.append(conv_pooling)

        self.conv_layers = torch.nn.Sequential(*conv_layers)

        test_shape = [1]
        test_shape.extend(input_shape)
        test_tensor = torch.rand(test_shape, dtype=torch.float32)
        test_tensor = self.to_feature_space(test_tensor)

        self.mlp = iara_mlp.MLP(input_shape = test_tensor.shape,
                                n_neurons = classification_n_neurons,
                                n_targets = n_targets,
                                activation_hidden_layer = classification_hidden_activation,
                                activation_output_layer = classification_output_activation)


    def to_feature_space(self, data: torch.Tensor) -> torch.Tensor:
        return self.conv_layers(data)


    def forward(self, data: torch.Tensor) -> torch.Tensor:
        data = self.to_feature_space(data)
        data = self.mlp(data)
        return data

    def __str__(self) -> str:
        """
        Return a string representation of the model.

        Returns:
            str: A string containing the name of the model class.
        """
        return f'{super().__str__()} ------- \n' + f'{str(self.conv_layers)}\n' + f'{str(self.mlp)}'
