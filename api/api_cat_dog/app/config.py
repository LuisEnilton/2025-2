import torch
from torchvision import transforms
import os

class Config:
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    IMAGE_SIZE = (224, 224)
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]
    MODEL_PATH = os.path.join(os.path.dirname(__file__), "cat_dog_classifier.pth")
    THRESHOLD = 0.5  # Limiar para classificação
    UNCERTAIN_THRESHOLD = 0.3  # Se a probabilidade estiver entre 0.3-0.7, considera incerto

    @staticmethod
    def get_transform():
        return transforms.Compose([
            transforms.Resize(Config.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=Config.MEAN, std=Config.STD)
        ])
