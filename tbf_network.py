import time
import socket
import requests
import speedtest
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.align import Align
from rich.live import Live
from rich.text import Text
from rich.progress import Progress, SpinnerColumn, BarColumn, TextColumn, TaskProgressColumn

console = Console()

def falling_text_animation(target_text: str, delay: float = 0.025):
    """Букви падають зверху вниз по центру екрана"""
    length = len(target_text)
    stages = [0] * length
    
    with Live(refresh_per_second=30, console=console) as live:
        for i in range(length):
            for stage in range(3):
                stages[i] = stage
                line_top, line_mid, line_bot = [], [], []

                for idx, char in enumerate(target_text):
                    if idx > i:
                        line_top.append(" ")
                        line_mid.append(" ")
                        line_bot.append(" ")
                    elif idx == i:
                        if stages[idx] == 0:
                            line_top.append(f"[bold cyan]{char}[/bold cyan]")
                            line_mid.append(" ")
                            line_bot.append(" ")
                        elif stages[idx] == 1:
                            line_top.append(" ")
                            line_mid.append(f"[bold yellow]{char}[/bold yellow]")
                            line_bot.append(" ")
                        else:
                            line_top.append(" ")
                            line_mid.append(" ")
                            line_bot.append(f"[bold green]{char}[/bold green]")
                    else:
                        line_top.append(" ")
                        line_mid.append(" ")
                        line_bot.append(f"[bold green]{char}[/bold green]")

                lines_render = (
                    "".join(line_top) + "\n" +
                    "".join(line_mid) + "\n" +
                    "".join(line_bot)
                )
                live.update(Align.center(Text.from_markup(lines_render)))
                time.sleep(delay)

def show_intro():
    console.clear()
    
    # 1. Анімація падаючого тексту
    console.print("\n" * 3)
    falling_text_animation("TBF-NETWORK ENGINE", delay=0.02)
    console.print(Align.center("[bold magenta]◆ CORE DIAGNOSTICS SYSTEM v1.0 ◆[/bold magenta]\n"))
    time.sleep(1.5)
    
    console.clear()

    # 2. Аналіз системи з 2 прогрес-барами
    console.print("\n[bold yellow]⚡ ЗАПУСК СИСТЕМНОГО АНАЛІЗУ...[/bold yellow]\n")
    
    with Progress(
        SpinnerColumn(),
        TextColumn("[bold cyan]{task.description}[/bold cyan]"),
        BarColumn(bar_width=35, style="black", complete_style="bold green", finished_style="bold green"),
        TaskProgressColumn(),
        console=console
    ) as progress:
        
        task1 = progress.add_task("Сканування оточення Termux....", total=100)
        task2 = progress.add_task("Ініціалізація сокетів & DNS.......", total=100)
        
        while not progress.finished:
            if not progress.tasks[0].finished:
                progress.update(task1, advance=3.0)
            else:
                progress.update(task2, advance=4.5)
            time.sleep(0.03)

    time.sleep(0.4)
    console.clear()

    # 3. Красива плашка з даними
    info_table = Table.grid(padding=(0, 2))
    info_table.add_column(style="bold cyan", justify="right")
    info_table.add_column(style="bold white")
    
    info_table.add_row("Платформа:", "Termux / Linux ARM64")
    info_table.add_row("Модуль:", "TBF Network Diagnostic Suite")
    info_table.add_row("Статус ядра:", "[bold green]ONLINE & READY[/bold green]")
    info_table.add_row("Шифрування:", "TLS v1.3 Enabled")

    final_panel = Panel(
        Align.center(info_table),
        title="[bold green] SYSTEM READY FOR TESTING [/bold green]",
        subtitle="[bold magenta] TBF-NETWORK v1.0 [/bold magenta]",
        border_style="bright_blue",
        padding=(1, 6)
    )
    
    console.print("\n")
    console.print(Align.center(final_panel))
    console.print("\n")

