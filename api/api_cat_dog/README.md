# CatDog Classifier API

API FastAPI para classificação de imagens de gatos e cachorros usando PyTorch. 

Mais detalhes em [projeto.md](projeto.md)

## Estrutura do Projeto

```bash
api_cat_dog
├── app
│   ├── main.py
│   ├── models.py
│   ├── config.py
│   ├── cat_dog_classifier.pth
│   └── requirements.txt
└── uploads
```

## Como Executar

### 1. Preparação do ambiente virtual 

```bash
python3 -m venv venv
```

```bash
source venv/bin/activate
```

### 2. Instale as dependências:

```bash
pip3 install -r requirements.txt
```

### 3. Certifique-se que o arquivo `cat_dog_classifier.pth` está na pasta app/

### 4. Execute a API:

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Como Usar a API

### 1. Via Interface Web
Acesse: `http://localhost:8000/docs` para ver a documentação interativa Swagger.

### 2. Via curl

```bash
curl -X POST "http://localhost:8000/predict/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@cachorro_teste.png"

{"filename":"5fc91a444704a551_cachorro_teste.png","prediction":"dog","confidence":0.998,"message":"✅ Esta é uma imagem de um cachorro!","image_url":"/uploads/5fc91a444704a551_cachorro_teste.png"}

curl -X POST "http://localhost:8000/predict/" \
     -H "accept: application/json" \
     -H "Content-Type: multipart/form-data" \
     -F "file=@gato_teste.png"

{"filename":"ff267ab884eabc30_gato_teste.png","prediction":"cat","confidence":0.9938,"message":"✅ Esta é uma imagem de um gato!","image_url":"/uploads/ff267ab884eabc30_gato_teste.png"}%
```

### 3. Via Python requests

```python
import requests

url = "http://localhost:8000/predict/"
files = {"file": open("seu_gato.jpg", "rb")}
response = requests.post(url, files=files)
print(response.json())
```

## Exemplo de Resposta

```json
{
  "filename": "a1b2c3d4e5_seu_gato.jpg",
  "prediction": "cat",
  "confidence": 0.9785,
  "message": "✅ Esta é uma imagem de um gato!",
  "image_url": "/uploads/a1b2c3d4e5_seu_gato.jpg"
}
```