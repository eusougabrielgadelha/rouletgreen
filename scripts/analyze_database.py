"""
Script para análise completa do banco de dados
"""
import sys
import os

# Adiciona o diretório raiz ao path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

# Configura encoding UTF-8 para Windows
from src.utils.encoding import setup_encoding
setup_encoding()

from src.database import Database
from src.analysis import PatternAnalyzer
from collections import Counter
from datetime import datetime, timedelta
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich import box
from config import config

console = Console()

def analyze_database():
    """Realiza análise completa do banco de dados"""
    db = Database(config.DATABASE_PATH)
    
    console.print("\n[bold cyan]📊 ANÁLISE DO BANCO DE DADOS BLAZE DOUBLE[/bold cyan]\n")
    
    # 1. Estatísticas Gerais
    show_general_stats(db)
    
    # 2. Distribuição de Cores
    show_color_distribution(db)
    
    # 3. Análise de Números
    show_number_analysis(db)
    
    # 4. Histórico de Apostas
    show_bets_history(db)
    
    # 5. Análise de Padrões
    show_patterns_analysis(db)
    
    # 6. Taxa de Acerto por Cor
    show_accuracy_by_color(db)
    
    # 7. Análise Temporal
    show_temporal_analysis(db)
    
    # 8. Últimos Jogos
    show_recent_games(db)
    
    # 9. Análise de Sequências Coletadas
    show_sequences_analysis(db)
    
    console.print("\n[bold green]✅ Análise concluída![/bold green]\n")

def show_general_stats(db):
    """Mostra estatísticas gerais"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Total de jogos
    cursor.execute('SELECT COUNT(*) FROM games')
    total_games = cursor.fetchone()[0]
    
    # Total de apostas
    cursor.execute('SELECT COUNT(*) FROM bets')
    total_bets = cursor.fetchone()[0]
    
    # Vitórias e derrotas
    cursor.execute('SELECT COUNT(*) FROM bets WHERE result = "WIN"')
    wins = cursor.fetchone()[0]
    
    cursor.execute('SELECT COUNT(*) FROM bets WHERE result = "LOSS"')
    losses = cursor.fetchone()[0]
    
    # Taxa de acerto
    win_rate = (wins / total_bets * 100) if total_bets > 0 else 0.0
    
    # Lucro
    cursor.execute('SELECT SUM(bet_amount * 2) FROM bets WHERE result = "WIN"')
    total_winnings = cursor.fetchone()[0] or 0.0
    
    cursor.execute('SELECT SUM(bet_amount) FROM bets')
    total_bet_amount = cursor.fetchone()[0] or 0.0
    
    total_profit = total_winnings - total_bet_amount
    
    # Primeiro e último jogo
    cursor.execute('SELECT MIN(timestamp), MAX(timestamp) FROM games')
    first_last = cursor.fetchone()
    first_game = first_last[0] if first_last[0] else "N/A"
    last_game = first_last[1] if first_last[1] else "N/A"
    
    conn.close()
    
    table = Table(title="📈 Estatísticas Gerais", box=box.ROUNDED)
    table.add_column("Métrica", style="cyan", width=30)
    table.add_column("Valor", style="yellow", width=20)
    
    table.add_row("Total de Jogos Coletados", str(total_games))
    table.add_row("Total de Apostas Realizadas", str(total_bets))
    table.add_row("Vitórias", f"[green]{wins}[/green]")
    table.add_row("Derrotas", f"[red]{losses}[/red]")
    table.add_row("Taxa de Acerto", f"{win_rate:.2f}%")
    table.add_row("Total Apostado", f"R$ {total_bet_amount:.2f}")
    table.add_row("Total Ganho", f"R$ {total_winnings:.2f}")
    table.add_row("Lucro Total", f"[{'green' if total_profit >= 0 else 'red'}]R$ {total_profit:.2f}[/{'green' if total_profit >= 0 else 'red'}]")
    table.add_row("Primeiro Jogo", str(first_game))
    table.add_row("Último Jogo", str(last_game))
    
    console.print(table)
    console.print()

def show_color_distribution(db):
    """Mostra distribuição de cores"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT color, COUNT(*) as count 
        FROM games 
        GROUP BY color 
        ORDER BY count DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        console.print("[yellow]Nenhum jogo encontrado no banco de dados[/yellow]\n")
        return
    
    total = sum(r[1] for r in results)
    
    table = Table(title="🎨 Distribuição de Cores", box=box.ROUNDED)
    table.add_column("Cor", style="bold", width=15)
    table.add_column("Quantidade", style="yellow", width=15, justify="right")
    table.add_column("Percentual", style="green", width=15, justify="right")
    
    color_names = {
        'red': '[bold red]🔴 Vermelho[/bold red]',
        'black': '[bold]⚫ Preto[/bold]',
        'white': '[bold]⚪ Branco[/bold]'
    }
    
    for color, count in results:
        percentage = (count / total * 100) if total > 0 else 0
        color_display = color_names.get(color, color)
        table.add_row(color_display, str(count), f"{percentage:.2f}%")
    
    console.print(table)
    console.print()

