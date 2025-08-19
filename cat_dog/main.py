import torch
from config import Config
from data_preparation import DataHandler, prepare_data_loaders
from model import initialize_model
from train import train_model
from evaluate import plot_training_history, visualize_predictions

def main():
    try:
      # Step 1: Prepare data
      print("Step 1: Prepare data")
      DataHandler.download_and_extract(Config.DATA_URL, Config.DATA_DIR)
      
      # Copy sample files (you would call these with your actual paths)
      print("Copy sample files to training")
      DataHandler.copy_random_files("data/PetImages/Cat", Config.TRAIN_DIR, 1000, 'cat')
      DataHandler.copy_random_files("data/PetImages/Dog", Config.TRAIN_DIR, 1000, 'dog')

      # Similar for validation...
      # Copy sample files (you would call these with your actual paths)
      print("Copy sample files to validate")
      DataHandler.copy_random_files("data/PetImages/Cat", Config.VAL_DIR, 1000, 'cat')
      DataHandler.copy_random_files("data/PetImages/Dog", Config.VAL_DIR, 1000, 'dog')
      
      print("prepare_data_loaders")
      train_loader, val_loader = prepare_data_loaders()
      
      # Step 2: Initialize model
      print("Step 2: Initialize model")
      model, criterion, optimizer = initialize_model()
      
      # Step 3: Train model
      print("Step 3: Train model")
      history = train_model(model, train_loader, val_loader, criterion, optimizer)
      
      # Step 4: Save model
      print("Step 4: Save model")
      torch.save(model.state_dict(), Config.MODEL_PATH)
      
      # Step 5: Evaluate
      print("Step 5: Evaluate")
      plot_training_history(history)
      
      # Example predictions
      print("Example predictions")
      test_images = [
          'data/PetImages/Dog/1.jpg',
          'data/PetImages/Cat/1000.jpg'
      ]
      visualize_predictions(test_images, model, Config.get_transform(), Config.DEVICE)
    except Exception as ex:
      print(f"Erro na chamada principal: {str(ex)}")
      
if __name__ == "__main__":
    main()