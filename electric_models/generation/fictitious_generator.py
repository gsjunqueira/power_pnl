"""
Módulo `fictitious_generator`

Define a classe `FictitiousGenerator`, que representa um gerador fictício utilizado para
balancear o sistema em situações de déficit de geração. Estes geradores são adicionados
automaticamente às barras com carga e permitem viabilizar soluções inviáveis.

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from .base_generator import BaseGenerator

@dataclass(kw_only=True)
class FictitiousGenerator(BaseGenerator):
    """
    Gerador fictício (dummy) para absorver ou injetar potência conforme necessário.

    Estes geradores não correspondem a unidades físicas reais, mas são úteis para:
    - Viabilizar soluções inviáveis em problemas de otimização.
    - Representar déficit de geração com custo elevado.
    - Atuar como unidades de emergência com rampas muito altas.

    Atributos:
        ramp (float): Grande rampa para permitir variações instantâneas.
        cost (float): Custo muito elevado (penalidade para evitar seu uso).
        emission (float): Emissão nula (representação artificial).
        status (bool): Indica se está disponível para uso no modelo.
    """
    ramp: float = 1e5
    cost: float = 1e6
    emission: float = 0.0
    type: str = "dummy"

    def __post_init__(self):
        """Associa automaticamente o gerador fictício à barra."""
        self.bus.add_generator(self)

    def get_power_output(self, period: int) -> float:
        """
        Retorna zero como valor simbólico (definido externamente em simulações).

        Args:
            period (int): Índice do período.

        Returns:
            float: Potência fictícia (MW).
        """
        return 0.0

    def __repr__(self):
        """
        Retorna uma representação resumida do gerador fictício para debug.

        Returns:
            str: String no formato "<FictitiousGenerator id=... bus=...>".
        """
        return f"<FictitiousGenerator id={self.id} bus={self.bus.id}>"
