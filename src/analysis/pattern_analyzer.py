"""
Módulo de análise de padrões e previsão
"""
from typing import List, Dict, Optional, Tuple
from collections import Counter
import statistics
import sys
import os

# Adiciona o diretório raiz ao path
root_dir = os.path.join(os.path.dirname(__file__), '..', '..')
sys.path.insert(0, os.path.abspath(root_dir))
from src.database.database import Database


class PatternAnalyzer:
    def __init__(self, db: Database):
        self.db = db
    
    def analyze_sequences_collection(self, sequence_length: int = None) -> Dict:
        """Analisa as sequências coletadas para identificar padrões recorrentes"""
        try:
            # Obtém sequências do banco
            if sequence_length:
                sequences = self.db.get_sequences_by_length(sequence_length, limit=200)
            else:
                # Analisa todas as sequências
                sequences = self.db.get_all_sequences(limit=500)
            
            if not sequences:
                return {'patterns_found': 0, 'common_patterns': []}
            
            # Agrupa sequências por padrão
            pattern_counts = Counter()
            pattern_results = {}
            
            for seq_data in sequences:
                seq = seq_data['sequence']
                colors = [s.get('color') for s in seq]
                pattern_str = ''.join(colors)
                
                pattern_counts[pattern_str] += 1
                
                if pattern_str not in pattern_results:
                    pattern_results[pattern_str] = {
                        'pattern': pattern_str,
                        'length': len(seq),
                        'count': 0,
                        'next_colors': []
                    }
                
                pattern_results[pattern_str]['count'] += 1
            
            # Identifica padrões mais comuns
            common_patterns = []
            for pattern_str, count in pattern_counts.most_common(10):
                if count >= 2:  # Padrão aparece pelo menos 2 vezes
                    pattern_info = pattern_results[pattern_str]
                    
                    # Analisa qual cor aparece após esse padrão
                    next_color_counts = Counter()
                    for seq_data in sequences:
                        seq = seq_data['sequence']
                        colors = [s.get('color') for s in seq]
                        if ''.join(colors) == pattern_str:
                            # Procura em outras sequências o que vem depois
                            # (precisa buscar no histórico completo)
                            pass
                    
                    common_patterns.append({
                        'pattern': pattern_str,
                        'length': pattern_info['length'],
                        'occurrences': count,
                        'frequency': count / len(sequences) * 100
                    })
            
            return {
                'patterns_found': len(common_patterns),
                'total_sequences': len(sequences),
                'common_patterns': common_patterns
            }
        except Exception as e:
            return {'patterns_found': 0, 'common_patterns': [], 'error': str(e)}
    
    def analyze_history(self, history: List[str], lookback: int = 10, numbers: List[int] = None) -> Dict:
        """Analisa o histórico e identifica padrões (cores e números)"""
        if len(history) < 3:
            return {'confidence': 0.0, 'prediction': None, 'patterns': []}
        
        patterns = []
        confidence = 0.0
        prediction = None
        
        # Análise 1: Sequências de cores
        seq_pattern = self._analyze_sequences(history, lookback)
        if seq_pattern:
            patterns.append(seq_pattern)
            confidence += seq_pattern.get('confidence', 0) * 0.25
            if not prediction and seq_pattern.get('prediction'):
                prediction = seq_pattern['prediction']
        
        # Análise 2: Frequência de cores
        freq_pattern = self._analyze_frequency(history, lookback)
        if freq_pattern:
            patterns.append(freq_pattern)
            confidence += freq_pattern.get('confidence', 0) * 0.25
            if not prediction and freq_pattern.get('prediction'):
                prediction = freq_pattern['prediction']
        
        # Análise 3: Padrões alternados
        alt_pattern = self._analyze_alternating(history, lookback)
        if alt_pattern:
            patterns.append(alt_pattern)
            confidence += alt_pattern.get('confidence', 0) * 0.20
            if not prediction and alt_pattern.get('prediction'):
                prediction = alt_pattern['prediction']
        
        # Análise 4: Tendências (últimas N jogadas)
        trend_pattern = self._analyze_trend(history, min(5, len(history)))
        if trend_pattern:
            patterns.append(trend_pattern)
            confidence += trend_pattern.get('confidence', 0) * 0.20
            if not prediction and trend_pattern.get('prediction'):
                prediction = trend_pattern['prediction']
        
        # Análise 5: Padrões de números (se disponível)
        if numbers and len(numbers) >= 3:
            number_pattern = self._analyze_number_patterns(numbers, history, lookback)
            if number_pattern:
                patterns.append(number_pattern)
                confidence += number_pattern.get('confidence', 0) * 0.10
                if not prediction and number_pattern.get('prediction'):
                    prediction = number_pattern['prediction']
        
        # Normaliza a confiança
        confidence = min(confidence, 1.0)
        
        return {
            'confidence': confidence,
            'prediction': prediction,
            'patterns': patterns
        }
    
    def _analyze_number_patterns(self, numbers: List[int], colors: List[str], lookback: int) -> Optional[Dict]:
        """Analisa padrões relacionados a números"""
        if len(numbers) < 3 or len(colors) < 3:
            return None
        
        recent_numbers = numbers[:min(lookback, len(numbers))]
        recent_colors = colors[:min(lookback, len(colors))]
        
        # Analisa se há números que tendem a aparecer com certas cores
        number_color_map = {}
        for i, num in enumerate(recent_numbers):
            if i < len(recent_colors):
                color = recent_colors[i]
                if num not in number_color_map:
                    number_color_map[num] = []
                number_color_map[num].append(color)
        
        # Verifica se algum número aparece frequentemente com uma cor específica
        for num, num_colors in number_color_map.items():
            if len(num_colors) >= 2:
                color_counts = Counter(num_colors)
                most_common_color, count = color_counts.most_common(1)[0]
                
                # Se um número aparece 2+ vezes com a mesma cor, pode ser um padrão
                if count >= 2 and count / len(num_colors) >= 0.7:
                    # Se o número mais recente foi este, prevê a cor associada
                    if recent_numbers[0] == num:
                        return {
                            'type': 'number_color_association',
                            'pattern': f"Número {num} tende a aparecer com {most_common_color}",
                            'prediction': most_common_color,
                            'confidence': 0.55
                        }
        
        return None
    
    def _analyze_sequences(self, history: List[str], lookback: int) -> Optional[Dict]:
        """Analisa sequências repetidas"""
        if len(history) < 3:
            return None
        
        recent = history[:lookback]
        
        # Procura por sequências de 2 ou mais cores iguais
        for i in range(len(recent) - 1):
            if recent[i] == recent[i+1]:
                # Verifica se há padrão de repetição
                if i + 2 < len(recent) and recent[i+1] != recent[i+2]:
                    # Padrão: AA B (duas iguais seguidas de uma diferente)
                    # Previsão: pode continuar com a cor diferente ou voltar à anterior
                    next_color = recent[i+2]
                    confidence = 0.6
                    return {
                        'type': 'sequence_break',
                        'pattern': f"{recent[i]}{recent[i+1]}{recent[i+2]}",
                        'prediction': next_color,
                        'confidence': confidence
                    }
        
        return None
    
    def _analyze_frequency(self, history: List[str], lookback: int) -> Optional[Dict]:
        """Analisa frequência de cores"""
        if len(history) < 3:
            return None
        
        recent = history[:lookback]
        color_counts = Counter(recent)
        total = len(recent)
        
        # Calcula probabilidades
        probabilities = {color: count / total for color, count in color_counts.items()}
        
        # Identifica a cor menos frequente (pode estar "atrasada")
        min_color = min(probabilities, key=probabilities.get)
        min_prob = probabilities[min_color]
        
        # Se uma cor está muito menos frequente, pode ser uma boa aposta
        if min_prob < 0.25 and total >= 5:
            confidence = 0.7 - min_prob
            return {
                'type': 'frequency_imbalance',
                'pattern': f"{min_color} está {min_prob*100:.1f}% frequente",
                'prediction': min_color,
                'confidence': confidence
            }
        
        return None
    
    def _analyze_alternating(self, history: List[str], lookback: int) -> Optional[Dict]:
        """Analisa padrões alternados"""
        if len(history) < 4:
            return None
        
        recent = history[:lookback]
        
        # Verifica padrão alternado (ABAB ou ABABAB)
        is_alternating = True
        for i in range(len(recent) - 2):
            if recent[i] == recent[i+2]:
                continue
            else:
                is_alternating = False
                break
        
        if is_alternating and len(recent) >= 4:
            # Padrão alternado detectado
            next_color = recent[0]  # A cor que deve vir (baseada no padrão)
            confidence = 0.65
            return {
                'type': 'alternating',
                'pattern': f"Alternado: {recent[0]}{recent[1]}...",
                'prediction': next_color,
                'confidence': confidence
            }
        
        return None
    
    def _analyze_trend(self, history: List[str], lookback: int) -> Optional[Dict]:
        """Analisa tendência recente"""
        if len(history) < 3:
            return None
        
        recent = history[:lookback]
        
        # Verifica qual cor apareceu mais nas últimas jogadas
        color_counts = Counter(recent)
        
        if len(color_counts) == 1:
            # Todas as últimas jogadas foram da mesma cor
            # Pode indicar que vai mudar
            dominant_color = color_counts.most_common(1)[0][0]
            other_colors = ['red', 'black', 'white']
            other_colors.remove(dominant_color)
            
            # Previsão: uma das outras cores (aleatório, mas tendendo para a menos frequente no histórico maior)
            if len(history) > lookback:
                full_counts = Counter(history)
                prediction = min(other_colors, key=lambda c: full_counts.get(c, 0))
            else:
                prediction = other_colors[0]
            
            confidence = 0.6
            return {
                'type': 'trend_reversal',
                'pattern': f"Muitas {dominant_color} seguidas, possível reversão",
                'prediction': prediction,
                'confidence': confidence
            }
        
        # Verifica se há uma cor dominante recente
        most_common = color_counts.most_common(1)[0]
        if most_common[1] / len(recent) >= 0.6:
            # Uma cor dominou recentemente
            confidence = 0.55
            return {
                'type': 'recent_dominance',
                'pattern': f"{most_common[0]} dominou recentemente ({most_common[1]}/{len(recent)})",
                'prediction': most_common[0],
                'confidence': confidence
            }
        
        return None
    
    def validate_signal(self, prediction: str, confidence: float, min_confidence: float = 0.6) -> bool:
        """Valida se um sinal é válido para apostar"""
        if not prediction:
            return False
        
        if confidence < min_confidence:
            return False
        
        # Verifica se a cor é válida
        if prediction not in ['red', 'black', 'white']:
            return False
        
        return True
    
    def get_prediction(self, history: List[str], min_confidence: float = 0.6, numbers: List[int] = None) -> Optional[Tuple[str, float, Dict]]:
        """Obtém uma previsão baseada no histórico (cores e números)"""
        if len(history) < 3:
            return None
        
        analysis = self.analyze_history(history, numbers=numbers)
        
        if not analysis['prediction']:
            return None
        
        if analysis['confidence'] < min_confidence:
            return None
        
        return (
            analysis['prediction'],
            analysis['confidence'],
            analysis['patterns']
        )

