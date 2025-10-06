#!/bin/bash

# Script para iniciar o cliente do Gemini ChatBot
# Uso: ./start_client.sh [IP_DO_SERVIDOR]

set -e  # Sai imediatamente se algum comando falhar

# Verificar se foi fornecido um IP como parâmetro
if [ $# -eq 0 ]; then
    echo "❌ Erro: IP do servidor não fornecido"
    echo "Uso: $0 <IP_DO_SERVIDOR>"
    echo "Exemplo: ./start_client.sh 10.13.63.20"
    exit 1
fi

SERVER_IP="$1"

echo "🚀 Iniciando setup do cliente..."
echo "📡 Conectando ao servidor: $SERVER_IP"

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

# Executar o cliente com o IP fornecido
echo "🎯 Iniciando cliente de chat..."
echo "🔗 Conectando ao servidor: $SERVER_IP"
python3 chat_client.py "$SERVER_IP"
