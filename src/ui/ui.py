"""
Módulo de interface de linha de comando usando Rich
"""
import sys
import os

# Configura encoding UTF-8 para Windows
if sys.platform == 'win32':
    try:
        import codecs
        if hasattr(sys.stdout, 'buffer'):
            sys.stdout = codecs.getwriter('utf-8')(sys.stdout.buffer, 'strict')
        if hasattr(sys.stderr, 'buffer'):
            sys.stderr = codecs.getwriter('utf-8')(sys.stderr.buffer, 'strict')
        os.environ['PYTHONIOENCODING'] = 'utf-8'
    except:
        pass

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.layout import Layout
from rich.live import Live
from rich.text import Text
from rich import box
from datetime import datetime
from typing import Dict, List, Optional
import time


class UI:
    def __init__(self):
        # Configura console com encoding UTF-8
        try:
            self.console = Console(force_terminal=True, encoding='utf-8')
        except:
            self.console = Console()
        self.last_update = None
    
    def print_header(self):
        """Imprime o cabeçalho do programa"""
        header = Panel.fit(
            "[bold cyan]🎰 BLAZE DOUBLE ANALYZER 🎰[/bold cyan]\n"
            "[yellow]Sistema de Análise e Previsão de Padrões[/yellow]",
            border_style="cyan"
        )
        self.console.print(header)
    
    def print_status(self, status: str, color: str = "white"):
        """Imprime um status"""
        timestamp = datetime.now().strftime("%H:%M:%S")
        self.console.print(f"[{color}][{timestamp}][/{color}] {status}")
    
    def print_success(self, message: str):
        """Imprime mensagem de sucesso"""
        self.print_status(f"✅ {message}", "green")
    
    def print_error(self, message: str):
        """Imprime mensagem de erro"""
        self.print_status(f"❌ {message}", "red")
    
    def print_warning(self, message: str):
        """Imprime mensagem de aviso"""
        self.print_status(f"⚠️  {message}", "yellow")
    
    def print_info(self, message: str):
        """Imprime mensagem informativa"""
        self.print_status(f"ℹ️  {message}", "blue")
    
    def display_game_history(self, history: List[Dict], limit: int = 24):
        """Exibe o histórico de jogos destacando as cores"""
        table = Table(title="Histórico de Cores", box=box.ROUNDED)
        table.add_column("Pos", style="cyan", width=4, justify="center")
        table.add_column("Cor", style="bold", width=12, justify="center")
        table.add_column("Número", style="dim yellow", width=8, justify="center")
        
        for i, game in enumerate(history[:limit], 1):
            color = game.get('color', '')
            number = game.get('number')
            
            # Define cor e símbolo baseado na cor
            if color == 'red':
                color_display = "[bold red]🔴 VERMELHO[/bold red]"
                color_code = "red"
            elif color == 'black':
                color_display = "[bold white on black]⚫ PRETO[/bold white on black]"
                color_code = "white on black"
            elif color == 'white':
                color_display = "[bold black on white]⚪ BRANCO[/bold black on white]"
                color_code = "black on white"
            else:
                color_display = "[dim]? DESCONHECIDO[/dim]"
                color_code = "dim"
            
            number_display = str(number) if number is not None else "[dim]N/A[/dim]"
            
            table.add_row(str(i), color_display, number_display)
        
        self.console.print(table)
    
    def display_prediction(self, prediction: str, confidence: float, patterns: List[Dict]):
        """Exibe a previsão gerada"""
        color_names = {
            'red': '🔴 Vermelho',
            'black': '⚫ Preto',
            'white': '⚪ Branco'
        }
        
        color_display = color_names.get(prediction, prediction)
        
        # Determina a cor baseada na confiança
        if confidence >= 0.8:
            conf_color = "green"
            conf_emoji = "🔥"
        elif confidence >= 0.6:
            conf_color = "yellow"
            conf_emoji = "⚡"
        else:
            conf_color = "red"
            conf_emoji = "⚠️"
        
        panel = Panel(
            f"[bold]{conf_emoji} Previsão: {color_display}[/bold]\n"
            f"[{conf_color}]Confiança: {confidence*100:.1f}%[/{conf_color}]\n\n"
            f"[dim]Padrões identificados: {len(patterns)}[/dim]",
            title="🎯 Previsão",
            border_style=conf_color
        )
        self.console.print(panel)
        
        # Exibe os padrões identificados
        if patterns:
            pattern_table = Table(box=box.SIMPLE, show_header=False)
            pattern_table.add_column("Tipo", style="cyan")
            pattern_table.add_column("Descrição", style="white")
            pattern_table.add_column("Confiança", style="yellow")
            
            for pattern in patterns:
                pattern_table.add_row(
                    pattern.get('type', 'N/A'),
                    pattern.get('pattern', 'N/A'),
                    f"{pattern.get('confidence', 0)*100:.1f}%"
                )
            
            self.console.print(pattern_table)
    
    def display_statistics(self, stats: Dict):
        """Exibe estatísticas do bot"""
        win_rate = stats.get('win_rate', 0)
        total_bets = stats.get('total_bets', 0)
        wins = stats.get('wins', 0)
        losses = stats.get('losses', 0)
        profit = stats.get('total_profit', 0)
        
        # Determina cor da taxa de acerto
        if win_rate >= 60:
            rate_color = "green"
        elif win_rate >= 50:
            rate_color = "yellow"
        else:
            rate_color = "red"
        
        # Determina cor do lucro
        profit_color = "green" if profit >= 0 else "red"
        profit_symbol = "💰" if profit >= 0 else "💸"
        
        stats_text = (
            f"[bold]Total de Apostas:[/bold] {total_bets}\n"
            f"[bold]Vitórias:[/bold] [green]{wins}[/green] | [bold]Derrotas:[/bold] [red]{losses}[/red]\n"
            f"[bold]Taxa de Acerto:[/bold] [{rate_color}]{win_rate:.2f}%[/{rate_color}]\n"
            f"[bold]Lucro Total:[/bold] [{profit_color}]{profit_symbol} R$ {profit:.2f}[/{profit_color}]"
        )
        
        panel = Panel(
            stats_text,
            title="📊 Estatísticas",
            border_style="blue"
        )
        self.console.print(panel)
    
    def display_bet_result(self, predicted: str, actual: str, result: str, confidence: float):
        """Exibe o resultado de uma aposta"""
        color_names = {
            'red': '🔴 Vermelho',
            'black': '⚫ Preto',
            'white': '⚪ Branco'
        }
        
        predicted_display = color_names.get(predicted, predicted)
        actual_display = color_names.get(actual, actual)
        
        if result == "WIN":
            result_text = f"[bold green]✅ VITÓRIA![/bold green]"
            border_color = "green"
        else:
            result_text = f"[bold red]❌ DERROTA[/bold red]"
            border_color = "red"
        
        panel = Panel(
            f"{result_text}\n\n"
            f"[bold]Previsão:[/bold] {predicted_display}\n"
            f"[bold]Resultado:[/bold] {actual_display}\n"
            f"[bold]Confiança:[/bold] {confidence*100:.1f}%",
            title="🎲 Resultado da Aposta",
            border_style=border_color
        )
        self.console.print(panel)
    
    def display_game_state(self, state: Dict):
        """Exibe o estado atual do jogo com as últimas cores"""
        timer_text = state.get('timer_text', 'Desconhecido')
        is_betting = state.get('is_betting_period', False)
        recent_colors = state.get('recent_colors', [])
        
        status = "💰 Período de Apostas" if is_betting else "⏳ Aguardando próximo jogo"
        
        # Formata as últimas cores
        colors_display = ""
        if recent_colors:
            colors_text_parts = []
            for color in recent_colors[:10]:  # Últimas 10 cores
                if color == 'red':
                    colors_text_parts.append("[bold red]🔴[/bold red]")
                elif color == 'black':
                    colors_text_parts.append("[bold white on black]⚫[/bold white on black]")
                elif color == 'white':
                    colors_text_parts.append("[bold]⚪[/bold]")
            
            if colors_text_parts:
                colors_display = f"\n[bold]Últimas Cores:[/bold] {' '.join(colors_text_parts)}"
        
        panel = Panel(
            f"[bold]{status}[/bold]\n"
            f"[dim]Timer: {timer_text}[/dim]"
            f"{colors_display}",
            title="Estado do Jogo",
            border_style="cyan"
        )
        self.console.print(panel)
    
    def clear_screen(self):
        """Limpa a tela"""
        self.console.clear()
    
    def print_separator(self):
        """Imprime um separador"""
        self.console.print("[dim]" + "─" * 60 + "[/dim]")

