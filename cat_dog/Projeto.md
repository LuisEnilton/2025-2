# Criação de um Modelo de Reconhecimento de Imagens de Cães e Gatos

## Funcionamento do Projeto de Solução

Este é um projeto completo de **classificação binária de imagens** (gatos vs. cachorros) que implementa uma pipeline de **Deep Learning** usando a biblioteca **PyTorch**. O projeto de software segue um fluxo padrão de Machine Learning:

1.  **Preparação dos Dados:** Baixa automaticamente um dataset, organiza as imagens em pastas de treino e validação, e aplica transformações (redimensionamento, normalização).
2.  **Definição do Modelo:** Utiliza uma rede neural convolucional pré-treinada (ResNet18) e adapta sua última camada para fazer uma classificação binária, uma técnica conhecida como **Transfer Learning**.
3.  **Treinamento:** Alimenta as imagens em lotes (batches) para o modelo, calcula o erro das previsões e ajusta os pesos da rede para minimizar esse erro ao longo de várias épocas (epochs).
4.  **Avaliação:** Mede o desempenho do modelo treinado em um conjunto de dados separado (validação) e gera gráficos para visualizar a evolução do aprendizado e exemplos de previsões.

Em suma, o projeto **automatiza a criação de um classificador de imagens** que, ao final do processo, é capaz de receber uma nova foto e prever com uma certa probabilidade se ela contém um gato ou um cachorro.

### Explicação do Processo Usado no Projeto

O projeto é um exemplo clássico e bem estruturado de como resolver um problema de visão computacional. O processo pode ser dividido em etapas claras, refletidas na organização dos arquivos:

#### 1. Configuração e Gerenciamento de Dependências (`requirements.txt`)
*   **Processo:** Define todo o ambiente software necessário para reproduzir o projeto. Isso garante que qualquer pessoa que baixe o código possa instalar as mesmas versões das bibliotecas e evitar conflitos.

#### 2. Definição Centralizada de Parâmetros (`Config.py`)
*   **Processo:** Adota uma prática de programação chamada **configuração centralizada**. Todos os parâmetros importantes (caminhos de arquivos, tamanho do batch, taxa de aprendizado, etc.) são definidos em um único lugar. Isso torna o código mais limpo, fácil de manter e de modificar (e.g., testar uma nova taxa de aprendizado é feito alterando apenas uma linha neste arquivo).

#### 3. Preparação e Carga de Dados (`data_preparation.py`)
*   **Processo:** Esta é a etapa de **Data Engineering**.
    *   **Download e Organização:** O código não assume que o dataset já está na máquina. Ele é baixado e organizado automaticamente nas pastas `train/cat`, `train/dog`, `val/cat`, `val/dog`.
    *   **Dataset Customizado:** Cria uma classe (`CatDogDataset`) que herda da classe `Dataset` do PyTorch. Isso é crucial, pois ensina ao PyTorch **como acessar cada imagem e seu rótulo correspondente**. O rótulo é inferido diretamente do nome do arquivo (e.g., `cat.124.jpg` -> rótulo `0`).
    *   **DataLoaders:** Cria objetos `DataLoader` que são responsáveis por agrupar as imagens em **batches**, embaralhar os dados de treino e carregá-los de forma eficiente durante o treinamento.

#### 4. Definição da Arquitetura do Modelo (`model.py`)
*   **Processo:** Utiliza a técnica de **Transferência de Aprendizado (Transfer Learning)**. Este é o conceito mais importante do projeto.
    *   **Por quê?** Treinar uma rede neural do zero requer muito poder computacional e um dataset gigantesco. O Transfer Learning aproveita um modelo já treinado (a ResNet18, que foi treinada no dataset ImageNet com milhões de imagens) e o adapta para uma nova tarefa.
    *   **Como?**
        1.  **Congela os parâmetros:** As camadas iniciais da rede, que são excelentes para detectar características básicas como bordas, texturas e formas, são congeladas. Elas não serão treinadas, poupando tempo e recursos.
        2.  **Substitui a cabeça (head):** A última camada totalmente conectada da ResNet, originalmente projetada para classificar 1000 classes do ImageNet, é substituída por uma nova camada projetada para classificar apenas 2 classes (gato ou cachorro). **Apenas os pesos desta nova camada serão treinados.**

#### 5. Loop de Treinamento e Validação (`train.py`)
*   **Processo:** Implementa o **ciclo central de aprendizado** do modelo.
    *   **Fase de Treino (`train_epoch`):**
        *   O modelo é colocado em modo de treino (`model.train()`).
        *   Para cada batch de imagens, o modelo faz uma previsão.
        *   A função de perda (**Binary Cross-Entropy**) calcula o erro entre a previsão e o rótulo verdadeiro.
        *   O otimizador (**Adam**) usa o cálculo do gradiente (backpropagation) para ajustar os pesos da rede (especificamente os da última camada) na direção que minimiza o erro.
    *   **Fase de Validação (`validate`):**
        *   O modelo é colocado em modo de avaliação (`model.eval()`).
        *   Os dados de validação, **nunca vistos durante o treino**, são usados para testar o modelo.
        *   O cálculo de gradientes é desativado para economizar memória e computação.
        *   A acurácia é calculada para medir o desempenho real do modelo.

