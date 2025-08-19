import torch
import matplotlib.pyplot as plt
from PIL import Image

def predict_image(image_path, model, transform, device):
    """Predicts whether image is cat or dog"""
    try:
        image = Image.open(image_path).convert('RGB')
        image = transform(image).unsqueeze(0).to(device)
        
        model.eval()
        with torch.no_grad():
            output = model(image)
            prob = output.item()
            pred = 'dog' if prob > 0.5 else 'cat'
            
        return pred, prob
    except Exception as e:
        print(f"Prediction error: {e}")
        return None, None

def visualize_predictions(image_paths, model, transform, device):
    """Visualizes predictions for multiple images"""
    plt.figure(figsize=(15, 10))
    for i, path in enumerate(image_paths):
        image = Image.open(path).convert('RGB')
        pred, prob = predict_image(path, model, transform, device)
        
        plt.subplot(2, 3, i+1)
        plt.imshow(image)
        plt.title(f"{pred} ({prob:.2f})")
        plt.axis('off')
    plt.show()

def plot_training_history(history):
    """Plots training and validation metrics"""
    plt.figure(figsize=(12, 5))
    
    plt.subplot(1, 2, 1)
    plt.plot(history['train_loss'], label='Train Loss')
    plt.plot(history['val_loss'], label='Val Loss')
    plt.legend()
    plt.title('Loss')
    
    plt.subplot(1, 2, 2)
    plt.plot(history['val_acc'], label='Val Accuracy')
    plt.legend()
    plt.title('Accuracy')
    
    plt.show()