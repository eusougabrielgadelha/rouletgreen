"""
Módulo de gerenciamento de banco de dados
"""
import sqlite3
from datetime import datetime
from typing import List, Dict, Optional
import json


def get_timestamp() -> str:
    """Retorna timestamp formatado com data, hora, minuto, segundo e microssegundos"""
    return datetime.now().strftime('%Y-%m-%d %H:%M:%S.%f')


class Database:
    def __init__(self, db_path: str = "blaze_data.db"):
        self.db_path = db_path
        self.init_database()
    
    def get_connection(self):
        return sqlite3.connect(self.db_path)
    
    def init_database(self):
        """Inicializa o banco de dados criando as tabelas necessárias"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Tabela de jogos
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS games (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT UNIQUE,
                color TEXT NOT NULL,
                number INTEGER,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                result TEXT
            )
        ''')
        
        # Tabela de apostas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS bets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                game_id TEXT,
                predicted_color TEXT NOT NULL,
                actual_color TEXT,
                bet_amount REAL,
                confidence REAL,
                result TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (game_id) REFERENCES games(game_id)
            )
        ''')
        
        # Tabela de padrões identificados
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patterns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                pattern_type TEXT NOT NULL,
                pattern_data TEXT,
                success_rate REAL,
                occurrences INTEGER DEFAULT 0,
                last_seen DATETIME,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de estatísticas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS statistics (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                total_games INTEGER DEFAULT 0,
                total_bets INTEGER DEFAULT 0,
                wins INTEGER DEFAULT 0,
                losses INTEGER DEFAULT 0,
                win_rate REAL DEFAULT 0.0,
                total_profit REAL DEFAULT 0.0,
                last_updated DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Tabela de sequências coletadas (amostragens)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sequences (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sequence_length INTEGER NOT NULL,
                sequence_data TEXT NOT NULL,
                sequence_colors TEXT NOT NULL,
                sequence_numbers TEXT,
                timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                UNIQUE(sequence_length, sequence_data)
            )
        ''')
        
        # Índices para consultas rápidas
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sequence_length ON sequences(sequence_length)')
        cursor.execute('CREATE INDEX IF NOT EXISTS idx_sequence_timestamp ON sequences(timestamp)')
        
        conn.commit()
        conn.close()
    
    def save_game(self, game_id: str, color: str, number: Optional[int] = None):
        """Salva um jogo no banco de dados (evita duplicação)"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Verifica se já existe um jogo com mesma cor e número recentemente
            cursor.execute('''
                SELECT game_id FROM games 
                WHERE color = ? AND number = ? 
                ORDER BY timestamp DESC 
                LIMIT 1
            ''', (color, number))
            
            existing = cursor.fetchone()
            
            # Se não existe ou é diferente, insere
            if not existing:
                cursor.execute('''
                    INSERT OR IGNORE INTO games (game_id, color, number, timestamp)
                    VALUES (?, ?, ?, ?)
                ''', (game_id, color, number, get_timestamp()))
                conn.commit()
            else:
                # Jogo já existe, apenas atualiza timestamp se necessário
                existing_id = existing[0]
                if existing_id != game_id:
                    cursor.execute('''
                        UPDATE games 
                        SET timestamp = ?
                        WHERE game_id = ?
                    ''', (get_timestamp(), existing_id))
                    conn.commit()
        except sqlite3.IntegrityError:
            # Jogo já existe com mesmo ID, apenas atualiza
            cursor.execute('''
                UPDATE games 
                SET color = ?, number = ?, timestamp = ?
                WHERE game_id = ?
            ''', (color, number, get_timestamp(), game_id))
            conn.commit()
        except Exception as e:
            # Em caso de erro, apenas ignora para não bloquear
            pass
        finally:
            conn.close()
    
    def save_bet(self, game_id: str, predicted_color: str, bet_amount: float, 
                 confidence: float, actual_color: Optional[str] = None, 
                 result: Optional[str] = None):
        """Salva uma aposta no banco de dados"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO bets (game_id, predicted_color, actual_color, 
                            bet_amount, confidence, result, timestamp)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        ''', (game_id, predicted_color, actual_color, bet_amount, 
              confidence, result, get_timestamp()))
        
        conn.commit()
        conn.close()
        self.update_statistics()
    
    def update_bet_result(self, game_id: str, actual_color: str, result: str):
        """Atualiza o resultado de uma aposta"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            UPDATE bets 
            SET actual_color = ?, result = ?
            WHERE game_id = ?
        ''', (actual_color, result, game_id))
        
        conn.commit()
        conn.close()
        self.update_statistics()
    
    def get_recent_games(self, limit: int = 50) -> List[Dict]:
        """Retorna os jogos mais recentes"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT game_id, color, number, timestamp, result
            FROM games
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        games = []
        for row in cursor.fetchall():
            games.append({
                'game_id': row[0],
                'color': row[1],
                'number': row[2],
                'timestamp': row[3],
                'result': row[4]
            })
        
        conn.close()
        return games
    
    def get_game_history_colors(self, limit: int = 50) -> List[str]:
        """Retorna apenas as cores dos jogos mais recentes"""
        games = self.get_recent_games(limit)
        return [game['color'] for game in games]
    
    def save_pattern(self, pattern_type: str, pattern_data: Dict, 
                    success_rate: float, occurrences: int = 1):
        """Salva um padrão identificado"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        pattern_json = json.dumps(pattern_data)
        
        cursor.execute('''
            INSERT INTO patterns (pattern_type, pattern_data, success_rate, 
                               occurrences, last_seen)
            VALUES (?, ?, ?, ?, ?)
        ''', (pattern_type, pattern_json, success_rate, occurrences, get_timestamp()))
        
        conn.commit()
        conn.close()
    
    def get_statistics(self) -> Dict:
        """Retorna as estatísticas gerais"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('SELECT * FROM statistics ORDER BY last_updated DESC LIMIT 1')
        row = cursor.fetchone()
        
        if row:
            return {
                'total_games': row[1],
                'total_bets': row[2],
                'wins': row[3],
                'losses': row[4],
                'win_rate': row[5],
                'total_profit': row[6]
            }
        
        conn.close()
        return {
            'total_games': 0,
            'total_bets': 0,
            'wins': 0,
            'losses': 0,
            'win_rate': 0.0,
            'total_profit': 0.0
        }
    
    def update_statistics(self):
        """Atualiza as estatísticas gerais"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Conta jogos
        cursor.execute('SELECT COUNT(*) FROM games')
        total_games = cursor.fetchone()[0]
        
        # Conta apostas
        cursor.execute('SELECT COUNT(*) FROM bets')
        total_bets = cursor.fetchone()[0]
        
        # Conta vitórias e derrotas
        cursor.execute('SELECT COUNT(*) FROM bets WHERE result = "WIN"')
        wins = cursor.fetchone()[0]
        
        cursor.execute('SELECT COUNT(*) FROM bets WHERE result = "LOSS"')
        losses = cursor.fetchone()[0]
        
        # Calcula taxa de acerto
        win_rate = (wins / total_bets * 100) if total_bets > 0 else 0.0
        
        # Calcula lucro (simplificado - assume que cada vitória paga 2x o valor apostado)
        cursor.execute('''
            SELECT SUM(bet_amount * 2) FROM bets WHERE result = "WIN"
        ''')
        total_winnings = cursor.fetchone()[0] or 0.0
        
        cursor.execute('SELECT SUM(bet_amount) FROM bets')
        total_bet_amount = cursor.fetchone()[0] or 0.0
        
        total_profit = total_winnings - total_bet_amount
        
        # Atualiza ou insere estatísticas
        cursor.execute('''
            INSERT OR REPLACE INTO statistics 
            (id, total_games, total_bets, wins, losses, win_rate, total_profit, last_updated)
            VALUES (1, ?, ?, ?, ?, ?, ?, ?)
        ''', (total_games, total_bets, wins, losses, win_rate, total_profit, get_timestamp()))
        
        conn.commit()
        conn.close()
    
    def save_sequence(self, sequence_length: int, sequence_data: List[Dict]):
        """Salva uma sequência de jogos para análise"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Extrai cores e números da sequência
            colors = [s.get('color', '') for s in sequence_data]
            numbers = [str(s.get('number', '')) if s.get('number') is not None else '' for s in sequence_data]
            
            # Cria representação da sequência
            colors_str = ','.join(colors)
            numbers_str = ','.join(numbers) if any(numbers) else None
            sequence_str = ','.join([f"{c}:{n}" if n else c for c, n in zip(colors, numbers)])
            
            # Insere ou ignora se já existe (evita duplicação)
            cursor.execute('''
                INSERT OR IGNORE INTO sequences 
                (sequence_length, sequence_data, sequence_colors, sequence_numbers, timestamp)
                VALUES (?, ?, ?, ?, ?)
            ''', (sequence_length, sequence_str, colors_str, numbers_str, get_timestamp()))
            
            conn.commit()
        except Exception as e:
            # Em caso de erro, apenas ignora para não bloquear
            pass
        finally:
            conn.close()
    
    def get_sequences_by_length(self, length: int, limit: int = 100) -> List[Dict]:
        """Retorna sequências de um tamanho específico"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sequence_data, sequence_colors, sequence_numbers, timestamp
            FROM sequences
            WHERE sequence_length = ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (length, limit))
        
        sequences = []
        for row in cursor.fetchall():
            sequence_data, colors_str, numbers_str, timestamp = row
            colors = colors_str.split(',') if colors_str else []
            numbers = numbers_str.split(',') if numbers_str else []
            
            # Reconstroi a sequência
            seq = []
            for i, color in enumerate(colors):
                number = int(numbers[i]) if i < len(numbers) and numbers[i] and numbers[i].isdigit() else None
                seq.append({'color': color, 'number': number})
            
            sequences.append({
                'sequence': seq,
                'length': length,
                'timestamp': timestamp
            })
        
        conn.close()
        return sequences
    
    def get_all_sequences(self, limit: int = 500) -> List[Dict]:
        """Retorna todas as sequências coletadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT sequence_length, sequence_data, sequence_colors, sequence_numbers, timestamp
            FROM sequences
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (limit,))
        
        sequences = []
        for row in cursor.fetchall():
            length, sequence_data, colors_str, numbers_str, timestamp = row
            colors = colors_str.split(',') if colors_str else []
            numbers = numbers_str.split(',') if numbers_str else []
            
            seq = []
            for i, color in enumerate(colors):
                number = int(numbers[i]) if i < len(numbers) and numbers[i] and numbers[i].isdigit() else None
                seq.append({'color': color, 'number': number})
            
            sequences.append({
                'sequence': seq,
                'length': length,
                'timestamp': timestamp
            })
        
        conn.close()
        return sequences
    
    def get_sequence_statistics(self) -> Dict:
        """Retorna estatísticas sobre sequências coletadas"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Total de sequências por tamanho
        cursor.execute('''
            SELECT sequence_length, COUNT(*) as count
            FROM sequences
            GROUP BY sequence_length
            ORDER BY sequence_length
        ''')
        
        stats_by_length = {}
        for row in cursor.fetchall():
            length, count = row
            stats_by_length[length] = count
        
        # Total geral
        cursor.execute('SELECT COUNT(*) FROM sequences')
        total = cursor.fetchone()[0]
        
        conn.close()
        
        return {
            'total_sequences': total,
            'by_length': stats_by_length
        }

