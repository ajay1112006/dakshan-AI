#!/usr/bin/env python3
"""
Dakshan AI
A sleek, feature-rich interactive CLI assistant powered by Dakshan AI.
"""

import os
import sys
import time
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv, set_key

# Force UTF-8 encoding for Windows terminal output
if sys.platform == "win32":
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

# Load environment variables from .env if present
env_path = Path(__file__).resolve().parent / ".env"
load_dotenv(dotenv_path=env_path)

try:
    from groq import Groq, APIError, AuthenticationError, RateLimitError
    from rich.console import Console
    from rich.panel import Panel
    from rich.table import Table
    from rich.markdown import Markdown
    from rich.live import Live
    from rich.text import Text
    from rich.prompt import Prompt, Confirm
except ImportError:
    print("Error: Missing required packages.")
    print("Please run: pip install -r requirements.txt")
    sys.exit(1)

console = Console()

# Filter out non-chat models (like audio/whisper or guard models)
NON_CHAT_KEYWORDS = ["whisper", "guard"]

def fetch_available_models(client: Groq) -> dict:
    """Fetch active chat models from Groq API or return sensible defaults."""
    fallback_models = {
        "1": {"id": "openai/gpt-oss-120b", "name": "Dakshan AI Model", "desc": "High capacity general reasoning"},
        "2": {"id": "qwen/qwen3.8-27b", "name": "Qwen 3.8 27B", "desc": "Fast, smart multilingual model"},
        "3": {"id": "openai/gpt-oss-20b", "name": "OpenAI GPT-OSS 20B", "desc": "Fast low-latency inference"},
        "4": {"id": "allam-2-7b", "name": "Allam 2 7B", "desc": "Lightweight model"},
    }

    try:
        remote_models = client.models.list().data
        chat_models = [
            m.id for m in remote_models 
            if getattr(m, 'active', True) and not any(kw in m.id.lower() for kw in NON_CHAT_KEYWORDS)
        ]
        if not chat_models:
            return fallback_models

        # Put strongest / popular models at top
        preferred_order = ["openai/gpt-oss-120b", "qwen/qwen3.8-27b", "openai/gpt-oss-20b", "allam-2-7b"]
        chat_models.sort(key=lambda m: preferred_order.index(m) if m in preferred_order else 99)

        model_dict = {}
        for idx, mid in enumerate(chat_models, start=1):
            name = "Dakshan AI Model" if idx == 1 else (mid.split("/")[-1].replace("-", " ").title() if "/" in mid else mid)
            desc = "Available on your Dakshan AI tier"
            if "120b" in mid:
                desc = "Highest capability & reasoning (Recommended)"
            elif "27b" in mid:
                desc = "Fast, highly capable conversational model"
            elif "20b" in mid:
                desc = "Fast lightweight conversational model"
            model_dict[str(idx)] = {"id": mid, "name": name, "desc": desc}

        return model_dict
    except Exception:
        return fallback_models

DEFAULT_SYSTEM_PROMPT = (
    "You are Dakshan AI, a helpful, knowledgeable, and concise AI assistant running inside a terminal. "
    "Format your answers with clean Markdown, including code blocks with syntax highlighting where applicable."
)



def ensure_api_key() -> str:
    """Ensure GROQ_API_KEY is available or prompt user to configure it."""
    api_key = os.getenv("GROQ_API_KEY", "").strip()

    if not api_key or api_key == "your_groq_api_key_here":
        console.print(
            Panel(
                "[bold yellow]GROQ_API_KEY not found in environment or .env[/bold yellow]\n\n"
                "Get your free API key at: [link=https://console.groq.com/keys]https://console.groq.com/keys[/link]",
                title="🔑 Groq API Key Setup",
                border_style="yellow",
            )
        )
        api_key = Prompt.ask("[bold cyan]Enter your Groq API Key[/bold cyan]", password=True).strip()
        if not api_key:
            console.print("[bold red]API key cannot be empty. Exiting.[/bold red]")
            sys.exit(1)

        should_save = Confirm.ask("Do you want to save this key to .env for future sessions?", default=True)
        if should_save:
            if not env_path.exists():
                env_path.touch()
            set_key(str(env_path), "GROQ_API_KEY", api_key)
            console.print("[bold green]API key saved to .env file successfully![/bold green]\n")
        os.environ["GROQ_API_KEY"] = api_key

    return api_key


