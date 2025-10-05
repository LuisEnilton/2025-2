#!/bin/bash

# Script para iniciar o cliente do Gemini ChatBot
# Uso: ./start_client.sh

set -e  # Sai imediatamente se algum comando falhar

echo "🚀 Iniciando setup do cliente..."

# Navegar para o diretório client
echo "📁 Navegando para o diretório client..."
cd client

# Verificar se o requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Arquivo requirements.txt não encontrado em client/"
    exit 1
fi

# Verificar se o chat_client.py existe
if [ ! -f "chat_client.py" ]; then
    echo "❌ Erro: Arquivo chat_client.py não encontrado em client/"
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip3 install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro na instalação das dependências"
    exit 1
fi

# Executar o cliente
echo "🎯 Iniciando cliente de chat..."
python3 chat_client.py