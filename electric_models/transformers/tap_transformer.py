"""
Módulo `tap_transformer`

Define a classe `TapTransformer`, que representa um transformador com controle de tap
(utilizado para regulação de tensão, sem defasagem angular).

Autor: Giovani Santiago Junqueira
"""

__author__ = "Giovani Santiago Junqueira"

from dataclasses import dataclass
from .transformer import Transformer

@dataclass
class TapTransformer(Transformer):
    """
    Transformador com ajuste de tap para regulação de tensão.

    Atributos herdados da classe base `Transformer`. Neste modelo, o ângulo de fase
    é automaticamente fixado em zero, indicando ausência de defasamento angular.

    Aplicações:
        - Fluxo de potência AC com controle de tensão.
        - FPO com transformadores de tap variável.
    """

    def __post_init__(self):
        """
        Inicializa o transformador com ângulo de defasagem fixado em 0°.

        Também realiza a validação padrão da classe base.
        """
        self.phase = 0.0
        super().__post_init__()