def print_banner(current_model_id: str):
    """Print the startup banner."""
    grid = Table.grid(expand=True)
    grid.add_column(justify="left")
    grid.add_column(justify="right")
    grid.add_row(
        "[bold cyan]⚡ Dakshan AI[/bold cyan]",
        "[dim]Model:[/dim] [bold green]Dakshan AI Model[/bold green]",
    )
    grid.add_row(
        "[dim]Type your message, or [bold]/help[/bold] for commands[/dim]",
        "[dim]Type [bold]/exit[/bold] or [bold]Ctrl+C[/bold] to quit[/dim]",
    )

    console.print(
        Panel(
            grid,
            border_style="cyan",
            padding=(0, 1),
        )
    )


def print_help():
    """Print the available CLI commands."""
    table = Table(title="Available Chatbot Commands", border_style="dim", header_style="bold magenta")
    table.add_column("Command", style="bold cyan", width=16)
    table.add_column("Description", style="white")

    table.add_row("/help", "Show this help table")
    table.add_row("/model", "Switch or view LLM models (Llama 3.3, DeepSeek, etc.)")
    table.add_row("/system", "Change or view the system instructions")
    table.add_row("/clear", "Clear conversation history and start fresh")
    table.add_row("/save", "Export current chat history to a Markdown file")
    table.add_row("/history", "View count of conversation turns")
    table.add_row("/exit, /quit", "Exit the terminal chatbot")

    console.print(table)
    console.print()


def select_model(current_model_id: str, available_models: dict) -> str:
    """Allow user to switch to a different model."""
    table = Table(title="Select Dakshan AI Model", border_style="dim", header_style="bold cyan")
    table.add_column("#", style="bold yellow", width=4)
    table.add_column("Model Name", style="bold green", width=28)
    table.add_column("ID", style="dim", width=36)
    table.add_column("Description", style="white")

    for k, v in available_models.items():
        active = " (Active)" if v["id"] == current_model_id else ""
        table.add_row(k, f"{v['name']}{active}", v["id"], v["desc"])

    console.print(table)
    choice = Prompt.ask(
        "Enter model number, model ID, or press Enter to keep current",
        default="",
        show_default=False,
    ).strip()

    if not choice:
        console.print(f"[dim]Keeping active model:[/dim] [bold green]{current_model_id}[/bold green]\n")
        return current_model_id

    if choice in available_models:
        new_model = available_models[choice]["id"]
        console.print(f"[bold green]Switched model to:[/bold green] {new_model}\n")
        return new_model

    # Allow custom model ID
    console.print(f"[bold green]Custom model set to:[/bold green] {choice}\n")
    return choice


def save_transcript(messages: list[dict], model_id: str):
    """Save the conversation transcript to a markdown file."""
    if len(messages) <= 1:
        console.print("[yellow]No conversation to save yet.[/yellow]\n")
        return

    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"chat_transcript_{timestamp}.md"
    file_path = Path(__file__).resolve().parent / filename

    content_lines = [
        f"# Dakshan AI Chat Transcript",
        f"- **Date**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}",
        f"- **Model**: Dakshan AI Model (`{model_id}`)",
        "",
        "---",
        "",
    ]

    for msg in messages:
        role = msg["role"]
        content = msg["content"]
        if role == "system":
            content_lines.append(f"> **System Prompt**: {content}\n")
        elif role == "user":
            content_lines.append(f"### 🧑 User\n\n{content}\n")
        elif role == "assistant":
            content_lines.append(f"### 🤖 Dakshan AI\n\n{content}\n")

    file_path.write_text("\n".join(content_lines), encoding="utf-8")
    console.print(f"[bold green]Conversation exported to:[/bold green] [bold cyan]{file_path.name}[/bold cyan]\n")


