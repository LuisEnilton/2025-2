# O que é o Whisper?

Whisper é um modelo open-source de **ASR** (Automatic Speech Recognition) criado pela OpenAI. Ele foi treinado em **\~680 mil horas** de áudio multilíngue e multitarefa (transcrição, tradução e identificação de idioma), o que lhe confere **robustez a sotaques, ruído e linguagem técnica**. Além de transcrever em vários idiomas, o Whisper também é capaz de **traduzir fala não-inglesa diretamente para inglês**. ([OpenAI][1], [OpenAI][2], [arXiv][3])

# Como funciona (por dentro, em 3 linhas)

* **Arquitetura**: um Transformer encoder-decoder que recebe espectrogramas de áudio (log-Mel) e produz texto.
* **Treino**: aprendizado “fraco” em larga escala (web-scale), com tarefas de transcrição e tradução supervisionadas.
* **Generalização**: por escala e diversidade do dataset, performa bem em *benchmarks* sem *fine-tuning* (modo zero-shot). ([OpenAI][2], [arXiv][3])

# Para que serve

* **Transcrição** de reuniões, aulas, entrevistas, vídeos do YouTube, *podcasts*, etc.
* **Tradução de fala** (ex.: PT→EN direto no modelo) e suporte a **detecção de idioma**.
* Implementações e variações aceleradas como **faster-whisper** (CTranslate2) e **whisper.cpp** permitem rodar rápido e localmente (CPU/GPU), até 4× mais veloz que a lib original em muitos cenários. ([GitHub][4], [Hugging Face][5])

> Observação: a OpenAI também oferece **APIs de speech-to-text** (histórico: whisper-1) além de opções mais novas; mas, como você pediu o Whisper em si e a tradução com Llama 3, abaixo vai um fluxo 100% local/auto-hospedado. ([Plataforma OpenAI][6])


# Exemplo: transcrever o áudio de um vídeo (EN) e traduzir para PT-BR com Llama 3 (Ollama)

## Pré-requisitos

1. **FFmpeg** (para extrair o áudio do vídeo)

* macOS: `brew install ffmpeg`
* Ubuntu/Debian: `sudo apt-get install ffmpeg`

2. **Python pacotes**

```bash
pip install faster-whisper==1.* numpy==1.* requests==2.*
```

*(“faster-whisper” é uma reimplementação performática do Whisper sobre CTranslate2.)* ([GitHub][4])

3. **Ollama + Llama 3** (para a tradução)

* Instale o Ollama e baixe o modelo:

  ```bash
  ollama pull llama3.2
  # ou: ollama pull llama3  (se preferir outra variante)
  ```
* Execute `ollama --version` e `ollama list` para checar. A API local do Ollama expõe endpoints em `http://localhost:11434/api/...`. ([ollama.readthedocs.io][7], [GitHub][8])

## Código Python (um arquivo só)

Este script:

1. Extrai o áudio de um vídeo (MP4, MKV, etc.).
2. Transcreve em inglês com Whisper (faster-whisper, modelo `large-v3`).
3. Agrupa o texto e pede ao Llama 3 (Ollama) a **tradução fiel para PT-BR**.

