## 📌 O que é o LangChain?

O **LangChain** é um **framework open source em Python e JavaScript** que facilita a criação de aplicações de **IA baseadas em LLMs (Large Language Models)**.
Ele ajuda a **conectar modelos de linguagem** (como GPT, LLaMA, Mistral, etc.) com **dados externos** e **ferramentas**, permitindo construir aplicações mais robustas, como:

* **Chatbots inteligentes** (que consultam dados específicos).
* **Assistentes de busca** (RAG – Retrieval Augmented Generation).
* **Agentes autônomos** (que tomam decisões e executam ações).
* **Integração com bancos de dados, APIs e documentos locais**.

## ⚙️ Como ele funciona?

O LangChain é baseado em **blocos modulares** que podem ser combinados:

1. **Models (LLMs ou Chat Models)** – o motor de IA (ex.: GPT-4, LLaMA, Gemini).
2. **Prompts** – mensagens estruturadas que orientam o modelo.
3. **Chains** – encadeamento de chamadas (ex.: gerar resposta + salvar no banco).
4. **Memory** – memória conversacional (guardar contexto).
5. **Retrievers** – buscar informações em bancos de dados, vetores, PDFs, sites.
6. **Agents** – permitem que o modelo escolha quais ferramentas usar em cada momento.

## 🎯 Para que ele serve?

Ele serve para **transformar LLMs em aplicações reais**, indo além de apenas “perguntar e responder”.
Com LangChain você pode:

* Integrar **LLMs a seus próprios dados** (ex.: PDFs, SQL, NoSQL).
* Criar **assistentes conversacionais especializados**.
* Automatizar **tarefas complexas** (consulta em APIs, cálculos, busca em documentos).
* Construir **sistemas de RAG** (modelos que respondem com base em documentos específicos).
  
## 🐍 Exemplo simples em Python

Aqui está um exemplo mínimo de como usar o LangChain com o modelo **GPT-4o-mini** via API da OpenAI:

```python
# Instalar dependências:
# pip install langchain langchain-openai

from langchain_openai import ChatOpenAI
from langchain.prompts import ChatPromptTemplate
from langchain.chains import LLMChain

# 1. Configura o modelo (usa API da OpenAI)
llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)

# 2. Define um prompt estruturado
prompt = ChatPromptTemplate.from_template("Traduza o seguinte texto para o português: {texto}")

# 3. Cria a chain (prompt + LLM)
chain = LLMChain(llm=llm, prompt=prompt)

# 4. Executa a chain
resposta = chain.run({"texto": "Artificial Intelligence is transforming the world."})
print(resposta)
```

👉 Saída esperada:

```
A Inteligência Artificial está transformando o mundo.
```

## 🚀 Próximos Passos

* Para **chatbots com memória**, você usaria `ConversationChain`.
* Para **buscar em PDFs ou banco de dados**, usaria **Retrievers + Vectorstores** (ex.: ChromaDB, FAISS).
* Para **agentes inteligentes**, você combinaria **LLM + Ferramentas externas** (APIs, Python, SQL).

# Exemplo de criação de um RAG usando LangChain

Vamos montar um **exemplo completo de RAG com LangChain** que lê **PDFs**, indexa em um **vetor (ChromaDB)**, e oferece um **chat** que responde com base nesses arquivos.

Abaixo vai um **script único** (pode rodar em modo CLI ou como **API FastAPI**). Ele funciona **sem chave de API** usando *embeddings* open-source (Sentence Transformers) e pode usar:

* **Ollama** local (ex.: `llama3`, `mistral`, `qwen2`) **ou**
* **OpenAI** (se você tiver `OPENAI_API_KEY`).

# 1) Instalação

```bash
# Python 3.10+
pip install -U langchain langchain-community langchain-openai langchain-ollama \
  chromadb pypdf sentence-transformers fastapi uvicorn python-dotenv
```

Se for usar **Ollama**:

```bash
# macOS/Linux
curl -fsSL https://ollama.com/install.sh | sh
ollama pull llama3
```

Estrutura de pastas:

```
rag_pdf/
  app.py
  .env              # opcional (para OPENAI_API_KEY)
  data/             # coloque aqui seus PDFs
  chroma_db/        # será criado automaticamente
```

`.env` (opcional):

```
OPENAI_API_KEY=sk-...
```

# 2) O código (app.py)