def show_number_analysis(db):
    """Mostra análise de números"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT number, COUNT(*) as count 
        FROM games 
        WHERE number IS NOT NULL
        GROUP BY number 
        ORDER BY count DESC
        LIMIT 10
    ''')
    
    results = cursor.fetchall()
    
    if results:
        cursor.execute('SELECT AVG(number), MIN(number), MAX(number) FROM games WHERE number IS NOT NULL')
        stats = cursor.fetchone()
        
        conn.close()
        
        table = Table(title="🔢 Análise de Números (Top 10 mais frequentes)", box=box.ROUNDED)
        table.add_column("Número", style="cyan", width=10, justify="center")
        table.add_column("Frequência", style="yellow", width=15, justify="right")
        
        for number, count in results:
            table.add_row(str(number), str(count))
        
        console.print(table)
        
        if stats[0]:
            panel = Panel(
                f"[bold]Média:[/bold] {stats[0]:.2f}\n"
                f"[bold]Mínimo:[/bold] {stats[1]}\n"
                f"[bold]Máximo:[/bold] {stats[2]}",
                title="📊 Estatísticas de Números",
                border_style="cyan"
            )
            console.print(panel)
    else:
        conn.close()
        console.print("[yellow]Nenhum número encontrado no banco de dados[/yellow]\n")
    
    console.print()

def show_bets_history(db):
    """Mostra histórico de apostas"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT predicted_color, actual_color, result, confidence, bet_amount, timestamp
        FROM bets
        ORDER BY timestamp DESC
        LIMIT 20
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        console.print("[yellow]Nenhuma aposta encontrada no banco de dados[/yellow]\n")
        return
    
    table = Table(title="💰 Histórico de Apostas (Últimas 20)", box=box.ROUNDED)
    table.add_column("Data/Hora", style="dim", width=20)
    table.add_column("Previsão", style="cyan", width=12)
    table.add_column("Resultado", style="yellow", width=12)
    table.add_column("Confiança", style="magenta", width=12)
    table.add_column("Valor", style="green", width=10)
    table.add_column("Status", style="bold", width=10)
    
    color_names = {
        'red': '🔴 Vermelho',
        'black': '⚫ Preto',
        'white': '⚪ Branco'
    }
    
    for row in results:
        predicted, actual, result, confidence, amount, timestamp = row
        predicted_display = color_names.get(predicted, predicted)
        actual_display = color_names.get(actual, actual) if actual else "N/A"
        result_display = f"[green]WIN[/green]" if result == "WIN" else f"[red]LOSS[/red]"
        
        table.add_row(
            str(timestamp),
            predicted_display,
            actual_display,
            f"{confidence*100:.1f}%",
            f"R$ {amount:.2f}",
            result_display
        )
    
    console.print(table)
    console.print()

def show_patterns_analysis(db):
    """Mostra análise de padrões"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT pattern_type, COUNT(*) as count, AVG(success_rate) as avg_success
        FROM patterns
        GROUP BY pattern_type
        ORDER BY count DESC
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        console.print("[yellow]Nenhum padrão identificado ainda[/yellow]\n")
        return
    
    table = Table(title="🔍 Padrões Identificados", box=box.ROUNDED)
    table.add_column("Tipo de Padrão", style="cyan", width=30)
    table.add_column("Ocorrências", style="yellow", width=15, justify="right")
    table.add_column("Taxa de Sucesso", style="green", width=15, justify="right")
    
    for pattern_type, count, avg_success in results:
        success_display = f"{avg_success*100:.2f}%" if avg_success else "N/A"
        table.add_row(pattern_type, str(count), success_display)
    
    console.print(table)
    console.print()

def show_accuracy_by_color(db):
    """Mostra taxa de acerto por cor prevista"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 
            predicted_color,
            COUNT(*) as total,
            SUM(CASE WHEN result = 'WIN' THEN 1 ELSE 0 END) as wins,
            AVG(confidence) as avg_confidence
        FROM bets
        WHERE result IS NOT NULL
        GROUP BY predicted_color
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        console.print("[yellow]Dados insuficientes para análise por cor[/yellow]\n")
        return
    
    table = Table(title="🎯 Taxa de Acerto por Cor", box=box.ROUNDED)
    table.add_column("Cor Prevista", style="bold", width=15)
    table.add_column("Total", style="yellow", width=10, justify="right")
    table.add_column("Vitórias", style="green", width=10, justify="right")
    table.add_column("Derrotas", style="red", width=10, justify="right")
    table.add_column("Taxa de Acerto", style="cyan", width=15, justify="right")
    table.add_column("Conf. Média", style="magenta", width=15, justify="right")
    
    color_names = {
        'red': '[bold red]🔴 Vermelho[/bold red]',
        'black': '[bold]⚫ Preto[/bold]',
        'white': '[bold]⚪ Branco[/bold]'
    }
    
    for predicted, total, wins, avg_conf in results:
        losses = total - wins
        win_rate = (wins / total * 100) if total > 0 else 0
        color_display = color_names.get(predicted, predicted)
        avg_conf_display = f"{avg_conf*100:.1f}%" if avg_conf else "N/A"
        
        table.add_row(
            color_display,
            str(total),
            str(wins),
            str(losses),
            f"{win_rate:.2f}%",
            avg_conf_display
        )
    
    console.print(table)
    console.print()

