#!/bin/bash

# Script para criar a estrutura do projeto CatDog Classifier no macOS Sequoia
# Execute com: chmod +x setup_project.sh && ./setup_project.sh

set -e  # Para o script se encontrar algum erro

echo "🐾 Iniciando criação do projeto CatDog Classifier..."
echo "====================================================="

# Nome do projeto
PROJECT_DIR="api_cat_dog"

# Criar diretório principal
echo "📁 Criando diretório principal: $PROJECT_DIR"
mkdir -p "$PROJECT_DIR"
cd "$PROJECT_DIR"

# Criar subdiretórios
echo "📁 Criando estrutura de pastas..."
mkdir -p app uploads

echo "✅ Estrutura de pastas criada:"
find . -type d -print | sed -e 's;[^/]*/;|____;g;s;____|; |;g'

# Criar arquivos na pasta app
echo "📝 Criando arquivos..."

# Arquivo requirements.txt
cat > app/requirements.txt << 'EOF'
fastapi==0.104.1
uvicorn==0.24.0
python-multipart==0.0.6
torch==2.1.0
torchvision==0.16.0
pillow==10.1.0
aiofiles==23.2.1
EOF

# Arquivo config.py
cat > app/config.py << 'EOF'
import torch
from torchvision import transforms

class Config:
    DEVICE = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    IMAGE_SIZE = (224, 224)
    MEAN = [0.485, 0.456, 0.406]
    STD = [0.229, 0.224, 0.225]
    MODEL_PATH = "cat_dog_classifier.pth"
    THRESHOLD = 0.5  # Limiar para classificação
    UNCERTAIN_THRESHOLD = 0.3  # Se a probabilidade estiver entre 0.3-0.7, considera incerto

    @staticmethod
    def get_transform():
        return transforms.Compose([
            transforms.Resize(Config.IMAGE_SIZE),
            transforms.ToTensor(),
            transforms.Normalize(mean=Config.MEAN, std=Config.STD)
        ])
EOF

# Arquivo models.py
cat > app/models.py << 'EOF'
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
EOF

# Arquivo database.py
cat > app/database.py << 'EOF'
import sqlite3
import datetime
from typing import List, Dict, Any

class Database:
    def __init__(self, db_path: str = "predictions.db"):
        self.db_path = db_path
        self.init_db()
    
    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS predictions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                filename TEXT NOT NULL,
                prediction TEXT NOT NULL,
                confidence REAL NOT NULL,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        conn.commit()
        conn.close()
    
    def save_prediction(self, filename: str, prediction: str, confidence: float):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO predictions (filename, prediction, confidence)
            VALUES (?, ?, ?)
        ''', (filename, prediction, confidence))
        conn.commit()
        conn.close()
    
    def get_recent_predictions(self, limit: int = 10) -> List[Dict[str, Any]]:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()
        cursor.execute('''
            SELECT * FROM predictions 
            ORDER BY timestamp DESC 
            LIMIT ?
        ''', (limit,))
        rows = cursor.fetchall()
        conn.close()
        return [dict(row) for row in rows]
EOF

# Arquivo main.py
cat > app/main.py << 'EOF'
from fastapi import FastAPI, File, UploadFile, HTTPException
from fastapi.responses import JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import torch
from PIL import Image
import io
import os
from typing import Dict, Any

from app.models import load_model
from app.config import Config
from app.database import Database

app = FastAPI(title="CatDog Classifier API", version="1.0.0")

# Configura CORS para permitir todas as origens
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Cria diretório de uploads se não existir
os.makedirs("uploads", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Carrega o modelo uma vez ao iniciar a aplicação
model = None
transform = Config.get_transform()
db = Database()

@app.on_event("startup")
async def startup_event():
    global model
    try:
        model = load_model()
        print("✅ Modelo carregado com sucesso!")
    except Exception as e:
        print(f"❌ Erro ao carregar modelo: {e}")
        raise e

def predict_image(image: Image.Image) -> Dict[str, Any]:
    """Faz a predição em uma imagem"""
    try:
        # Aplica as transformações
        image_tensor = transform(image).unsqueeze(0).to(Config.DEVICE)
        
        # Faz a predição
        with torch.no_grad():
            output = model(image_tensor)
            confidence = output.item()
        
        # Determina a classe baseado no threshold
        if confidence > Config.THRESHOLD:
            prediction = "dog"
            final_confidence = confidence
        elif confidence < (1 - Config.THRESHOLD):
            prediction = "cat"
            final_confidence = 1 - confidence
        else:
            prediction = "uncertain"
            final_confidence = abs(confidence - 0.5) * 2  # Normaliza para 0-1
        
        return {
            "prediction": prediction,
            "confidence": round(final_confidence, 4),
            "raw_output": round(confidence, 4)
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro na predição: {str(e)}")

@app.post("/predict/", response_model=Dict[str, Any])
async def predict(file: UploadFile = File(...)):
    """Endpoint para fazer predição de uma imagem"""
    # Verifica se o arquivo é uma imagem
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="Arquivo deve ser uma imagem")
    
    try:
        # Lê a imagem
        contents = await file.read()
        image = Image.open(io.BytesIO(contents)).convert('RGB')
        
        # Faz a predição
        result = predict_image(image)
        
        # Salva a imagem no diretório de uploads
        filename = f"{os.urandom(8).hex()}_{file.filename}"
        file_path = os.path.join("uploads", filename)
        image.save(file_path)
        
        # Salva no banco de dados
        db.save_prediction(filename, result["prediction"], result["confidence"])
        
        return JSONResponse(content={
            "filename": filename,
            "prediction": result["prediction"],
            "confidence": result["confidence"],
            "message": get_prediction_message(result["prediction"]),
            "image_url": f"/uploads/{filename}"
        })
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erro ao processar imagem: {str(e)}")

@app.get("/predictions/recent/")
async def get_recent_predictions(limit: int = 10):
    """Retorna as predições recentes"""
    predictions = db.get_recent_predictions(limit)
    return {"predictions": predictions}

@app.get("/health/")
async def health_check():
    """Endpoint de health check"""
    return {
        "status": "healthy",
        "model_loaded": model is not None,
        "device": str(Config.DEVICE)
    }

def get_prediction_message(prediction: str) -> str:
    """Retorna mensagem amigável baseada na predição"""
    messages = {
        "dog": "✅ Esta é uma imagem de um cachorro!",
        "cat": "✅ Esta é uma imagem de um gato!",
        "uncertain": "❓ Não tenho certeza se é um cachorro ou gato. Tente com uma imagem mais clara."
    }
    return messages.get(prediction, "❓ Não foi possível classificar a imagem.")

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
EOF

# Criar arquivo .pth vazio (placeholder)
echo "🔧 Criando arquivo de modelo vazio (substitua com seu modelo treinado)"
touch "app/cat_dog_classifier.pth"

# Criar arquivo README.md
cat > README.md << 'EOF'
# CatDog Classifier API

API FastAPI para classificação de imagens de gatos e cachorros usando PyTorch.

## Estrutura do Projeto

api_cat_dog/
│
├── app/
│   ├── main.py
│   ├── models.py
│   ├── config.py
│   ├── cat_dog_classifier.pth
│   └── requirements.txt
│
└── uploads/
EOF