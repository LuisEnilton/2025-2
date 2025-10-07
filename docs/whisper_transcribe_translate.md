Abaixo está um **script Python completo** — limpo, robusto e comentado — que implementa a tradução de um vídeo em inglês para transcrição em Português:

* extrai o áudio de um vídeo com **FFmpeg**;
* transcreve em inglês com **Whisper (faster-whisper)**;
* gera **transcript\_en.txt** e **transcript\_en.srt**;
* traduz a transcrição para **português (PT-BR)** usando **Llama 3** via **Ollama**;
* opcionalmente traduz **cada segmento** e gera **transcript\_ptbr.srt** preservando os *timestamps* (ativando `--translate-srt`).

# 1) Pré-requisitos

```bash
# FFmpeg
# macOS: 
brew install ffmpeg
# Ubuntu/Debian:
sudo apt-get update && sudo apt-get install -y ffmpeg

# Python libs
pip install faster-whisper==1.* numpy==1.* requests==2.* rich==13.*

# Ollama + Llama 3 (em outro terminal)
# macOS/Linux: https://ollama.com
ollama pull llama3.2   # (ou "llama3")
```

# 2) Script: `whisper_transcribe_translate.py`

```python
#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
Estudo de Caso — Seção 5:
Transcrição (Whisper/faster-whisper) + Tradução (Llama 3 via Ollama)

Saídas:
  - transcript_en.txt       (texto em inglês)
  - transcript_en.srt       (legendas SRT em inglês)
  - transcript_ptbr.txt     (tradução PT-BR do texto completo)
  - transcript_ptbr.srt     (opcional: tradução PT-BR segmentada com os mesmos timestamps)

Uso (exemplos):
  python whisper_transcribe_translate.py input.mp4
  python whisper_transcribe_translate.py input.mkv --model-size large-v3 --device auto --translate-srt
"""

import argparse
import math
import os
import subprocess
import sys
from dataclasses import dataclass
from typing import List, Tuple

import requests
from faster_whisper import WhisperModel
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn

# -----------------------
# Configurações padrão
# -----------------------
DEFAULT_SAMPLE_RATE = 16000
DEFAULT_MODEL_SIZE = "large-v3"   # tiny/base/small/medium/large-v2/large-v3
DEFAULT_DEVICE = "auto"           # "cuda", "cpu" ou "auto"
DEFAULT_COMPUTE_TYPE = "float16"  # alternativas: "int8_float16" (menos VRAM), "float32" (CPU)
DEFAULT_OLLAMA_URL = "http://localhost:11434/api/chat"
DEFAULT_OLLAMA_MODEL = "llama3.2" # ou "llama3"

console = Console()

@dataclass
class Segment:
    idx: int
    start: float
    end: float
    text: str

# -----------------------
# Utilidades
# -----------------------
def ensure_ffmpeg():
    """Checa se o ffmpeg está disponível."""
    try:
        subprocess.run(["ffmpeg", "-version"], stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=True)
    except Exception as e:
        console.print("[red]FFmpeg não encontrado. Instale e tente novamente.[/red]")
        raise SystemExit(1) from e

def extract_audio(input_video: str, output_wav: str, sr: int = DEFAULT_SAMPLE_RATE):
    """Extrai o áudio como WAV mono a 16kHz."""
    if os.path.exists(output_wav):
        os.remove(output_wav)
    cmd = [
        "ffmpeg", "-y",
        "-i", input_video,
        "-ac", "1",              # mono
        "-ar", str(sr),          # sample rate
        "-vn",                   # sem vídeo
        output_wav
    ]
    subprocess.run(cmd, check=True)

def fmt_srt_time(t: float) -> str:
    """Formata segundos em timestamp SRT."""
    h = int(t // 3600)
    m = int((t % 3600) // 60)
    s = int(t % 60)
    ms = int((t - math.floor(t)) * 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def write_srt(path: str, segments: List[Segment]):
    """Escreve arquivo SRT a partir de segmentos."""
    lines = []
    for seg in segments:
        lines.append(str(seg.idx))
        lines.append(f"{fmt_srt_time(seg.start)} --> {fmt_srt_time(seg.end)}")
        lines.append(seg.text.strip())
        lines.append("")  # linha em branco
    with open(path, "w", encoding="utf-8") as f:
        f.write("\n".join(lines))

def write_txt(path: str, text: str):
    with open(path, "w", encoding="utf-8") as f:
        f.write(text)

def chunk_text(text: str, max_chars: int = 3000) -> List[str]:
    """Divide texto em blocos para não estourar contexto do LLM."""
    if len(text) <= max_chars:
        return [text]
    chunks, cur, cur_len = [], [], 0
    for para in text.split("\n"):
        if cur_len + len(para) + 1 > max_chars:
            chunks.append("\n".join(cur).strip())
            cur, cur_len = [para], len(para) + 1
        else:
            cur.append(para)
            cur_len += len(para) + 1
    if cur:
        chunks.append("\n".join(cur).strip())
    return [c for c in chunks if c]

# -----------------------
# Transcrição (Whisper)
# -----------------------
def transcribe_whisper(
    wav_path: str,
    model_size: str = DEFAULT_MODEL_SIZE,
    device: str = DEFAULT_DEVICE,
    compute_type: str = DEFAULT_COMPUTE_TYPE,
    language_hint: str = "en",
) -> Tuple[str, List[Segment]]:
    """Roda transcrição e retorna (texto_total, segmentos)."""
    model = WhisperModel(model_size, device=device, compute_type=compute_type)
    segments, info = model.transcribe(
        wav_path,
        language=language_hint,   # define "en" quando já se sabe o idioma
        beam_size=5,
        vad_filter=True
    )
    out_segments: List[Segment] = []
    texts = []
    idx = 1
    for seg in segments:
        txt = seg.text.strip()
        out_segments.append(Segment(idx=idx, start=seg.start, end=seg.end, text=txt))
        texts.append(txt)
        idx += 1
    full_text = " ".join(texts).strip()
    return full_text, out_segments

# -----------------------
# Tradução (Ollama/Llama3)
# -----------------------
def translate_text_ollama(
    text: str,
    model: str = DEFAULT_OLLAMA_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
    system_msg: str = (
        "Você é um tradutor profissional EN→PT-BR. "
        "Traduza fielmente, mantendo sentido, nomes próprios e termos técnicos. "
        "Não explique nada; responda apenas com o texto traduzido."
    ),
    timeout: int = 600,
) -> str:
    """Traduz um texto longo (com *chunking* automático)."""
    chunks = chunk_text(text, max_chars=3000)
    translated = []
    for i, block in enumerate(chunks, 1):
        payload = {
            "model": model,
            "stream": False,
            "messages": [
                {"role": "system", "content": system_msg},
                {"role": "user", "content": f"Traduza para PT-BR (parte {i} de {len(chunks)}):\n{block}"}
            ],
        }
        resp = requests.post(url, json=payload, timeout=timeout)
        resp.raise_for_status()
        translated.append(resp.json().get("message", {}).get("content", "").strip())
    return "\n".join(translated).strip()

def translate_segments_ollama(
    segments: List[Segment],
    model: str = DEFAULT_OLLAMA_MODEL,
    url: str = DEFAULT_OLLAMA_URL,
    timeout: int = 600,
) -> List[Segment]:
    """Traduz cada segmento para PT-BR (útil para gerar SRT traduzido)."""
    translated: List[Segment] = []
    with Progress(
        SpinnerColumn(), TextColumn("[progress.description]{task.description}"),
        console=console
    ) as progress:
        task = progress.add_task("Traduzindo segmentos (PT-BR)…", total=len(segments))
        for seg in segments:
            payload = {
                "model": model,
                "stream": False,
                "messages": [
                    {"role": "system", "content":
                        "Traduza EN→PT-BR de forma fiel, mantendo termos técnicos. "
                        "Responda apenas com o texto traduzido."
                    },
                    {"role": "user", "content": seg.text}
                ],
            }
            resp = requests.post(url, json=payload, timeout=timeout)
            resp.raise_for_status()
            pt = resp.json().get("message", {}).get("content", "").strip()
            translated.append(Segment(idx=seg.idx, start=seg.start, end=seg.end, text=pt))
            progress.update(task, advance=1)
    return translated

# -----------------------
# Pipeline principal
# -----------------------
def main():
    parser = argparse.ArgumentParser(description="Transcrever (Whisper) e traduzir (Llama3 via Ollama) um vídeo.")
    parser.add_argument("video", help="Caminho do arquivo de vídeo de entrada (mp4, mkv, etc.)")
    parser.add_argument("--outdir", default=".", help="Diretório de saída (default: atual)")
    parser.add_argument("--sr", type=int, default=DEFAULT_SAMPLE_RATE, help="Sample rate do WAV (default: 16000)")
    parser.add_argument("--model-size", default=DEFAULT_MODEL_SIZE, help="Tamanho do Whisper (ex.: large-v3)")
    parser.add_argument("--device", default=DEFAULT_DEVICE, help='Dispositivo: "cpu", "cuda" ou "auto"')
    parser.add_argument("--compute-type", default=DEFAULT_COMPUTE_TYPE, help='Ex.: "float16", "int8_float16", "float32"')
    parser.add_argument("--ollama-url", default=DEFAULT_OLLAMA_URL, help="URL da API do Ollama /api/chat")
    parser.add_argument("--ollama-model", default=DEFAULT_OLLAMA_MODEL, help="Modelo do Ollama (ex.: llama3.2)")
    parser.add_argument("--language-hint", default="en", help="Hint de idioma para a transcrição (default: en)")
    parser.add_argument("--translate-srt", action="store_true", help="Gera transcript_ptbr.srt traduzindo segmento a segmento")
    args = parser.parse_args()

    video_path = args.video
    outdir = args.outdir
    os.makedirs(outdir, exist_ok=True)

    wav_path = os.path.join(outdir, "temp_audio.wav")
    en_txt_path = os.path.join(outdir, "transcript_en.txt")
    en_srt_path = os.path.join(outdir, "transcript_en.srt")
    pt_txt_path = os.path.join(outdir, "transcript_ptbr.txt")
    pt_srt_path = os.path.join(outdir, "transcript_ptbr.srt")

    rprint("[bold cyan]== Whisper + Llama3 Pipeline ==[/bold cyan]")
    ensure_ffmpeg()

    # 1) Extrair áudio
    rprint(":speaker: [cyan]Extraindo áudio com FFmpeg…[/cyan]")
    try:
        extract_audio(video_path, wav_path, sr=args.sr)
    except subprocess.CalledProcessError as e:
        console.print(f"[red]Erro ao extrair áudio: {e}[/red]")
        sys.exit(1)

    # 2) Transcrever
    rprint(":memo: [cyan]Transcrevendo com Whisper (faster-whisper)…[/cyan]")
    try:
        en_text, segments = transcribe_whisper(
            wav_path,
            model_size=args.model_size,
            device=args.device,
            compute_type=args.compute_type,
            language_hint=args.language_hint,
        )
    except Exception as e:
        console.print(f"[red]Erro na transcrição: {e}[/red]")
        sys.exit(1)

    # salvar saídas em inglês
    write_txt(en_txt_path, en_text)
    write_srt(en_srt_path, segments)
    rprint(f"[green]OK[/green] → {en_txt_path}")
    rprint(f"[green]OK[/green] → {en_srt_path}")

    # 3) Traduzir texto completo para PT-BR
    rprint(":globe_with_meridians: [cyan]Traduzindo texto completo para PT-BR (Ollama/Llama3)…[/cyan]")
    try:
        pt_text = translate_text_ollama(
            en_text,
            model=args.ollama_model,
            url=args.ollama_url
        )
    except Exception as e:
        console.print(f"[red]Erro na tradução (texto completo): {e}[/red]")
        sys.exit(1)

    write_txt(pt_txt_path, pt_text)
    rprint(f"[green]OK[/green] → {pt_txt_path}")

    # 4) (Opcional) Traduzir segmento a segmento e gerar SRT em PT-BR
    if args.translate_srt:
        rprint(":film_frames: [cyan]Gerando SRT em PT-BR (tradução por segmento)…[/cyan]")
        try:
            seg_pt = translate_segments_ollama(
                segments,
                model=args.ollama_model,
                url=args.ollama_url
            )
            write_srt(pt_srt_path, seg_pt)
            rprint(f"[green]OK[/green] → {pt_srt_path}")
        except Exception as e:
            console.print(f"[yellow]Falha ao criar SRT PT-BR: {e}[/yellow] (prosseguindo apenas com TXT PT-BR)")

    # Limpeza opcional do WAV
    try:
        if os.path.exists(wav_path):
            os.remove(wav_path)
    except Exception:
        pass

    rprint("[bold green]Concluído.[/bold green]")

if __name__ == "__main__":
    main()
```

