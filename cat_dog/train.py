import torch
from tqdm import tqdm
from config import Config

def train_epoch(model, loader, criterion, optimizer):
    # Check if GPU is available
    device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
    model = model.to(device)# Step 6: Training Setup

    model.train()
    running_loss = 0.0
    
    for images, labels in tqdm(loader, desc="Training"):
        images = images.to(Config.DEVICE)
        labels = labels.float().unsqueeze(1).to(Config.DEVICE)
        
        optimizer.zero_grad()
        outputs = model(images)
        loss = criterion(outputs, labels)
        loss.backward()
        optimizer.step()
        
        running_loss += loss.item() * images.size(0)
        
    return running_loss / len(loader.dataset)

def validate(model, loader, criterion):
    model.eval()
    val_loss = 0.0
    correct = 0
    
    with torch.no_grad():
        for images, labels in tqdm(loader, desc="Validating"):
            images = images.to(Config.DEVICE)
            labels = labels.float().unsqueeze(1).to(Config.DEVICE)
            
            outputs = model(images)
            val_loss += criterion(outputs, labels).item() * images.size(0)
            correct += ((outputs > 0.5).float() == labels).sum().item()
            
    accuracy = 100 * correct / len(loader.dataset)
    return val_loss / len(loader.dataset), accuracy

def train_model(model, train_loader, val_loader, criterion, optimizer):
    history = {
        'train_loss': [],
        'val_loss': [],
        'val_acc': []
    }
    
    for epoch in range(Config.NUM_EPOCHS):
        print(f"\nEpoch {epoch+1}/{Config.NUM_EPOCHS}")
        
        train_loss = train_epoch(model, train_loader, criterion, optimizer)
        val_loss, val_acc = validate(model, val_loader, criterion)
        
        history['train_loss'].append(train_loss)
        history['val_loss'].append(val_loss)
        history['val_acc'].append(val_acc)
        
        print(f"Train Loss: {train_loss:.4f} | Val Loss: {val_loss:.4f} | Val Acc: {val_acc:.2f}%")
    
    return history