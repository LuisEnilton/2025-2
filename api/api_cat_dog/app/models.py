import torch
import torch.nn as nn
from torchvision import models
from app.config import Config

class CatDogClassifier(nn.Module):
    def __init__(self):
        super(CatDogClassifier, self).__init__()
        # Carrega o ResNet18 pré-treinado
        self.model = models.resnet18(pretrained=True)
        
        # Congela todos os parâmetros
        for param in self.model.parameters():
            param.requires_grad = False
        
        # Substitui a última camada para classificação binária
        num_features = self.model.fc.in_features
        self.model.fc = nn.Linear(num_features, 1)
        
        # Função de ativação sigmoid para classificação binária
        self.sigmoid = nn.Sigmoid()
    
    def forward(self, x):
        x = self.model(x)
        return self.sigmoid(x)

# Função para carregar o modelo
def load_model():
    model = CatDogClassifier()
    model.load_state_dict(torch.load(Config.MODEL_PATH, map_location=Config.DEVICE))
    model.to(Config.DEVICE)
    model.eval()
    return model
