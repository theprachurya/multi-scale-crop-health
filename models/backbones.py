import torch
import torch.nn as nn
from torchvision.models import resnet50, ResNet50_Weights, efficientnet_b0, EfficientNet_B0_Weights

class ResNet50Backbone(nn.Module):
    def __init__(self, pretrained=True, freeze_layers=True):
        super().__init__()
        weights = ResNet50_Weights.IMAGENET1K_V1 if pretrained else None
        resnet = resnet50(weights=weights)
        
        # Keep up to avgpool, remove fc
        self.features = nn.Sequential(*list(resnet.children())[:-1])
        self.out_dim = 2048
        
        if freeze_layers:
            for param in self.features.parameters():
                param.requires_grad = False
            # In the Sequential layout, index 7 corresponds to ResNet layer4.
            for param in self.features[7].parameters():
                param.requires_grad = True

    def forward(self, x):
        x = self.features(x)
        x = torch.flatten(x, 1) # GAP creates (batch, 2048, 1, 1), flatten gives (batch, 2048)
        return x

class EfficientNetB0Backbone(nn.Module):
    def __init__(self, pretrained=True, freeze_layers=True):
        super().__init__()
        weights = EfficientNet_B0_Weights.IMAGENET1K_V1 if pretrained else None
        effnet = efficientnet_b0(weights=weights)
        
        self.features = effnet.features
        self.avgpool = nn.AdaptiveAvgPool2d(1)
        self.out_dim = 1280
        
        if freeze_layers:
            # Freeze features.0 through features.6, train features.7 and 8
            for i, child in enumerate(self.features.children()):
                if i < 7:
                    for param in child.parameters():
                        param.requires_grad = False
                else:
                    for param in child.parameters():
                        param.requires_grad = True

    def forward(self, x):
        x = self.features(x)
        x = self.avgpool(x)
        x = torch.flatten(x, 1) # (batch, 1280)
        return x
