from rich.prompt import Prompt
from rich.console import Console
from rich.panel import Panel

def show_menu():
    """Displays the interactive menu and processes user choice."""
    console = Console()

    # Define menu options
    options = [
        "Opção 1: Exibir informações",
        "Opção 2: Configurar o sistema",
        "Opção 3: Executar uma tarefa",
        "Sair"
    ]

    while True:
        # Display the panel with the menu title
        console.print(Panel("Selecione uma opção:", title="Menu Principal"))
        
        # Now, use Prompt.ask() with a simple string for the prompt
        # The choices argument will handle the list display
        choice = Prompt.ask(
            "Selecione uma opção",
            choices=options,
            console=console
        )

        # Handle user choice
        if choice == "Opção 1: Exibir informações":
            console.print("\n[bold green]Você escolheu a Opção 1.[/bold green]")
            console.print("Exibindo informações importantes...\n")
        elif choice == "Opção 2: Configurar o sistema":
            console.print("\n[bold yellow]Você escolheu a Opção 2.[/bold yellow]")
            console.print("Iniciando o processo de configuração...\n")
        elif choice == "Opção 3: Executar uma tarefa":
            console.print("\n[bold blue]Você escolheu a Opção 3.[/bold blue]")
            console.print("Executando a tarefa selecionada...\n")
        elif choice == "Sair":
            console.print("\n[bold red]Saindo do programa. Tchau![/bold red]")
            break

# Call the function to run the menu
show_menu()