#### 6. Avaliação e Visualização dos Resultados (`evaluate.py`)
*   **Processo:** Foca na **interpretabilidade e análise** do modelo treinado.
    *   **Predição em Imagens Individuais:** Mostra como usar o modelo para prever uma única imagem nova.
    *   **Visualização em Lote:** Gera uma grade com várias imagens e suas previsões, permitindo uma verificação rápida e intuitiva do desempenho.
    *   **Análise do Treinamento:** Plota gráficos de Loss e Acurácia ao longo do tempo. Esses gráficos são **essenciais** para diagnosticar problemas como overfitting (quando a loss de treino continua caindo mas a loss de validação para de cair ou sobe).

#### 7. Orquestração de Todo o Pipeline (`main.py`)
*   **Processo:** O arquivo principal **orquestra todo o fluxo** descrito acima, na sequência correta. Ele é o "script mestre" que alguém executaria para treinar o modelo do início ao fim, demonstrando como todas as peças separadas se conectam para formar um sistema completo.

### Conclusão do Processo

O projeto emprega um **processo de engenharia de machine learning robusto e bem organizado**, indo desde a aquisição e preparação dos dados até o deploy de um modelo treinado e sua avaliação final. A escolha inteligente do **Transfer Learning** com a ResNet18 é o que torna o projeto viável e eficiente, permitindo alcançar bons resultados sem a necessidade de um poder computacional massivo ou de um dataset extremamente grande. A estrutura modular do código (com arquivos separados para dados, modelo, treino, etc.) é uma prática exemplar que facilita a compreensão, a manutenção e a escalabilidade do projeto.

## Arquivo requirements.txt

O arquivo requirements.txt lista os pacotes Python necessários para rodar o projeto. Cada linha especifica um pacote e a versão mínima recomendada. Veja o que cada um faz:

- **torch**: Biblioteca principal do PyTorch para deep learning.
- **torchvision**: Conjunto de utilitários e modelos para visão computacional com PyTorch.
- **pillow**: Manipulação de imagens (abrir, salvar, converter formatos).
- **matplotlib**: Visualização de dados e gráficos.
- **numpy**: Operações matemáticas e manipulação de arrays.
- **tqdm**: Barra de progresso para loops.
- **requests**: Realiza requisições HTTP (útil para baixar arquivos).
 
Instale esses pacotes para garantir que o código do projeto funcione corretamente, especialmente para tarefas de processamento de imagens, treinamento de modelos e visualização de resultados.

## Arquivo Config.py

O arquivo config.py define uma classe chamada Config que centraliza as principais configurações do projeto de classificação de imagens de gatos e cachorros. Aqui está um resumo dos principais pontos:

* **URLs e diretórios de dados**: Define onde baixar o dataset (DATA_URL) e os caminhos locais para os dados (DATA_DIR, TRAIN_DIR, VAL_DIR).

* **Parâmetros de treinamento**: Define o tamanho do batch (BATCH_SIZE), taxa de aprendizado (LEARNING_RATE), número de épocas (NUM_EPOCHS) e onde salvar o modelo treinado (MODEL_PATH).

* **Transformações de imagem**: Define o tamanho das imagens (IMAGE_SIZE) e os valores de normalização (MEAN, STD) usados para pré-processar as imagens.

* **Configuração do dispositivo**: Escolhe automaticamente entre GPU (cuda) ou CPU para treinar o modelo, dependendo da disponibilidade.

* **Método estático get_transform()**: Retorna uma sequência de transformações para serem aplicadas nas imagens antes de alimentar o modelo (redimensionamento, conversão para tensor e normalização).

Este arquivo facilita a manutenção e reutilização das configurações em diferentes partes do projeto.

## Arquivo data_preparation.py

O arquivo data_preparation.py cuida do preparo dos dados para o projeto de classificação de gatos e cachorros. Veja o que cada parte faz:

### 1. **DataHandler**
- **download_and_extract**: Baixa o arquivo zip do dataset a partir de uma URL, extrai o conteúdo e cria as pastas `train` e `val` para treinamento e validação.
- **copy_random_files**: Copia uma quantidade aleatória de arquivos de uma pasta de origem para uma pasta de destino, renomeando cada arquivo com um prefixo (por exemplo, "cat" ou "dog").

### 2. **CatDogDataset**
- Herda de `torch.utils.data.Dataset` para criar um dataset customizado.
- **__init__**: Recebe o diretório raiz e uma transformação. Lista todas as imagens válidas no diretório.
- **__len__**: Retorna o número de imagens.
- **__getitem__**: Carrega a imagem pelo índice, aplica a transformação e define o rótulo (`0` para gato, `1` para cachorro) baseado no nome do arquivo. Se houver erro ao carregar, tenta outro índice aleatório.

