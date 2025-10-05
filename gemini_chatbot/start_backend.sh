#!/bin/bash

# Script para iniciar o backend do Gemini ChatBot
# Uso: ./start_backend.sh

set -e  # Sai imediatamente se algum comando falhar

echo "🚀 Iniciando setup do backend..."

# Navegar para o diretório backend
echo "📁 Navegando para o diretório backend..."
cd backend

# Verificar se o requirements.txt existe
if [ ! -f "requirements.txt" ]; then
    echo "❌ Erro: Arquivo requirements.txt não encontrado em backend/"
    exit 1
fi

# Instalar dependências
echo "📦 Instalando dependências Python..."
pip install -r requirements.txt

if [ $? -eq 0 ]; then
    echo "✅ Dependências instaladas com sucesso!"
else
    echo "❌ Erro na instalação das dependências"
    exit 1
fi

# Executar a aplicação
echo "🎯 Iniciando servidor FastAPI..."
python3 run.py