```python
import os
import subprocess
import math
import textwrap
import requests
from faster_whisper import WhisperModel

# ---------- Config ----------
VIDEO_IN = "entrada_video.mp4"       # seu vídeo de origem
AUDIO_WAV = "temp_audio.wav"
ASR_MODEL_SIZE = "large-v3"          # outras: tiny/base/small/medium/large-v2/v3
DEVICE = "auto"                      # "cuda" para GPU, "cpu" para CPU; "auto" tenta escolher
COMPUTE_TYPE = "float16"             # "int8_float16" para menos VRAM; use "float32" na CPU se precisar
OLLAMA_URL = "http://localhost:11434/api/chat"
OLLAMA_MODEL = "llama3.2"            # ou "llama3"

# ---------- 1) Extrair áudio do vídeo com FFmpeg ----------
def extract_audio(video_path, wav_path, sr=16000):
    if os.path.exists(wav_path):
        os.remove(wav_path)
    cmd = [
        "ffmpeg", "-y",
        "-i", video_path,
        "-ac", "1",           # mono
        "-ar", str(sr),       # 16 kHz
        "-vn",                # sem vídeo
        wav_path
    ]
    subprocess.run(cmd, check=True)

# ---------- 2) Transcrever com Whisper (faster-whisper) ----------
def transcribe_audio(wav_path):
    # Carrega o modelo (baixará na primeira vez para ~/.cache/faster_whisper)
    model = WhisperModel(ASR_MODEL_SIZE, device=DEVICE, compute_type=COMPUTE_TYPE)
    # language="en" ajuda quando você já sabe o idioma do áudio
    segments, info = model.transcribe(wav_path, language="en", beam_size=5, vad_filter=True)

    chunks = []
    srt_lines = []
    idx = 1
    for seg in segments:
        text = seg.text.strip()
        chunks.append(text)

        # SRT opcional
        def fmt(t):
            h = int(t // 3600)
            m = int((t % 3600) // 60)
            s = int(t % 60)
            ms = int((t - math.floor(t)) * 1000)
            return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

        srt_lines.append(f"{idx}")
        srt_lines.append(f"{fmt(seg.start)} --> {fmt(seg.end)}")
        srt_lines.append(text)
        srt_lines.append("")  # linha em branco
        idx += 1

    transcript_en = " ".join(chunks)
    with open("transcript_en.txt", "w", encoding="utf-8") as f:
        f.write(transcript_en)
    with open("transcript_en.srt", "w", encoding="utf-8") as f:
        f.write("\n".join(srt_lines))

    return transcript_en

# ---------- 3) Traduzir com Llama 3 (Ollama API /chat) ----------
def translate_with_llama3(text_en):
    # Para evitar ultrapassar limites de contexto, dividimos em blocos
    # Ajuste o tam. do bloco conforme o seu modelo/VRAM
    blocks = split_text(text_en, max_chars=3000)

    translated_blocks = []
    system_msg = (
        "Você é um tradutor profissional EN→PT-BR. "
        "Traduza fielmente, mantendo sentido, nomes próprios e termos técnicos. "
        "Não explique nada; responda apenas com o texto traduzido."
    )

    for i, block in enumerate(blocks, 1):
        payload = {
            "model": OLLAMA_MODEL,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Texto (parte {i} de {len(blocks)}):\n{block}"}
            ]
        }
        r = requests.post(OLLAMA_URL, json=payload, timeout=600)
        r.raise_for_status()
        data = r.json()
        translated = data.get("message", {}).get("content", "").strip()
        translated_blocks.append(translated)

    full_pt = "\n".join(translated_blocks)
    with open("transcript_ptbr.txt", "w", encoding="utf-8") as f:
        f.write(full_pt)
    return full_pt

def split_text(text, max_chars=3000):
    # quebra respeitando limites de parágrafos/espacos
    paragraphs = textwrap.wrap(text, width=max_chars, break_long_words=False, replace_whitespace=False)
    return paragraphs if paragraphs else [text]

if __name__ == "__main__":
    # 1) Extrai áudio do vídeo
    extract_audio(VIDEO_IN, AUDIO_WAV)

    # 2) Transcreve (EN)
    en_text = transcribe_audio(AUDIO_WAV)
    print("\n--- TRANSCRIÇÃO (EN) ---\n")
    print(en_text[:1000] + ("..." if len(en_text) > 1000 else ""))

    # 3) Traduz para PT-BR (Llama 3 via Ollama)
    pt_text = translate_with_llama3(en_text)
    print("\n--- TRADUÇÃO (PT-BR) ---\n")
    print(pt_text[:1000] + ("..." if len(pt_text) > 1000 else ""))

    # limpeza opcional do WAV
    # os.remove(AUDIO_WAV)
```

### Como executar

1. Coloque seu vídeo como `entrada_video.mp4` na mesma pasta do script (ou ajuste `VIDEO_IN`).
2. Deixe o **Ollama** rodando e com o modelo **llama3.2** baixado.
3. Rode o script: `python transcreve_e_traduz.py`
4. Saídas geradas:

   * `transcript_en.txt` (texto em inglês)
   * `transcript_en.srt` (legendas SRT)
   * `transcript_ptbr.txt` (tradução PT-BR)

---

## Dicas e variações

* **Modelo Whisper**: para vídeos longos/ruidosos, `large-v3` costuma dar melhor qualidade; para máquinas modestas, use `medium`/`small`. ([Hugging Face][5])
* **Desempenho**: em GPU com pouca VRAM, troque `COMPUTE_TYPE` para `"int8_float16"`; em CPU pura, `"float32"` (mais preciso, mais lento). ([GitHub][4])
* **Tradução direta pelo Whisper**: Whisper também pode **traduzir fala→EN** diretamente; neste exemplo, preferimos a rota “transcreve EN → traduz com Llama 3 (PT-BR)” para dar controle total da tradução. ([OpenAI][1])
* **API da OpenAI (alternativa)**: se quiser fazer **transcrição na nuvem** via endpoints de áudio da OpenAI, confira os guias oficiais de *speech-to-text*. ([Plataforma OpenAI][6])
* **Ollama API**: a rota `/api/chat` aceita mensagens multi-turn; também há `/api/generate` se preferir prompt único. ([ollama.readthedocs.io][7])

Outras possibilidades:  
- 1) fazer *diarization* por falante,
- 2) salvar **VTT**/**SRT** com tradução,
- 3) rodar dentro de **Docker**, ou
- 4) usar **LangChain** com um *chain* “Transcrever→Traduzir→Resumir”.

[1]: https://openai.com/index/whisper/?utm_source=chatgpt.com "Introducing Whisper"
[2]: https://cdn.openai.com/papers/whisper.pdf?utm_source=chatgpt.com "Robust Speech Recognition via Large-Scale Weak ..."
[3]: https://arxiv.org/abs/2212.04356?utm_source=chatgpt.com "[2212.04356] Robust Speech Recognition via Large-Scale ..."
[4]: https://github.com/SYSTRAN/faster-whisper?utm_source=chatgpt.com "Faster Whisper transcription with CTranslate2"
[5]: https://huggingface.co/Systran/faster-whisper-large-v3?utm_source=chatgpt.com "Systran/faster-whisper-large-v3"
[6]: https://platform.openai.com/docs/guides/speech-to-text?utm_source=chatgpt.com "Speech to text - OpenAI API"
[7]: https://ollama.readthedocs.io/en/api/?utm_source=chatgpt.com "API Reference - Ollama English Documentation"
[8]: https://github.com/ollama/ollama?utm_source=chatgpt.com "ollama/ollama: Get up and running with OpenAI gpt-oss, ..."