### 3. **prepare_data_loaders**
- Cria os datasets de treino e validação usando as transformações definidas em `Config`.
- Cria os `DataLoader` do PyTorch para facilitar o carregamento dos dados em batches durante o treinamento e validação.

Este arquivo automatiza o download, extração, organização e carregamento dos dados, além de definir como as imagens e rótulos são lidos para uso no treinamento do modelo.

## Arquivo model.py

O arquivo model.py define o modelo de classificação de gatos e cachorros usando PyTorch e torchvision. Veja o que cada parte faz:

### 1. **CatDogClassifier**
- Herda de `nn.Module` (PyTorch).
- Usa o modelo pré-treinado `ResNet18` da torchvision.
- **Congela os parâmetros**: As camadas do modelo base não são treinadas (útil para transfer learning).
- **Substitui a última camada**: Troca a camada final (`fc`) para uma camada linear com 1 saída (classificação binária).
- **forward**: Aplica o modelo e retorna a saída com função sigmoide (probabilidade entre 0 e 1).

### 2. **initialize_model**
- Inicializa o modelo, a função de perda (`BCELoss` para classificação binária) e o otimizador (`Adam`).
- Move o modelo para o dispositivo correto (CPU ou GPU).
- Retorna o modelo, a função de perda e o otimizador.
  
Este arquivo prepara o modelo de rede neural para classificar imagens como gato ou cachorro, usando transfer learning com ResNet18, e configura os componentes necessários para o treinamento.

## Arquivo evaluate.py

O arquivo evaluate.py contém funções para avaliar e visualizar o desempenho do modelo de classificação de gatos e cachorros. Veja o que cada função faz:

### 1. **predict_image**
- Recebe o caminho de uma imagem, o modelo, a transformação e o dispositivo (CPU/GPU).
- Carrega e transforma a imagem, faz a predição com o modelo em modo avaliação.
- Retorna a classe prevista (`cat` ou `dog`) e a probabilidade associada.

### 2. **visualize_predictions**
- Recebe uma lista de caminhos de imagens e exibe as imagens com suas predições.
- Mostra até 6 imagens em um grid, com o nome da classe prevista e a probabilidade no título.

### 3. **plot_training_history**
- Recebe um dicionário `history` com métricas de treinamento e validação.
- Plota gráficos de perda (loss) e acurácia (accuracy) para acompanhar o desempenho do modelo ao longo das épocas.
 
Este arquivo facilita a avaliação do modelo, mostrando predições individuais, visualizando resultados em lote e acompanhando o histórico de treinamento.

## Arquivo train.py

O arquivo train.py contém funções para treinar e validar o modelo de classificação de gatos e cachorros. Veja o que cada parte faz:

### 1. **train_epoch**
- Treina o modelo por uma época (passagem por todo o dataset de treino).
- Move imagens e rótulos para o dispositivo (CPU/GPU).
- Calcula a saída do modelo, a perda, faz o backpropagation e atualiza os pesos.
- Acumula a perda total para calcular a média no final.

### 2. **validate**
- Avalia o modelo no dataset de validação (sem atualizar pesos).
- Calcula a perda e a acurácia (percentual de predições corretas).
- Usa o modelo em modo avaliação e desabilita o cálculo de gradientes.

### 3. **train_model**
- Executa o treinamento por várias épocas.
- Para cada época, chama `train_epoch` e `validate`, armazenando as métricas em um histórico.
- Imprime as métricas de cada época (perda de treino, perda de validação e acurácia de validação).
- Retorna o histórico para análise posterior.

Este arquivo organiza o processo de treinamento e validação do modelo, permitindo acompanhar o desempenho ao longo das épocas e facilitando o ajuste dos hiperparâmetros.

## Arquivo main.py

O arquivo main.py é o ponto de entrada do projeto e organiza todo o fluxo de processamento, treinamento e avaliação do modelo de classificação de gatos e cachorros. Veja o que cada etapa faz:

### 1. **Preparação dos dados**
- Baixa e extrai o dataset usando `DataHandler.download_and_extract`.
- Copia arquivos de gatos e cachorros para as pastas de treino e validação usando `copy_random_files`.

### 2. **Criação dos DataLoaders**
- Usa `prepare_data_loaders` para criar os carregadores de dados de treino e validação, que facilitam o processamento em batches.

### 3. **Inicialização do modelo**
- Chama `initialize_model` para criar o modelo, a função de perda e o otimizador.

### 4. **Treinamento**
- Executa o treinamento do modelo com `train_model`, armazenando o histórico de métricas.

### 5. **Salvar o modelo**
- Salva os pesos do modelo treinado em um arquivo usando `torch.save`.

### 6. **Avaliação e visualização**
- Plota o histórico de treinamento (perda e acurácia) com `plot_training_history`.
- Faz predições em exemplos de imagens e mostra os resultados com `visualize_predictions`.

### 7. **Tratamento de erros**
- Todo o processo está dentro de um bloco `try/except` para capturar e exibir erros.

O arquivo main.py automatiza todo o pipeline do projeto: desde o preparo dos dados, passando pelo treinamento, até a avaliação e visualização dos resultados.