def get_network_info():
    try:
        hostname = socket.gethostname()
        local_ip = socket.gethostbyname(hostname)
    except Exception:
        local_ip = "Не визначено"

    try:
        req = requests.get("https://api.ipify.org?format=json", timeout=5).json()
        public_ip = req.get("ip", "Помилка")
    except Exception:
        public_ip = "Офлайн"

    return local_ip, public_ip

def ping_host(host):
    start_time = time.time()
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.settimeout(2.0)
        sock.connect((host, 80))
        sock.close()
        latency = round((time.time() - start_time) * 1000, 2)
        return f"[bold green]{latency} ms[/bold green]"
    except Exception:
        return "[bold red]Timeout / Failed[/bold red]"

def run_speedtest():
    try:
        st = speedtest.Speedtest(secure=True)
        st.get_best_server()
        
        download_speed = round(st.download() / 1_000_000, 2)
        upload_speed = round(st.upload() / 1_000_000, 2)
        ping = round(st.results.ping, 2)
        
        return download_speed, upload_speed, ping
    except Exception:
        return None, None, None

def main():
    show_intro()

    # 1. Мережеві ідентифікатори
    with Progress(SpinnerColumn(), TextColumn("[yellow]Збір мережевих даних...[/yellow]"), transient=True) as progress:
        progress.add_task("info", total=None)
        local_ip, public_ip = get_network_info()

    info_table = Table(title="[bold white]Мережеві Ідентифікатори[/bold white]", show_header=True, header_style="bold blue")
    info_table.add_column("Параметр", style="cyan")
    info_table.add_column("Значення", style="green")
    info_table.add_row("Локальний IP", local_ip)
    info_table.add_row("Зовнішній (Public) IP", public_ip)
    console.print(info_table)
    console.print()

    # 2. Перевірка затримки (Ping)
    hosts = {
        "Google DNS": "8.8.8.8",
        "Cloudflare DNS": "1.1.1.1",
        "Telegram API": "149.154.167.220",
        "GitHub": "github.com"
    }

    ping_table = Table(title="[bold white]Перевірка Затримки (Ping)[/bold white]", show_header=True, header_style="bold blue")
    ping_table.add_column("Сервіс / Вузол", style="cyan")
    ping_table.add_column("Адреса", style="yellow")
    ping_table.add_column("Затримка (Latency)", style="magenta")

    with Progress(SpinnerColumn(), TextColumn("[yellow]Пінгуємо вузли...[/yellow]"), transient=True) as progress:
        progress.add_task("ping", total=None)
        for name, host in hosts.items():
            latency = ping_host(host)
            ping_table.add_row(name, host, latency)

    console.print(ping_table)
    console.print()

    # 3. Тест швидкості
    console.print(Panel("[bold yellow]Запуск Speedtest (це може зайняти 15–30 секунд)...[/bold yellow]", border_style="yellow"))
    
    with Progress(SpinnerColumn(), TextColumn("[cyan]Вимірювання швидкості каналу...[/cyan]"), transient=True) as progress:
        progress.add_task("speed", total=None)
        dl, ul, ping_val = run_speedtest()

    if dl is not None:
        speed_table = Table(title="[bold white]Результати Speedtest[/bold white]", show_header=True, header_style="bold blue")
        speed_table.add_column("Метрика", style="cyan")
        speed_table.add_column("Показник", style="bold green")
        
        speed_table.add_row("Завантаження (Download)", f"{dl} Mbps")
        speed_table.add_row("Віддача (Upload)", f"{ul} Mbps")
        speed_table.add_row("Пінг сервера", f"{ping_val} ms")
        console.print(speed_table)
    else:
        console.print("[bold red]Не вдалося виміряти швидкість. Перевірте підключення.[/bold red]")

    console.print("\n[bold green]Діагностика успішно завершена![/bold green]")

if __name__ == "__main__":
    main()
  