def show_temporal_analysis(db):
    """Mostra análise temporal"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    # Jogos por hora do dia
    cursor.execute('''
        SELECT 
            strftime('%H', timestamp) as hour,
            COUNT(*) as count
        FROM games
        GROUP BY hour
        ORDER BY hour
    ''')
    
    hourly = cursor.fetchall()
    
    if hourly:
        table = Table(title="⏰ Distribuição de Jogos por Hora", box=box.ROUNDED)
        table.add_column("Hora", style="cyan", width=10, justify="center")
        table.add_column("Quantidade", style="yellow", width=15, justify="right")
        
        for hour, count in hourly:
            table.add_row(f"{hour}:00", str(count))
        
        console.print(table)
        console.print()
    
    conn.close()

def show_recent_games(db):
    """Mostra os últimos jogos"""
    conn = db.get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT color, number, timestamp
        FROM games
        ORDER BY timestamp DESC
        LIMIT 30
    ''')
    
    results = cursor.fetchall()
    conn.close()
    
    if not results:
        console.print("[yellow]Nenhum jogo encontrado[/yellow]\n")
        return
    
    table = Table(title="🎲 Últimos 30 Jogos", box=box.ROUNDED)
    table.add_column("Pos", style="cyan", width=5, justify="center")
    table.add_column("Cor", style="bold", width=15)
    table.add_column("Número", style="yellow", width=10, justify="center")
    table.add_column("Data/Hora", style="dim", width=20)
    
    color_names = {
        'red': '[bold red]🔴 VERMELHO[/bold red]',
        'black': '[bold white on black]⚫ PRETO[/bold white on black]',
        'white': '[bold]⚪ BRANCO[/bold]'
    }
    
    for i, (color, number, timestamp) in enumerate(results, 1):
        color_display = color_names.get(color, color)
        number_display = str(number) if number is not None else "[dim]N/A[/dim]"
        
        table.add_row(
            str(i),
            color_display,
            number_display,
            str(timestamp)
        )
    
    console.print(table)
    console.print()

def show_sequences_analysis(db):
    """Mostra análise de sequências coletadas"""
    analyzer = PatternAnalyzer(db)
    
    # Estatísticas gerais
    stats = db.get_sequence_statistics()
    
    if stats['total_sequences'] == 0:
        console.print("[yellow]Nenhuma sequência coletada ainda[/yellow]\n")
        return
    
    table = Table(title="📊 Estatísticas de Sequências Coletadas", box=box.ROUNDED)
    table.add_column("Tamanho", style="cyan", width=12, justify="center")
    table.add_column("Quantidade", style="yellow", width=15, justify="right")
    
    for length in sorted(stats['by_length'].keys()):
        count = stats['by_length'][length]
        table.add_row(f"{length} jogos", str(count))
    
    table.add_row("[bold]TOTAL[/bold]", f"[bold]{stats['total_sequences']}[/bold]")
    
    console.print(table)
    console.print()
    
    # Análise de padrões por tamanho
    for length in sorted(stats['by_length'].keys())[:5]:  # Top 5 tamanhos
        analysis = analyzer.analyze_sequences_collection(sequence_length=length)
        
        if analysis.get('patterns_found', 0) > 0:
            panel = Panel(
                f"[bold]Padrões encontrados:[/bold] {analysis['patterns_found']}\n"
                f"[bold]Total de sequências:[/bold] {analysis['total_sequences']}",
                title=f"📈 Análise de Sequências de {length} jogos",
                border_style="cyan"
            )
            console.print(panel)
            
            if analysis.get('common_patterns'):
                table = Table(box=box.SIMPLE)
                table.add_column("Padrão", style="cyan", width=20)
                table.add_column("Ocorrências", style="yellow", width=15)
                table.add_column("Frequência", style="green", width=15)
                
                for pattern_info in analysis['common_patterns'][:5]:
                    pattern_display = ' → '.join([c[0].upper() for c in pattern_info['pattern']])
                    table.add_row(
                        pattern_display,
                        str(pattern_info['occurrences']),
                        f"{pattern_info['frequency']:.1f}%"
                    )
                
                console.print(table)
                console.print()

if __name__ == "__main__":
    try:
        analyze_database()
    except Exception as e:
        console.print(f"[bold red]Erro ao analisar banco de dados: {e}[/bold red]")
        import traceback
        traceback.print_exc()

