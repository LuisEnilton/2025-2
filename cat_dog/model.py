import torch
import torch.nn as nn
import torchvision.models as models
import torch.optim as optim
from config import Config

class CatDogClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.model = models.resnet18(pretrained=True)
        
        # Freeze layers
        for param in self.model.parameters():
            param.requires_grad = False
            
        # Replace final layer
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 1)
        
    def forward(self, x):
        return torch.sigmoid(self.model(x))

def initialize_model():
    """Initializes model, criterion and optimizer"""
    model = CatDogClassifier().to(Config.DEVICE)
    criterion = nn.BCELoss()
    optimizer = optim.Adam(model.parameters(), lr=Config.LEARNING_RATE)
    return model, criterion, optimizer