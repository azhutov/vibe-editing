#!/usr/bin/env python3
"""Instruct Agent

Monitors a folder for new audio files, transcribes them with `llm`,
generates integration instructions, writes results to disk, and
signals a waiting Cursor workflow (Integrator Agent) via a named pipe.
"""
from __future__ import annotations

import os
import subprocess
import sys
import time
import yaml
from pathlib import Path
from typing import Optional

from rich.console import Console
from rich.markdown import Markdown

# ── Config ────────────────────────────────────────────────────────────────────
config_data = yaml.safe_load(open('./agents/config.yaml'))
paths_config = config_data.get('paths', {})
llm_config = config_data.get('llm_settings', {})
agent_config = config_data.get('agent_settings', {})

PROJECT_ROOT = Path(__file__).parent.parent
FOLDER = PROJECT_ROOT / paths_config.get('voice_notes_folder', 'data/voice-notes-demo')
TRANSCRIPTS = PROJECT_ROOT / paths_config.get('transcripts_folder', 'data/transcripts')
INSTRUCTIONS = PROJECT_ROOT / paths_config.get('integration_instructions_folder', 'data/integration_instructions')
PROMPT_FILE = PROJECT_ROOT / paths_config.get('integration_prompt_file', 'prompts/integrate_instructions.md')
PIPE = Path(paths_config.get('pipe_path', '/tmp/cursor_agent_pipe'))

MODEL = llm_config.get('model', 'gemini-2.5-flash-preview-04-17')
THINKING_BUDGET_TRANSCRIBE = int(llm_config.get('thinking_budget_transcribe', 1024))
THINKING_BUDGET_INTEGRATION = int(llm_config.get('thinking_budget_integration', 0))
TEMP = str(llm_config.get('temperature', 0.1))

POLL = int(agent_config.get('poll_interval_seconds', 2))
TRANSCRIBE_PROMPT = agent_config.get('transcribe_prompt')


# ── Setup ─────────────────────────────────────────────────────────────────────
console = Console()
console.clear()
console.rule("[bold cyan]Instruct Agent[/bold cyan]")

if PIPE.exists() and not PIPE.is_fifo():
    console.print(f"[bold red]Error[/bold red]: Pipe {PIPE} exists and is not a FIFO. Please remove it and restart.")
    sys.exit(1)
if not PIPE.exists():
    try:
        os.mkfifo(PIPE)
        console.print(f"[green]✓ Created pipe for Integrator Agent:[/green] {PIPE}")
    except OSError as e:
        console.print(f"[bold red]Error[/bold red]: Could not create pipe {PIPE}: {e}")
        sys.exit(1)

try:
    INTEGRATION_PROMPT = PROMPT_FILE.read_text()
except FileNotFoundError:
    console.print(f"[bold red]Prompt file missing[/bold red]: {PROMPT_FILE}")
    sys.exit(1)

seen_deleted_folders = set() # For tracking folder state

# ── Helpers ───────────────────────────────────────────────────────────────────

def run_command(cmd: list[str]) -> tuple[str, str, int]:
    """Run a shell command, return stdout, stderr, and return‑code."""
    p = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    out, err = p.communicate()
    return out.strip(), err.strip(), p.returncode


def transcribe(audio: Path) -> Optional[str]:
    console.print(f"  [dim]Transcribing '{audio.name}'...[/dim]")
    out, err, rc = run_command(["llm", "-m", MODEL, "-o", "thinking_budget", str(THINKING_BUDGET_TRANSCRIBE), TRANSCRIBE_PROMPT, "-a", str(audio)])
    if rc == 0:
        console.print(f"  [green]✓ Transcription successful.[/green]")
        return out
    else:
        console.print(f"  [red]Transcription failed.[/red] Error: {err or 'Unknown error'}")
        return None


def generate_integration_directives(text: str) -> Optional[str]:
    console.print(f"  [dim]Generating integration directives...[/dim]")
    full_prompt_for_llm = f"{INTEGRATION_PROMPT}\n\n**[Your Raw Thoughts/Dictation]**\n{text}\n---"
    out, err, rc = run_command(["llm", "-m", MODEL, "-o", "temperature", TEMP, "-o", "thinking_budget", str(THINKING_BUDGET_INTEGRATION), full_prompt_for_llm])
    if rc == 0:
        console.print(f"  [green]✓ Integration directives generated.[/green]")
        return out
    else:
        console.print(f"  [red]Integration directive generation failed.[/red] Error: {err or 'Unknown error'}")
        return None


