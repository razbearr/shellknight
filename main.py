#main.py

import os
from groq import Groq
from logger import get_recent_commands, get_cmd_frequency, init_db, update_ml_score
from analyzer import analyze_session
from ml_detector import score_command
from train import train
from dotenv import load_dotenv
import argparse
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from parser import parsehist, seed_db_from_history
import pathlib

console = Console()

def run_scan():
    init_db()
    console.print(Panel("[bold pink]ShellKnight Security Monitor[/bold pink]"))

    commands = get_recent_commands(20)
    table1 = Table(title="Last 20 Commands")
    table1.add_column("Status", style="cyan")
    table1.add_column("Command")

    for entry in commands:
        if entry['flagged']:
            status = f"[red]{entry['severity'].upper()}[/red]"
        else:
            status = "[green]clean[/green]"
        table1.add_row(status, entry['command'])
    console.print(table1)

    table2 = Table(title="Top Commands by Frequency")
    table2.add_column("Frequency")
    table2.add_column("Command")

    for entry in get_cmd_frequency()[:5]:
        table2.add_row(f"{entry['frequency']}x", entry['command'])
    console.print(table2)

    table3 = Table(title="ML Anomaly Detection")
    table3.add_column("Status", style="cyan")
    table3.add_column("Command")
    table3.add_column("Score")
    for entry in commands:
        if entry["timestamp"] is None:
            continue
        result = score_command(entry["command"], entry["timestamp"])
        update_ml_score(entry["command"], entry["timestamp"], result["score"]) 
        flag = "ANOMALY" if result["anomaly"] else "normal"
        if flag == "ANOMALY":
            status = f"[red]{flag}[/red]"
        else:
            status = f"[green]{flag}[/green]"
        table3.add_row(status, entry['command'],f"{result['score']:.4f}")
    console.print(table3)

    ai_result = analyze_session()
    risk = "unknown"
    for line in ai_result.split("\n"):
        if line.startswith("RISK:"):
            risk = line.split(":")[1].strip().lower()
            break
    console.print(Panel(ai_result,title=f"[bold white] AI Session Analysis — {risk.upper()}[/bold white]",border_style="white"))

def run_train():
    train()

def run_seed():
    hist_zsh = pathlib.Path.home() / ".zsh_history"
    hist_bash = pathlib.Path.home() / ".bash_history"
    console.print(Panel("[bold blue]ShellKnight - History Seeder[/bold blue]"))
    
    # count commands before doing anything
    zsh_count = len(parsehist(hist_zsh)) if hist_zsh.exists() else 0
    bash_count = len(parsehist(hist_bash)) if hist_bash.exists() else 0
    total = zsh_count + bash_count
    
    console.print(f"[cyan]Found shell histories:[/cyan]")
    if hist_zsh.exists():
        console.print(f"  ~/.zsh_history  → [green]{zsh_count}[/green] commands")
    if hist_bash.exists():
        console.print(f"  ~/.bash_history → [green]{bash_count}[/green] commands")
    
    console.print(f"\n[yellow]This will:[/yellow]")
    console.print(f"  1. Clear your existing DB")
    console.print(f"  2. Import [bold]{total}[/bold] commands from your shell history")
    console.print(f"  3. Retrain the IsolationForest model on fresh data")
    
    response = input("\nProceed? [y/n]: ")
    if response.lower() != "y":
        console.print("[red]Cancelled.[/red]")
        return
    
    seed_db_from_history()
    console.print("[green]✓ History imported[/green]")
    console.print("[cyan]Retraining model...[/cyan]")
    train()
    console.print("[green]✓ Model retrained. ShellKnight is ready.[/green]")

def run_why():
    commands = get_recent_commands(50)
    seen = set()
    unique_flagged = []
    flagged = [c for c in commands if c['flagged'] == 1]
    for c in flagged:
        if c['command'] not in seen:
            seen.add(c['command'])
            unique_flagged.append(c)
    if not unique_flagged:
        console.print("[yellow]No flagged commands found.[/yellow]")
        return
    load_dotenv()
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    for entry in unique_flagged[:3]:
        prompt = f"""You are a terminal security expert. A shell command was flagged as suspicious.
    Command: {entry['command']}
    Severity: {entry['severity']}
    Reason: {entry['reason']}
    Explain in 3-4 sentences:
    1. What this command does
    2. Why it is dangerous
    3. What an attacker could use it for"""
        response = client.chat.completions.create(model="llama-3.1-8b-instant",max_tokens=300,messages=[{"role": "user", "content": prompt}])
        explanation = response.choices[0].message.content
        severity = entry['severity'] or "unknown"
        if severity in ["critical", "high"]:
            color = "red"
        elif severity == "medium":
            color = "yellow"
        else:
            color = "green"
        title = f"[bold {color}]⚠️  {severity.upper()} — {entry['command']}[/bold {color}]"
        console.print(Panel(explanation,title=title,border_style=color))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
    prog="shellknight",
    description="ShellKnight - Terminal Security Monitor"
)
    subparsers = parser.add_subparsers(dest="command")
    
    subparsers.add_parser("scan", help="Run ML + AI analysis on recent commands")
    subparsers.add_parser("why", help="Explain the last flagged command")
    subparsers.add_parser("train", help="Retrain the ML model on your history")
    subparsers.add_parser("seed", help="Seed DB from shell history and retrain model")
    
    args = parser.parse_args()
    
    if args.command == "scan":
        run_scan()
    elif args.command == "why":
        run_why()
    elif args.command == "train":
        run_train()
    elif args.command == "seed":
        run_seed()
    else:
        parser.print_help()