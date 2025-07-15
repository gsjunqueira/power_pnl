"""
Módulo `transformer_factory`

Fábrica de transformadores que infere o tipo apropriado com base nos dados.

A lógica utiliza os valores de tap e phase para identificar se o transformador
é do tipo básico, com controle de tensão (tap), com defasagem (phase) ou com ambos (dual).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from .tap_transformer import TapTransformer
from .phase_transformer import PhaseTransformer
from .dual_transformer import DualTransformer
from .transformer import Transformer


def create_transformer(data: dict):
    """
    Cria dinamicamente o tipo de transformador adequado com base nos dados fornecidos.

    Regras de inferência:
        - DualTransformer se tap ≠ 1.0 e phase ≠ 0.0
        - TapTransformer se apenas tap ≠ 1.0
        - PhaseTransformer se apenas phase ≠ 0.0
        - Transformer (simples) se tap == 1.0 e phase == 0.0

    Args:
        data (dict): Dicionário contendo os atributos do transformador.
            Deve conter pelo menos:
                - id (str)
                - from_bus (Bus)
                - to_bus (Bus)
                - r (float)
                - x (float)
                - tap (float, opcional, default = 1.0)
                - phase (float, opcional, default = 0.0)

    Returns:
        Transformer | TapTransformer | PhaseTransformer | DualTransformer
            Instância do transformador apropriado para os dados fornecidos.

    Raises:
        TypeError: Se `data` não for um dicionário.
        KeyError: Se campos obrigatórios estiverem ausentes.
    """
    if not isinstance(data, dict):
        raise TypeError("Esperado um dicionário de dados para o transformador.")

    required = {"id", "from_bus", "to_bus", "r", "x"}
    missing = required - set(data)
    if missing:
        raise KeyError(f"Campos obrigatórios ausentes: {missing}")

    tap = data.get("tap", 1.0)
    phase = data.get("phase", 0.0)

    if tap != 1.0 and phase != 0.0:
        return DualTransformer(data)
    elif tap != 1.0:
        return TapTransformer(**data)
    elif phase != 0.0:
        return PhaseTransformer(**data)
    else:
        return Transformer(**data)