def stream_response(client: Groq, model: str, messages: list[dict]) -> str:
    """Stream response with live markdown rendering."""
    accumulated_text = ""
    start_time = time.time()
    first_token_time = None
    token_count = 0

    console.print("\n[bold green]Dakshan AI[/bold green] [dim]• streaming...[/dim]")

    try:
        # Use Rich Live display with Markdown for progressive rendering
        with Live(
            Markdown(""),
            console=console,
            refresh_per_second=15,
            vertical_overflow="visible",
        ) as live:
            response_stream = client.chat.completions.create(
                model=model,
                messages=messages,
                stream=True,
                temperature=0.7,
            )

            for chunk in response_stream:
                delta = chunk.choices[0].delta.content or ""
                if delta:
                    if first_token_time is None:
                        first_token_time = time.time()
                    accumulated_text += delta
                    token_count += 1
                    live.update(Markdown(accumulated_text))

        # Performance summary
        total_time = max(time.time() - start_time, 0.001)
        ttft = (first_token_time - start_time) if first_token_time else 0.0
        tps = token_count / total_time if token_count > 0 else 0.0

        stats_text = (
            f"[dim]Time: {total_time:.2f}s | TTFT: {ttft*1000:.0f}ms | ~{tps:.1f} tokens/s[/dim]\n"
        )
        console.print(stats_text)

        return accumulated_text

    except AuthenticationError:
        console.print(
            "\n[bold red]Authentication Error:[/bold red] Invalid Groq API Key. "
            "Please check your key at https://console.groq.com/keys\n"
        )
        return ""
    except RateLimitError as e:
        console.print(f"\n[bold red]Rate Limit Exceeded:[/bold red] {e}\n")
        return ""
    except APIError as e:
        console.print(f"\n[bold red]Groq API Error:[/bold red] {e}\n")
        return ""
    except KeyboardInterrupt:
        console.print("\n[yellow][Generation interrupted by user][/yellow]\n")
        return accumulated_text
    except Exception as e:
        console.print(f"\n[bold red]Unexpected error:[/bold red] {e}\n")
        return ""


def main():
    api_key = ensure_api_key()
    client = Groq(api_key=api_key)

    available_models = fetch_available_models(client)
    default_key = next(iter(available_models.keys()), "1")
    current_model = available_models[default_key]["id"]
    system_prompt = DEFAULT_SYSTEM_PROMPT

    messages: list[dict] = [{"role": "system", "content": system_prompt}]

    print_banner(current_model)

    while True:
        try:
            user_input = Prompt.ask("\n[bold cyan]You[/bold cyan]").strip()

            if not user_input:
                continue

            # Command routing
            if user_input.lower() in ["/exit", "/quit", "exit", "quit"]:
                console.print("\n[bold yellow]Goodbye! Have a great day.[/bold yellow]\n")
                break

            if user_input.lower() == "/help":
                print_help()
                continue

            if user_input.lower() == "/clear":
                messages = [{"role": "system", "content": system_prompt}]
                console.clear()
                print_banner(current_model)
                console.print("[bold green]Conversation history cleared.[/bold green]\n")
                continue

            if user_input.lower() == "/model":
                current_model = select_model(current_model, available_models)
                continue

            if user_input.lower() == "/history":
                user_turns = sum(1 for m in messages if m["role"] == "user")
                console.print(
                    f"[dim]History contains [bold cyan]{len(messages)}[/bold cyan] total messages "
                    f"([bold cyan]{user_turns}[/bold cyan] user turns).[/dim]\n"
                )
                continue

            if user_input.lower() == "/save":
                save_transcript(messages, current_model)
                continue

            if user_input.lower() == "/system":
                console.print(
                    Panel(
                        f"[italic]{system_prompt}[/italic]",
                        title="Current System Prompt",
                        border_style="magenta",
                    )
                )
                new_system = Prompt.ask(
                    "Enter new system prompt (leave blank to keep current)",
                    default="",
                    show_default=False,
                ).strip()
                if new_system:
                    system_prompt = new_system
                    messages[0] = {"role": "system", "content": system_prompt}
                    console.print("[bold green]System prompt updated successfully![/bold green]\n")
                continue

            # Regular chat exchange
            messages.append({"role": "user", "content": user_input})
            assistant_text = stream_response(client, current_model, messages)

            if assistant_text:
                messages.append({"role": "assistant", "content": assistant_text})
            else:
                # If generation failed or was empty, pop the unanswered user question
                messages.pop()

        except (KeyboardInterrupt, EOFError):
            console.print("\n")
            if Confirm.ask("Do you want to exit the chatbot?", default=True):
                console.print("[bold yellow]Goodbye![/bold yellow]\n")
                break
            else:
                continue


if __name__ == "__main__":
    main()
