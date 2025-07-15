"""
Módulo `phase_transformer`

Define a classe `PhaseTransformer`, que representa um transformador defasador (phase shifter).
Este equipamento é utilizado para controle de fluxo de potência ativa via ajuste do ângulo de fase,
sem alterar a magnitude da tensão (tap fixo em 1.0).

Aplicações:
    - Fluxo de potência AC (controle de ângulo)
    - FPO linearizado (Power Transfer Distribution Factors)
    - Modelagem de redes com controle de fluxo

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from .transformer import Transformer

@dataclass
class PhaseTransformer(Transformer):
    """
    Transformador com defasagem angular.

    Este modelo considera tap fixo (1.0) e permite ajustar o ângulo de fase (`phase`),
    sendo utilizado principalmente para controle de fluxo de potência ativa em sistemas AC.

    Atributos herdados da classe base `Transformer`.
    """
    def __post_init__(self):
        """
        Inicializa o transformador com tap fixo em 1.0 e executa validações.

        Também registra o transformador nas barras `from_bus` e `to_bus` e verifica coerência
        dos parâmetros elétricos e de confiabilidade.
        """
        self.tap = 1.0
        super().__post_init__()
