import torch.nn as nn

class ClassificationHead(nn.Module):
    def __init__(self, input_dim: int, num_classes: int = 3, dropout_rate: float = 0.5):
        super().__init__()
        # Architecture: input_dim -> 1024 -> 256 -> num_classes
        self.net = nn.Sequential(
            nn.Linear(input_dim, 1024),
            nn.BatchNorm1d(1024),
            nn.ReLU(inplace=True),
            nn.Dropout(p=dropout_rate), # 0.5 expected
            
            nn.Linear(1024, 256),
            nn.BatchNorm1d(256),
            nn.ReLU(inplace=True),
            nn.Dropout(p=0.3), # 0.3 expected based on instructions
            
            nn.Linear(256, num_classes)
        )
        
        # Weight initialization (Kaiming He)
        self._initialize_weights()

    def _initialize_weights(self):
        for m in self.modules():
            if isinstance(m, nn.Linear):
                nn.init.kaiming_normal_(m.weight, mode='fan_in', nonlinearity='relu')
                if m.bias is not None:
                    nn.init.constant_(m.bias, 0)
            elif isinstance(m, nn.BatchNorm1d):
                nn.init.constant_(m.weight, 1)
                nn.init.constant_(m.bias, 0)

    def forward(self, x):
        return self.net(x)