```python
import os
from pathlib import Path
from dotenv import load_dotenv

# LangChain core & community
from langchain_community.document_loaders import DirectoryLoader, PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.vectorstores import Chroma
from langchain_community.embeddings import HuggingFaceEmbeddings

# Modelos (OpenAI ou Ollama)
from langchain_openai import ChatOpenAI
from langchain_ollama import ChatOllama

# Chain de QA conversacional com RAG
from langchain.chains import ConversationalRetrievalChain

# API (opcional)
from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

load_dotenv()

# -----------------------------
# Configurações
# -----------------------------
DATA_DIR = Path("data")
PERSIST_DIR = "chroma_db"

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"  # rápido e leve
USE_OPENAI = bool(os.getenv("OPENAI_API_KEY"))              # usa OpenAI se houver chave
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "llama3")          # fallback local

# -----------------------------
# 1) Carregar e fragmentar PDFs
# -----------------------------
def load_and_split_pdfs(data_dir: Path):
    if not data_dir.exists():
        raise FileNotFoundError(f"Pasta '{data_dir}' não encontrada. Crie e coloque PDFs dentro dela.")
    # Carrega TODOS os PDFs da pasta
    docs = []
    for pdf in data_dir.glob("*.pdf"):
        loader = PyPDFLoader(str(pdf))
        docs.extend(loader.load())

    splitter = RecursiveCharacterTextSplitter(
        chunk_size=1000, chunk_overlap=150, separators=["\n\n", "\n", " ", ""]
    )
    chunks = splitter.split_documents(docs)
    return chunks

# -----------------------------
# 2) Criar/abrir o VectorStore (Chroma)
# -----------------------------
def build_or_load_vectorstore(chunks):
    embeddings = HuggingFaceEmbeddings(model_name=EMBEDDING_MODEL)
    if chunks is not None:
        # cria do zero e persiste (primeira vez)
        vectordb = Chroma.from_documents(
            documents=chunks,
            embedding=embeddings,
            persist_directory=PERSIST_DIR
        )
    else:
        # reabre índice existente
        vectordb = Chroma(
            embedding_function=embeddings,
            persist_directory=PERSIST_DIR
        )
    return vectordb

# -----------------------------
# 3) Selecionar o LLM (OpenAI ou Ollama)
# -----------------------------
def make_llm(temperature: float = 0.1):
    if USE_OPENAI:
        # Modelos como gpt-4o-mini, gpt-4.1, etc.
        return ChatOpenAI(model="gpt-4o-mini", temperature=temperature)
    else:
        # Modelos locais via Ollama: llama3, mistral, qwen2, phi3, etc.
        return ChatOllama(model=OLLAMA_MODEL, temperature=temperature)

# -----------------------------
# 4) Construir a chain de RAG conversacional
# -----------------------------
def build_qa_chain(retriever):
    llm = make_llm()
    # Prompt padrão interno do ConversationalRetrievalChain já faz "stuff" dos documentos.
    # Você pode customizar mais tarde com combine_docs_chain e prompt próprio.
    chain = ConversationalRetrievalChain.from_llm(
        llm=llm,
        retriever=retriever,
        return_source_documents=True,
        verbose=False
    )
    return chain

# -----------------------------
# Inicialização (índice)
# -----------------------------
def ensure_index():
    if not os.path.exists(PERSIST_DIR) or not os.listdir(PERSIST_DIR):
        print("⏳ Criando índice vetorial a partir dos PDFs (primeira execução)...")
        chunks = load_and_split_pdfs(DATA_DIR)
        vectordb = build_or_load_vectorstore(chunks)
        vectordb.persist()
        print(f"✅ Índice criado e persistido em '{PERSIST_DIR}'.")
    else:
        print("✅ Índice já existente. Usando base persistida.")

# -----------------------------
# CLI Chat
# -----------------------------
def run_cli_chat(k: int = 4):
    ensure_index()
    vectordb = build_or_load_vectorstore(chunks=None)
    retriever = vectordb.as_retriever(search_kwargs={"k": k})
    qa = build_qa_chain(retriever)

    print("\n🤖 RAG Chat sobre PDFs — digite sua pergunta. ('/exit' para sair)")
    chat_history = []  # lista de pares (pergunta, resposta)

    while True:
        question = input("\nVocê: ").strip()
        if not question:
            continue
        if question.lower() in {"/exit", "sair", "quit", "q"}:
            print("Tchau! 👋")
            break

        result = qa({"question": question, "chat_history": chat_history})
        answer = result["answer"]
        sources = result.get("source_documents", [])

        print("\nAssistente:", answer)

        if sources:
            print("\n📚 Fontes:")
            for i, doc in enumerate(sources, 1):
                meta = doc.metadata or {}
                source = meta.get("source", "desconhecida")
                page = meta.get("page", "?")
                print(f"  {i}. {Path(source).name} (p.{page})")

        chat_history.append((question, answer))

# -----------------------------
# FastAPI (opcional)
# -----------------------------
app = FastAPI(title="RAG PDF Chat")

class Query(BaseModel):
    question: str
    session_id: str | None = "default"

# memória simples por sessão
SESSION_HISTORY: dict[str, list[tuple[str, str]]] = {}

@app.on_event("startup")
def _startup():
    ensure_index()
    global vectordb, retriever, qa
    vectordb = build_or_load_vectorstore(chunks=None)
    retriever = vectordb.as_retriever(search_kwargs={"k": 4})
    qa = build_qa_chain(retriever)

@app.post("/chat")
def chat(q: Query):
    sid = q.session_id or "default"
    history = SESSION_HISTORY.setdefault(sid, [])
    result = qa({"question": q.question, "chat_history": history})
    answer = result["answer"]
    sources = [
        {"file": Path(d.metadata.get("source", "desconhecida")).name,
         "page": d.metadata.get("page", "?")}
        for d in result.get("source_documents", [])
    ]
    history.append((q.question, answer))
    return {"answer": answer, "sources": sources}

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--api", action="store_true", help="Rodar como API FastAPI")
    args = parser.parse_args()
    if args.api:
        uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
    else:
        run_cli_chat()
```

# 3) Como executar

### Modo **CLI** (mais rápido para testar)

1. Coloque seus **PDFs** em `./data`.
2. Rode:

```bash
python app.py
```

3. Pergunte algo como:

```
"Quais são os principais conceitos tratados no documento X?"
```

O programa responde e lista as **fontes (PDF e página)** usadas.

### Modo **API** (FastAPI)

```bash
python app.py --api
# Em outro terminal, teste:
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"question":"Resuma o PDF", "session_id":"sessao1"}'
```

## Observações e melhorias

* **Qualidade**: trocar o embedding por um maior (ex.: `all-mpnet-base-v2`) melhora a recuperação.
* **Privacidade**: tudo roda local (com Ollama e embeddings open-source).
* **Modelo**: para português, considere `qwen2`, `mistral`, `llama3:instruct` no Ollama.
* **Citações**: você pode personalizar o *prompt* para **sempre citar** arquivo/página.
* **Escala**: para muitos PDFs, use FAISS/Weaviate/Milvus; e banco persistente para histórico.