# 3) Como usar

```bash
# caso 1: transcrever + traduzir para PT-BR (TXT), sem SRT traduzido
python whisper_transcribe_translate.py entrada_video.mp4 --outdir saida

# caso 2: idem, mas também gerar SRT em PT-BR (segmento a segmento)
python whisper_transcribe_translate.py entrada_video.mp4 --outdir saida --translate-srt

# opções úteis:
# - escolher outro tamanho de modelo Whisper (mais leve/pesado)
python whisper_transcribe_translate.py entrada_video.mp4 --model-size medium

# - forçar CPU ou GPU
python whisper_transcribe_translate.py entrada_video.mp4 --device cpu --compute-type float32
python whisper_transcribe_translate.py entrada_video.mp4 --device cuda --compute-type float16

# - apontar para outro modelo/endpoint do Ollama
python whisper_transcribe_translate.py entrada_video.mp4 --ollama-model llama3 --ollama-url http://localhost:11434/api/chat
```

## Observações de qualidade e desempenho

* Em **GPU** com VRAM limitada, experimente `--compute-type int8_float16` (CTranslate2 quantiza camadas mantendo qualidade muito boa).
* Em **CPU**, `--compute-type float32` tende a ser mais estável; modelos menores (`small`/`medium`) reduzem tempo e memória.
* `--translate-srt` envia um *prompt* por segmento; para vídeos longos, isso pode levar mais tempo. Use apenas quando precisar de **SRT PT-BR sincronizado**.
* Se você quiser **detecção automática de idioma**, remova `--language-hint en` (ou defina `None`) no `transcribe_whisper`.

Outras possibilidades?

* empacotar em **Docker**;
* expor uma **API FastAPI**;
* integrar com **LangChain** (chain Transcrever→Traduzir→Resumir/Indexar);
* salvar também **VTT** e **CSV** com *timestamps* + texto.
