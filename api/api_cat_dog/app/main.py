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
