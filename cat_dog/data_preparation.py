import os
import random
import shutil
import urllib.request
import zipfile
import logging
from PIL import Image
import torch
from torch.utils.data import Dataset, DataLoader
from config import Config
import ssl

class DataHandler:
    @staticmethod
    def download_and_extract(url, data_dir):
        ssl._create_default_https_context = ssl._create_unverified_context
        """Downloads and extracts dataset"""
        try:
            os.makedirs(data_dir, exist_ok=True)
            filename = os.path.basename(url)
            filepath = os.path.join(data_dir, filename)
            
            if not os.path.exists(filepath):
                urllib.request.urlretrieve(url, filepath)
            
            if filepath.endswith('.zip'):
                with zipfile.ZipFile(filepath, 'r') as zip_ref:
                    zip_ref.extractall(data_dir)
            
            os.makedirs(os.path.join(data_dir, 'train'), exist_ok=True)
            os.makedirs(os.path.join(data_dir, 'val'), exist_ok=True)
            
        except Exception as e:
            logging.error(f"Data preparation error: {e}")
            raise

    @staticmethod
    def copy_random_files(source, dest, num_files, prefix):
        """Copies random files with prefix"""
        files = [f for f in os.listdir(source) if os.path.isfile(os.path.join(source, f))]
        files = random.sample(files, min(num_files, len(files)))
        
        os.makedirs(dest, exist_ok=True)
        for file in files:
            new_name = f"{prefix}.{file}"
            shutil.copy2(os.path.join(source, file), os.path.join(dest, new_name))

class CatDogDataset(Dataset):
    def __init__(self, root_dir, transform=None):
        self.root_dir = root_dir
        self.transform = transform
        self.images = [f for f in os.listdir(root_dir) 
                      if f.lower().endswith(('.png', '.jpg', '.jpeg', '.bmp', '.gif'))]
        
    def __len__(self):
        return len(self.images)
    
    def __getitem__(self, idx):
        img_name = self.images[idx]
        img_path = os.path.join(self.root_dir, img_name)
        
        try:
            image = Image.open(img_path).convert('RGB')
            label = 0 if 'cat' in img_name.lower() else 1
            
            if self.transform:
                image = self.transform(image)
                
            return image, label
        except Exception as e:
            print(f"Error loading {img_path}: {e}")
            return self.__getitem__(torch.randint(0, len(self)-1, (1,)).item())

def prepare_data_loaders():
    """Prepares and returns train and validation data loaders"""
    transform = Config.get_transform()
    
    train_dataset = CatDogDataset(Config.TRAIN_DIR, transform)
    val_dataset = CatDogDataset(Config.VAL_DIR, transform)
    
    train_loader = DataLoader(train_dataset, batch_size=Config.BATCH_SIZE, shuffle=True)
    val_loader = DataLoader(val_dataset, batch_size=Config.BATCH_SIZE, shuffle=False)
    
    return train_loader, val_loader