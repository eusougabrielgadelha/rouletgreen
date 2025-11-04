"""
Utilitários de mapeamento da roleta Double (Blaze):
- 0 => white
- 1..7 => red
- 8..14 => black

Também provê normalização de resultados extraídos do DOM.
"""

from typing import Optional, List, Dict


def number_to_color(number: Optional[int]) -> Optional[str]:
    if number is None:
        return None
    if number == 0:
        return 'white'
    if 1 <= number <= 7:
        return 'red'
    if 8 <= number <= 14:
        return 'black'
    return None


def color_to_numbers(color: str) -> List[int]:
    c = (color or '').lower()
    if c == 'white':
        return [0]
    if c == 'red':
        return list(range(1, 8))
    if c == 'black':
        return list(range(8, 15))
    return []


def normalize_result(result: Dict) -> Dict:
    """Garante consistência entre número e cor.
    - Se cor = white e número vazio, define número=0
    - Se número está presente e cor vazia, infere cor pelo número
    - Mantém chaves 'color' e 'number'
    """
    color = (result.get('color') or '').lower() if isinstance(result, dict) else ''
    number = result.get('number') if isinstance(result, dict) else None

    if color == 'white' and (number is None):
        number = 0

    if number is not None and (not color):
        color = number_to_color(number) or color

    # Se ambos existem mas conflitam, prioriza o número (fonte mais confiável)
    if number is not None:
        inferred = number_to_color(number)
        if inferred and inferred != color:
            color = inferred

    return {'color': color if color else None, 'number': number}


