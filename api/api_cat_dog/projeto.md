# Projeto API manipula modelo CatDogClassifier

## Arquivo requirements.txt

O arquivo requirements.txt lista as dependências do seu projeto Python. Cada linha especifica um pacote e sua versão exata. Aqui está o que cada pacote faz:

- **fastapi==0.104.1**: Framework para criar APIs web rápidas e assíncronas.
- **uvicorn==0.24.0**: Servidor ASGI usado para rodar aplicações FastAPI.
- **python-multipart==0.0.6**: Suporte para upload de arquivos em requisições HTTP.
- **torch==2.1.0**: Biblioteca para computação científica e aprendizado de máquina (PyTorch).
- **torchvision==0.16.0**: Extensão do PyTorch para tarefas de visão computacional.
- **pillow==10.1.0**: Biblioteca para manipulação de imagens em Python.
- **aiofiles==23.2.1**: Permite operações assíncronas com arquivos.

Esses pacotes são necessários para rodar e desenvolver sua API, especialmente se ela envolve processamento de imagens e aprendizado de máquina.

## Arquivo config.py

O arquivo config.py define configurações e utilitários para o seu projeto de classificação de imagens (gatos e cachorros):

- **Importações**: Usa `torch` para computação e `transforms` do `torchvision` para pré-processamento de imagens.
- **Classe Config**: Centraliza parâmetros importantes:
  - `DEVICE`: Define se o código usará GPU (`cuda`) ou CPU, dependendo da disponibilidade.
  - `IMAGE_SIZE`: Tamanho para redimensionar as imagens (224x224 pixels).
  - `MEAN` e `STD`: Valores usados para normalizar as imagens, padrão de modelos pré-treinados.
  - `MODEL_PATH`: Caminho do arquivo do modelo treinado.
  - `THRESHOLD`: Limiar para decidir entre gato/cachorro.
  - `UNCERTAIN_THRESHOLD`: Se a probabilidade estiver entre 0.3 e 0.7, a classificação é considerada incerta.
- **get_transform()**: Método estático que retorna uma sequência de transformações para preparar a imagem: redimensiona, converte para tensor e normaliza.

Essas configurações ajudam a manter o código organizado e fácil de ajustar.

## Arquivo database.py

O arquivo database.py implementa uma classe para gerenciar um banco de dados SQLite que armazena previsões feitas pelo modelo. Veja o que cada parte faz:

- **Importações**: Usa `sqlite3` para o banco de dados, `datetime` para manipulação de datas (embora não seja usado diretamente), e tipos do módulo `typing` para anotações.

- **Classe Database**:
  - **__init__**: Inicializa o caminho do banco de dados (padrão: `predictions.db`) e chama `init_db()` para garantir que a tabela existe.
  - **init_db**: Cria a tabela `predictions` se ela não existir, com campos para id, nome do arquivo, previsão, confiança e timestamp.
  - **save_prediction**: Insere uma nova previsão na tabela, incluindo nome do arquivo, resultado da previsão e confiança.
  - **get_recent_predictions**: Busca as últimas previsões (padrão: 10), ordenadas por timestamp decrescente, e retorna como uma lista de dicionários.

Essa classe facilita salvar e consultar previsões feitas pelo seu modelo de classificação de imagens.

## Arquivo models.py

O arquivo models.py define o modelo de classificação de imagens (gato/cachorro) usando PyTorch e ResNet18. Veja o que cada parte faz:

- **Importações**: Usa PyTorch, módulos de rede neural, modelos pré-treinados do torchvision e configurações do projeto.

- **Classe CatDogClassifier**:
  - Herda de `nn.Module`.
  - Carrega o modelo ResNet18 pré-treinado.
  - Congela os parâmetros do modelo (não serão ajustados durante o treinamento).
  - Substitui a última camada totalmente conectada (`fc`) para produzir uma saída (classificação binária).
  - Adiciona uma função de ativação sigmoid para converter a saída em probabilidade (entre 0 e 1).

- **forward**: Define o fluxo de dados pelo modelo, aplicando a sigmoid na saída.

- **Função load_model**:
  - Instancia o modelo.
  - Carrega os pesos salvos do arquivo definido em `Config.MODEL_PATH`.
  - Move o modelo para o dispositivo correto (CPU ou GPU).
  - Coloca o modelo em modo de avaliação (`eval()`).
  - Retorna o modelo pronto para inferência.

Esse arquivo prepara e carrega o modelo para fazer previsões de gato ou cachorro em imagens.

## Arquivo main.py

O arquivo main.py implementa a API principal usando FastAPI para classificar imagens de gatos e cachorros. Veja o que cada parte faz:

### Importações
- **FastAPI**: Framework para criar APIs web.
- **UploadFile, File, HTTPException**: Para upload e validação de arquivos.
- **JSONResponse, StaticFiles, CORSMiddleware**: Para respostas, servir arquivos estáticos e configurar CORS.
- **torch, PIL, io, os**: Para manipulação de imagens e arquivos.
- **app.models, app.config, app.database**: Importa funções e classes do projeto.

### Configuração da API
- Cria a instância do FastAPI.
- Configura CORS para permitir requisições de qualquer origem.
- Cria o diretório uploads para salvar imagens enviadas.
- Monta o diretório de uploads como arquivos estáticos.

### Inicialização
- Carrega o modelo de classificação e as transformações de imagem.
- Inicializa o banco de dados.

### Eventos
- No evento de startup, carrega o modelo treinado.

### Função de Predição
- **predict_image**: Recebe uma imagem, aplica transformações, faz a predição com o modelo, determina a classe (gato, cachorro ou incerto) e retorna o resultado.

### Endpoints
- **POST /predict/**: Recebe uma imagem, faz a predição, salva a imagem e o resultado no banco de dados, e retorna as informações.
- **GET /predictions/recent/**: Retorna as últimas predições salvas no banco de dados.
- **GET /health/**: Endpoint para verificar se a API e o modelo estão funcionando.

### Utilitário
- **get_prediction_message**: Retorna uma mensagem amigável baseada no resultado da predição.

### Execução
- Se rodar como script, inicia o servidor Uvicorn na porta 8000.

**Resumo:**  
Este arquivo expõe uma API REST que recebe imagens, classifica como gato/cachorro/incerto, salva resultados e permite consultar predições recentes.