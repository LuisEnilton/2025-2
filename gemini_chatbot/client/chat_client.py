from dotenv import load_dotenv
import os
import requests
import json
import uuid

from rich.console import Console
from rich.panel import Panel
from rich.markdown import Markdown
from rich import print as rprint

load_dotenv()

class ChatClient:
    def __init__(self):
        self.base_url = os.getenv("API_URL", "http://localhost:8000")
        self.session_id = str(uuid.uuid4())
        self.console = Console()
        
    def start_chat(self):
        """Inicia a sessão de chat"""
        self.console.print(
            Panel.fit(
                "[bold blue]🤖 Gemini ChatBot[/bold blue]\n"
                f"[dim]Sessão: {self.session_id}[/dim]\n"
                "Digite 'sair' para encerrar ou 'ajuda' para comandos",
                border_style="green"
            )
        )
        
        while True:
            try:
                user_input = self.console.input("\n[bold yellow]Você:[/bold yellow] ").strip()
                
                if user_input.lower() in ['sair', 'exit', 'quit']:
                    self.console.print("[green]Até logo! 👋[/green]")
                    break
                elif user_input.lower() in ['ajuda', 'help']:
                    self._show_help()
                    continue
                elif user_input.lower() == 'historico':
                    self._show_history()
                    continue
                elif not user_input:
                    continue
                
                with self.console.status("[bold green]Aguarde...[/bold green]", spinner="dots") as status:
                    # Enviar mensagem para API
                    response = self._send_message(user_input)
                self._display_response(response)
                
            except KeyboardInterrupt:
                self.console.print("\n[red]Interrompido pelo usuário[/red]")
                break
            except Exception as e:
                self.console.print(f"[red]Erro: {str(e)}[/red]")
    
    def _send_message(self, message: str) -> dict:
        """Envia mensagem para a API"""
        payload = {
            "message": message,
            "session_id": self.session_id
        }
        
        response = requests.post(
            f"{self.base_url}/chat",
            json=payload,
            headers={"Content-Type": "application/json"}
        )
        
        if response.status_code != 200:
            raise Exception(f"Erro na API: {response.text}")
        
        return response.json()
    
    def _display_response(self, response: dict):
        """Exibe a resposta formatada"""
        response_text = response.get("response", "Sem resposta")
        tokens_used = response.get("tokens_used", 0)
        
        # Usar Markdown para melhor formatação
        md = Markdown(response_text)
        
        self.console.print(
            Panel(
                md,
                title="[bold green]🤖 Assistente[/bold green]",
                title_align="left",
                border_style="blue",
                subtitle=f"[dim]Tokens usados: {tokens_used}[/dim]"
            )
        )
    
    def _show_help(self):
        """Mostra ajuda dos comandos"""
        help_text = """
[b]Comandos disponíveis:[/b]
• [yellow]sair[/yellow] - Encerra o chat
• [yellow]historico[/yellow] - Mostra histórico da conversa
• [yellow]ajuda[/yellow] - Mostra esta mensagem

[b]Exemplos de perguntas:[/b]
• "Explique o que é machine learning"
• "Como funciona um neural network?"
• "Me ajude a debugar um código Python"
"""
        self.console.print(Panel(help_text, title="[bold]Ajuda[/bold]", border_style="yellow"))
    
    def _show_history(self):
        """Mostra histórico da conversa"""
        try:
            response = requests.get(f"{self.base_url}/conversations/{self.session_id}")
            if response.status_code == 200:
                conversation = response.json()
                self.console.print("\n[bold cyan]📜 Histórico da Conversa:[/bold cyan]")
                for msg in conversation.get("messages", []):
                    role = "👤 Você" if msg["role"] == "user" else "🤖 Assistente"
                    self.console.print(f"\n[bold]{role}:[/bold] {msg['content']}")
                    self.console.print(f"[dim]{msg['timestamp']}[/dim]")
            else:
                self.console.print("[yellow]Nenhum histórico encontrado[/yellow]")
        except Exception as e:
            self.console.print(f"[red]Erro ao buscar histórico: {str(e)}[/red]")

if __name__ == "__main__":
    client = ChatClient()
    client.start_chat()