def notify_integrator_agent(path: Path) -> None:
    console.print(f"  [dim]Notifying Integrator Agent via pipe: {PIPE}...[/dim]")
    try:
        with PIPE.open("w") as fifo:
            fifo.write(f"integration_instructions_created {path}\n")
            fifo.flush()
        console.print(f"  [green]✓ Notification sent to Integrator Agent.[/green]")
    except Exception as e:
        console.print(f"  [red]Failed to write to pipe {PIPE}: {e}[/red]")


def process_voice_note(file: Path) -> None:
    console.print(f"\n[bold magenta]Processing new file:[/bold magenta] {file.name}")
    text = transcribe(file)
    if not text:
        return

    TRANSCRIPTS.mkdir(parents=True, exist_ok=True)
    t_path = TRANSCRIPTS / f"{file.stem}.txt"
    t_path.write_text(text)
    console.print(f"  [dim]Transcript saved: {t_path.name}[/dim]")

    integration_directives = generate_integration_directives(text)
    if not integration_directives:
        return

    INSTRUCTIONS.mkdir(parents=True, exist_ok=True)
    i_path = INSTRUCTIONS / f"{file.stem}_integration_instructions.txt"
    i_path.write_text(integration_directives)
    console.print(f"  [dim]Instructions saved: {i_path.name}[/dim]")

    console.print("\n[bold]Generated Integration Instructions:[/bold]")
    console.print(Markdown(integration_directives))
    notify_integrator_agent(i_path)
    console.print(f"[cyan]▶ Instruct Agent now idle, awaiting next audio file...[/cyan]")

def wait_for_file_sync(path: Path, interval: float = 1.0, stable_checks: int = 5):
    last_size = -1
    stable = 0
    while stable < stable_checks:
        try:
            size = path.stat().st_size if path.exists() else -1
        except FileNotFoundError:
            time.sleep(interval)
            continue
        if size != -1 and size == last_size: # Ensure file exists before comparing size
            stable += 1
        else:
            stable = 0
            last_size = size
        time.sleep(interval)

def watch(folder: Path) -> None:
    if not folder.exists():
        console.print(f"[bold red]Monitored folder not found[/bold red]: {folder}")
        sys.exit(1)

    console.print("[dim]Press Ctrl+C to stop.[/dim]")
    
    seen = set()
    try:
        seen.update(f for f in folder.iterdir() if f.is_file() and not f.name.startswith('.'))
    except FileNotFoundError:
        console.print(f"[yellow]Warning:[/yellow] Monitored folder [bold purple]{folder}[/bold purple] not accessible at startup. Will retry.")
    except Exception as e:
        console.print(f"[red]Error scanning folder [bold purple]{folder}[/bold purple] at startup: {e}[/red]")

    watch_status_text = f"[bold green]Watching for new voice notes [/bold green]"

    with console.status(watch_status_text, spinner="dots"):
        while True:
            current_files = set()
            try:
                if not folder.exists():
                    if folder not in seen_deleted_folders:
                        console.print(f"[bold red]Error:[/bold red] Monitored folder [bold purple]{folder}[/bold purple] no longer exists. Please ensure it's available.")
                        seen_deleted_folders.add(folder)
                    time.sleep(POLL * 5)
                    continue
                
                if folder in seen_deleted_folders:
                    console.print(f"[green]✓ Monitored folder [bold purple]{folder}[/bold purple] is available again.[/green]")
                    seen_deleted_folders.remove(folder)
                    seen.clear()
                    seen.update(f for f in folder.iterdir() if f.is_file() and not f.name.startswith('.'))

                current_files.update(f for f in folder.iterdir() if f.is_file() and not f.name.startswith('.'))
            
            except FileNotFoundError:
                if folder not in seen_deleted_folders:
                     console.print(f"[yellow]Warning:[/yellow] Monitored folder [bold purple]{folder}[/bold purple] inaccessible during scan. Will retry.")
                     seen_deleted_folders.add(folder)
                time.sleep(POLL)
                continue
            except Exception as e:
                console.print(f"[red]Error scanning folder [bold purple]{folder}[/bold purple]: {e}[/red]")
                time.sleep(POLL)
                continue

            new_files = current_files - seen
            if new_files:
                for item in new_files:
                    # wait until the file has finished syncing
                    wait_for_file_sync(item)
                    process_voice_note(item)
            
            seen = current_files
            time.sleep(POLL)


if __name__ == "__main__":
    try:
        watch(FOLDER)
    except KeyboardInterrupt:
        console.print("\n[bold cyan]👋 Instruct Agent stopped by user. Bye![/bold cyan]")
    except Exception as e:
        console.print(f"\n[bold red]An unexpected error occurred in Instruct Agent:[/bold red] {e}")
    finally:
        pass